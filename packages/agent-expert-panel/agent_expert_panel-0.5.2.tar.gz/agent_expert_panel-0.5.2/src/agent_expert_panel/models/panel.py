"""
Panel-related models and enums for the Expert Panel system.
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class DiscussionPattern(Enum):
    """Available discussion patterns for agent interaction."""

    ROUND_ROBIN = "round_robin"
    OPEN_FLOOR = "open_floor"
    STRUCTURED_DEBATE = "structured_debate"


class PanelResult(BaseModel):
    """Results from a panel discussion."""

    # Core fields
    topic: Optional[str] = None
    discussion_pattern: Optional[DiscussionPattern] = None
    agents_participated: Optional[list[str]] = None
    discussion_history: Optional[list[dict[str, Any]]] = None
    consensus_reached: Optional[bool] = None
    final_recommendation: Optional[str] = None
    total_rounds: Optional[int] = None

    # Extended fields for other test scenarios
    query: Optional[str] = None
    results: Optional[list[dict[str, Any]]] = None
    consensus: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
