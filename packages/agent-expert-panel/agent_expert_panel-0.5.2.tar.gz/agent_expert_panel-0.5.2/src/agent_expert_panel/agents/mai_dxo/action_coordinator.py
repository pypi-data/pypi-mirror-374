"""
MAI-DxO Action Coordinator

Coordinates action decisions among the five MAI-DxO agents to determine
the next action: internet search, ask user, continue discussion, or provide solution.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from ...models.mai_dxo import (
    ActionDecision,
    DecisionContext,
    NextAction,
    SearchResult,
    UserQuestion,
    UserResponse,
    AgentOutput,
    AgentRole,
)
from .base_agent import MAIDxOBaseAgent


class ActionCoordinator:
    """Coordinates action decisions among MAI-DxO agents.

    After agents complete their initial discussion round, this coordinator:
    1. Collects action recommendations from each agent
    2. Determines consensus on the next action
    3. Executes the chosen action (search, ask user, continue discussion, or provide solution)
    4. Manages the flow back to agent discussion if needed
    """

    def __init__(self):
        self.search_results: List[SearchResult] = []
        self.user_questions: List[UserQuestion] = []
        self.user_responses: List[UserResponse] = []
        self.action_history: List[Dict[str, Any]] = []

    async def coordinate_next_action(
        self,
        agents: List["MAIDxOBaseAgent"],
        context: DecisionContext,
        previous_outputs: List[AgentOutput],
        user_input_func: Optional[Callable[[str], str]] = None,
    ) -> Dict[str, Any]:
        """Coordinate the next action decision among agents.

        Args:
            agents: List of all MAI-DxO agents
            context: The decision context
            previous_outputs: All agent outputs from current discussion
            user_input_func: Function to call for user input (if needed)

        Returns:
            Dictionary containing action result and next steps
        """
        print("\n🤖 MAI-DxO Action Coordination Phase")
        print("=" * 50)

        # Step 1: Collect action recommendations from each agent
        action_decisions = []
        for agent in agents:
            print(f"Asking {agent.agent_role.value} for action recommendation...")
            try:
                decision = await agent.decide_next_action(
                    context=context,
                    previous_outputs=previous_outputs,
                    search_results=self.search_results,
                    user_responses=self.user_responses,
                )
                action_decisions.append(decision)
                print(
                    f"  {agent.agent_role.value}: {decision.recommended_action.value}"
                )
                print(f"  Reasoning: {decision.reasoning[:100]}...")
            except Exception as e:
                print(f"  Error getting action from {agent.agent_role.value}: {e}")
                continue

        # Step 2: Determine consensus action
        consensus_action = self._determine_consensus_action(action_decisions)

        print(f"\n🎯 Consensus Action Decided: {consensus_action.value}")

        # Step 3: Execute the chosen action
        action_result = await self._execute_action(
            consensus_action, action_decisions, context, user_input_func
        )

        # Step 4: Log action in history
        self.action_history.append(
            {
                "action": consensus_action.value,
                "decisions": [d.model_dump() for d in action_decisions],
                "result": action_result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "consensus_action": consensus_action,
            "action_decisions": action_decisions,
            "action_result": action_result,
            "should_continue": consensus_action != NextAction.PROVIDE_SOLUTION,
        }

    def _determine_consensus_action(
        self, decisions: List[ActionDecision]
    ) -> NextAction:
        """Determine consensus action from agent recommendations.

        Uses weighted voting based on agent confidence and priority levels.
        """
        if not decisions:
            return NextAction.CONTINUE_DISCUSSION

        # Count votes with confidence weighting
        weighted_votes = {}
        for decision in decisions:
            action = decision.recommended_action
            weight = decision.confidence * (decision.priority_level / 5.0)

            if action not in weighted_votes:
                weighted_votes[action] = 0
            weighted_votes[action] += weight

        # Find action with highest weighted vote
        consensus_action = max(weighted_votes.keys(), key=lambda x: weighted_votes[x])

        print("\n📊 Action Voting Results:")
        for action, weight in sorted(
            weighted_votes.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {action.value}: {weight:.2f} weighted votes")

        return consensus_action

    async def _execute_action(
        self,
        action: NextAction,
        decisions: List[ActionDecision],
        context: DecisionContext,
        user_input_func: Optional[Callable[[str], str]] = None,
    ) -> Dict[str, Any]:
        """Execute the chosen action and return results.

        Args:
            action: The action to execute
            decisions: All agent action decisions for context
            context: Decision context
            user_input_func: Function for user input

        Returns:
            Dictionary with action execution results
        """
        print(f"\n🔄 Executing Action: {action.value}")
        print("-" * 40)

        if action == NextAction.INTERNET_SEARCH:
            return await self._execute_internet_search(decisions, context)

        elif action == NextAction.ASK_USER:
            return await self._execute_ask_user(decisions, context, user_input_func)

        elif action == NextAction.CONTINUE_DISCUSSION:
            return self._execute_continue_discussion(decisions)

        elif action == NextAction.PROVIDE_SOLUTION:
            return self._execute_provide_solution(decisions, context)

        else:
            return {"error": f"Unknown action: {action}"}

    async def _execute_internet_search(
        self, decisions: List[ActionDecision], context: DecisionContext
    ) -> Dict[str, Any]:
        """Execute internet search using Tavily."""

        # Generate search queries from agent recommendations
        search_queries = []
        for decision in decisions:
            if decision.recommended_action == NextAction.INTERNET_SEARCH:
                # Extract potential search query from supporting context
                if decision.supporting_context:
                    search_queries.append(decision.supporting_context)

        # If no specific queries, generate based on context
        if not search_queries:
            search_queries = [
                f"{context.domain} best practices {datetime.now().year}",
                f"{context.problem_description[:50]} market research",
                f"{context.domain} industry trends analysis",
            ]

        print(f"🔍 Performing {len(search_queries)} internet searches...")

        search_results = []

        # Check if Tavily is available
        if os.getenv("TAVILY_API_KEY"):
            try:
                from ...tools.tavily_search import tavily_web_search

                for query in search_queries[:3]:  # Limit to 3 searches
                    print(f"  Searching: {query[:60]}...")
                    try:
                        results = tavily_web_search(query, max_results=2)

                        for result in results:
                            search_result = SearchResult(
                                query=query,
                                title=result.get("title", "No title"),
                                url=result.get("url", ""),
                                content=result.get("content", "")[
                                    :500
                                ],  # Limit content
                                relevance_score=0.8,  # Default score
                                source_credibility=0.7,  # Default score
                                timestamp=datetime.now().isoformat(),
                            )
                            search_results.append(search_result)

                        print(f"    Found {len(results)} results")

                    except Exception as e:
                        print(f"    Search failed: {e}")

            except ImportError:
                print("  Tavily integration not available")
                search_results = self._create_simulated_search_results(search_queries)
        else:
            print("  TAVILY_API_KEY not set - simulating search results")
            search_results = self._create_simulated_search_results(search_queries)

        # Store results for future reference
        self.search_results.extend(search_results)

        print(f"✅ Gathered {len(search_results)} search results")

        return {
            "searches_performed": len(search_queries),
            "results_found": len(search_results),
            "search_results": [r.model_dump() for r in search_results],
            "message": f"Internet search completed. Found {len(search_results)} relevant sources.",
        }

    def _create_simulated_search_results(
        self, queries: List[str]
    ) -> List[SearchResult]:
        """Create simulated search results for demo purposes."""
        simulated_results = []

        for query in queries:
            # Create 2 simulated results per query
            for i in range(2):
                simulated_results.append(
                    SearchResult(
                        query=query,
                        title=f"Research Study: {query[:30]}... - Result {i + 1}",
                        url=f"https://example.com/research-{i + 1}",
                        content=f"Simulated research content for '{query}'. Industry analysis shows key trends and insights relevant to decision-making process. Data suggests multiple factors should be considered for optimal outcomes.",
                        relevance_score=0.7 + (i * 0.1),
                        source_credibility=0.8,
                        timestamp=datetime.now().isoformat(),
                    )
                )

        return simulated_results

    async def _execute_ask_user(
        self,
        decisions: List[ActionDecision],
        context: DecisionContext,
        user_input_func: Optional[Callable[[str], str]] = None,
    ) -> Dict[str, Any]:
        """Execute user questioning."""

        if not user_input_func:
            print("❌ No user input function provided - cannot ask user questions")
            return {"error": "No user input function available"}

        # Generate questions from agent recommendations
        questions_to_ask = []
        for decision in decisions:
            if decision.recommended_action == NextAction.ASK_USER:
                question_text = (
                    decision.supporting_context
                    or f"What additional information do you have about {context.problem_description}?"
                )

                from ...models.mai_dxo import UserQuestion

                question = UserQuestion(
                    asking_agent=decision.agent_role,
                    question_text=question_text,
                    context=decision.reasoning,
                    priority=decision.priority_level,
                    timestamp=datetime.now().isoformat(),
                )
                questions_to_ask.append(question)

        # If no specific questions, ask a general one
        if not questions_to_ask:
            from ...models.mai_dxo import UserQuestion

            question = UserQuestion(
                asking_agent=AgentRole.STRATEGIC_ANALYST,
                question_text=f"Can you provide more specific details about your situation regarding: {context.problem_description}?",
                context="General information gathering",
                priority=3,
                timestamp=datetime.now().isoformat(),
            )
            questions_to_ask.append(question)

        print(f"❓ Asking {len(questions_to_ask)} user questions...")

        responses = []
        for question in questions_to_ask:
            print(f"\n🤔 Question from {question.asking_agent.value}:")
            print(f"   {question.question_text}")

            try:
                user_answer = user_input_func(question.question_text)

                response = UserResponse(
                    question_id=question.question_id,
                    response_text=user_answer,
                    follow_up_needed=len(user_answer.split()) < 5,  # Simple heuristic
                    completeness_score=min(
                        1.0, len(user_answer) / 100
                    ),  # Simple scoring
                    timestamp=datetime.now().isoformat(),
                )
                responses.append(response)

                print(f"👤 User Response: {user_answer}")

            except Exception as e:
                print(f"❌ Error getting user input: {e}")
                continue

        # Store questions and responses
        self.user_questions.extend(questions_to_ask)
        self.user_responses.extend(responses)

        print(f"✅ Collected {len(responses)} user responses")

        return {
            "questions_asked": len(questions_to_ask),
            "responses_received": len(responses),
            "user_questions": [q.model_dump() for q in questions_to_ask],
            "user_responses": [r.model_dump() for r in responses],
            "message": f"User questioning completed. Received {len(responses)} responses.",
        }

    def _execute_continue_discussion(
        self, decisions: List[ActionDecision]
    ) -> Dict[str, Any]:
        """Execute continue discussion action."""

        print("💬 Agents will continue discussion for another round")

        # Analyze why agents want to continue discussion
        reasons = []
        for decision in decisions:
            if decision.recommended_action == NextAction.CONTINUE_DISCUSSION:
                reasons.append(decision.reasoning)

        return {
            "continue_reasons": reasons,
            "message": "Agents will engage in another round of discussion to reach better consensus.",
        }

    def _execute_provide_solution(
        self, decisions: List[ActionDecision], context: DecisionContext
    ) -> Dict[str, Any]:
        """Execute provide solution action."""

        print("🎯 Agents are ready to provide final solution")

        # Collect readiness indicators
        solution_readiness = []
        for decision in decisions:
            if decision.recommended_action == NextAction.PROVIDE_SOLUTION:
                solution_readiness.append(
                    {
                        "agent": decision.agent_role.value,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning,
                    }
                )

        return {
            "solution_readiness": solution_readiness,
            "total_searches": len(self.search_results),
            "total_user_responses": len(self.user_responses),
            "message": "All information gathered. Agents ready to provide final solution.",
        }

    def get_coordination_summary(self) -> Dict[str, Any]:
        """Get summary of all coordination actions taken."""
        return {
            "total_actions": len(self.action_history),
            "search_results_gathered": len(self.search_results),
            "user_questions_asked": len(self.user_questions),
            "user_responses_received": len(self.user_responses),
            "action_history": self.action_history,
        }
