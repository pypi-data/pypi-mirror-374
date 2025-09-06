"""
CLI utilities for handling file attachments.

This module provides CLI-specific utilities for handling file attachments
in the agent-expert-panel system.
"""

from pathlib import Path
from typing import Optional, Callable

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel as RichPanel

from ..models.file_attachment import (
    FileAttachment,
    AttachedMessage,
    FileProcessingError,
    FileType,
)
from ..tools.file_processor import (
    process_file_attachment,
    get_supported_extensions,
    is_supported_file,
)


class FileAttachmentCLI:
    """CLI handler for file attachments."""

    def __init__(
        self,
        console: Optional[Console] = None,
        max_file_size: int = 50 * 1024 * 1024,  # 50MB default
        supported_types: list[FileType] = None,
    ):
        self.console = console or Console()
        self.max_file_size = max_file_size

        if supported_types is None:
            # Default to all file types
            self.supported_types = list(FileType)
        else:
            self.supported_types = supported_types

    def is_file_type_supported(self, file_type: FileType) -> bool:
        """Check if a file type is supported."""
        return file_type in self.supported_types

    def _validate_file_size(self, file_path: Path) -> None:
        """Validate file size against maximum limit."""
        if not file_path.exists():
            raise FileProcessingError(file_path, "File does not exist")

        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise FileProcessingError(
                file_path,
                f"File size {file_size} bytes exceeds maximum allowed size of {self.max_file_size} bytes",
            )

    def _validate_file_type(self, file_type: FileType) -> None:
        """Validate that file type is supported."""
        if not self.is_file_type_supported(file_type):
            raise FileProcessingError(
                None, f"File type {file_type.value} is not supported"
            )

    def _validate_file_path(self, file_path: Path) -> None:
        """Validate that file path exists and is a file."""
        if not file_path.exists():
            raise FileProcessingError(file_path, "File does not exist")
        if not file_path.is_file():
            raise FileProcessingError(file_path, "Path is not a file")

    def process_file(self, file_path: Path) -> FileAttachment:
        """Process a single file and return FileAttachment."""
        # Validate file
        self._validate_file_path(file_path)
        self._validate_file_size(file_path)

        # Create attachment
        attachment = FileAttachment.from_path(file_path)
        self._validate_file_type(attachment.file_type)

        # Read content
        content = self._read_file_content(file_path, attachment.file_type)
        attachment.content = content

        return attachment

    def _read_file_content(self, file_path: Path, file_type: FileType) -> str:
        """Read and process file content based on file type."""
        # Use the static processor for content reading
        from ..tools.file_processor import FileProcessor

        attachment = FileAttachment.from_path(file_path)
        processed = FileProcessor.process_file_static(attachment)
        return processed.content or ""

    def process_multiple_files(self, file_paths: list[Path]) -> list[FileAttachment]:
        """Process multiple files and return list of attachments."""
        attachments = []
        for file_path in file_paths:
            try:
                attachment = self.process_file(file_path)
                attachments.append(attachment)
            except FileProcessingError:
                # Skip failed files but continue with others
                continue
        return attachments

    def get_processing_summary(self) -> dict[str, any]:
        """Get processing statistics summary."""
        # For now, return basic stats - in a real implementation this would track actual stats
        return {
            "total_files_processed": 0,
            "successful_processes": 0,
            "failed_processes": 0,
        }

    def reset_processing_state(self) -> None:
        """Reset processing state/statistics."""
        # For now this is a no-op - in a real implementation would reset counters
        pass

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions."""
        return get_supported_extensions()

    def is_extension_supported(self, extension: str) -> bool:
        """Check if file extension is supported."""
        return extension.lower() in self.get_supported_extensions()

    def _get_file_type_from_extension(self, file_path: Path) -> FileType:
        """Get file type from file extension."""
        return FileAttachment._detect_file_type(file_path)

    def process_file_arguments(self, files: list[str] | None) -> list[FileAttachment]:
        """
        Process file arguments from CLI and return FileAttachment objects.

        Args:
            files: List of file paths from CLI arguments

        Returns:
            List of processed FileAttachment objects

        Raises:
            FileProcessingError: If any file processing fails
        """
        if not files:
            return []

        attachments = []

        for file_path_str in files:
            file_path = Path(file_path_str)

            # Validate file exists
            if not file_path.exists():
                self.console.print(f"[red]Error: File not found: {file_path}[/red]")
                continue

            try:
                # Validate file size first
                self._validate_file_size(file_path)

                # Check file type support
                file_attachment = FileAttachment.from_path(file_path)
                if not self.is_file_type_supported(file_attachment.file_type):
                    self.console.print(
                        f"[yellow]Warning: Unsupported file type: {file_path}[/yellow]"
                    )
                    self.console.print(
                        f"Supported extensions: {', '.join(get_supported_extensions())}"
                    )

                    if not Confirm.ask(
                        f"Attempt to process {file_path.name} as text file?",
                        default=False,
                    ):
                        continue

                # Process the file
                self.console.print(f"[dim]Processing file: {file_path.name}...[/dim]")
                attachment = process_file_attachment(file_path)
                attachments.append(attachment)
                self.console.print(f"[green]✓ Processed: {file_path.name}[/green]")

            except FileProcessingError as e:
                self.console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
                continue
            except PermissionError as e:
                self.console.print(
                    f"[red]Permission denied accessing {file_path.name}: {e}[/red]"
                )
                continue

        return attachments

    def interactive_file_selection(self) -> list[FileAttachment]:
        """
        Interactive file selection for CLI users.

        Returns:
            List of selected and processed FileAttachment objects
        """
        if not Confirm.ask(
            "Would you like to attach files to your message?", default=False
        ):
            return []

        attachments = []

        self.console.print("\n[bold]File Attachment Options:[/bold]")
        self.console.print("1. Enter file path(s) manually")
        self.console.print("2. Browse current directory")
        self.console.print("3. Skip file attachments")

        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")

        if choice == "1":
            attachments = self._manual_file_input()
        elif choice == "2":
            attachments = self._browse_directory()
        else:
            return []

        if attachments:
            self._display_attachment_summary(attachments)

        return attachments

    def _manual_file_input(self) -> list[FileAttachment]:
        """Handle manual file path input."""
        attachments = []

        self.console.print(
            f"\n[dim]Supported file types: {', '.join(get_supported_extensions())}[/dim]"
        )

        while True:
            file_path_str = Prompt.ask(
                "Enter file path (or 'done' to finish)", default="done"
            )

            if file_path_str.lower() == "done":
                break

            file_path = Path(file_path_str).expanduser().resolve()

            if not file_path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                continue

            if not file_path.is_file():
                self.console.print(f"[red]Not a file: {file_path}[/red]")
                continue

            try:
                # Validate file size and type first
                self._validate_file_size(file_path)
                file_attachment = FileAttachment.from_path(file_path)
                if not self.is_file_type_supported(file_attachment.file_type):
                    self.console.print(
                        f"[yellow]File type not supported: {file_attachment.file_type.value}[/yellow]"
                    )
                    continue

                attachment = process_file_attachment(file_path)
                attachments.append(attachment)
                self.console.print(f"[green]✓ Added: {attachment.filename}[/green]")

            except FileProcessingError as e:
                self.console.print(f"[red]Error: {e}[/red]")
                continue

        return attachments

    def _browse_directory(self) -> list[FileAttachment]:
        """Browse current directory for file selection."""
        current_dir = Path.cwd()
        supported_files = []
        # Find supported files in current directory
        for file_path in current_dir.iterdir():
            if file_path.is_file() and is_supported_file(file_path):
                supported_files.append(file_path)

        if not supported_files:
            self.console.print(
                "[yellow]No supported files found in current directory.[/yellow]"
            )
            return []

        # Display files in a table
        table = Table(title=f"Supported Files in {current_dir.name}")
        table.add_column("#", style="cyan")
        table.add_column("Filename", style="green")
        table.add_column("Size", style="white")
        table.add_column("Type", style="yellow")

        for i, file_path in enumerate(supported_files, 1):
            file_size = file_path.stat().st_size
            size_str = self._format_file_size(file_size)
            file_type = file_path.suffix.lower() or "no extension"

            table.add_row(str(i), file_path.name, size_str, file_type)

        self.console.print(table)

        # Let user select files
        attachments = []
        while True:
            choice = Prompt.ask(
                f"Select file number (1-{len(supported_files)}) or 'done' to finish",
                default="done",
            )

            if choice.lower() == "done":
                break

            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(supported_files):
                    file_path = supported_files[file_index]

                    # Check if already selected
                    if any(att.file_path == file_path for att in attachments):
                        self.console.print(
                            f"[yellow]File already selected: {file_path.name}[/yellow]"
                        )
                        continue

                    try:
                        attachment = process_file_attachment(file_path)
                        attachments.append(attachment)
                        self.console.print(
                            f"[green]✓ Added: {attachment.filename}[/green]"
                        )

                    except FileProcessingError as e:
                        self.console.print(
                            f"[red]Error processing {file_path.name}: {e}[/red]"
                        )
                        continue

                else:
                    self.console.print(
                        f"[red]Invalid selection. Choose 1-{len(supported_files)}[/red]"
                    )

            except ValueError:
                self.console.print("[red]Invalid input. Enter a number or 'done'[/red]")

        return attachments

    def _display_attachment_summary(self, attachments: list[FileAttachment]) -> None:
        """Display a summary of selected attachments."""
        if not attachments:
            return

        self.console.print(
            f"\n[bold green]Selected {len(attachments)} file(s):[/bold green]"
        )

        total_size = 0
        for attachment in attachments:
            size_str = self._format_file_size(attachment.file_size)
            total_size += attachment.file_size
            preview = attachment.get_content_preview(100)
            preview_lines = preview.count("\n") + 1

            self.console.print(
                f"  • {attachment.filename} ({attachment.file_type.value}, {size_str}, ~{preview_lines} lines)"
            )

        total_size_str = self._format_file_size(total_size)
        self.console.print(f"[dim]Total size: {total_size_str}[/dim]")

    def create_attached_message(
        self, content: str, attachments: list[FileAttachment], source: str = "user"
    ) -> AttachedMessage:
        """

        Create an AttachedMessage from content and attachments.

        Args:
            content: The text content of the message
            attachments: List of file attachments
            source: Message source identifier

        Returns:
            AttachedMessage object
        """

        return AttachedMessage(content=content, attachments=attachments, source=source)

    def display_message_preview(self, message: AttachedMessage) -> None:
        """Display a preview of the message with attachments."""
        if not message.has_attachments():
            return

        # Show attachment summary
        summary = message.get_attachment_summary()
        self.console.print(
            f"\n[bold blue]Message with attachments:[/bold blue] {summary}"
        )

        # Show content preview
        preview_content = message.get_full_content(include_file_content=False)
        if len(preview_content) > 500:
            preview_content = preview_content[:500] + "..."

        panel = RichPanel(preview_content, title="Message Preview", border_style="blue")
        self.console.print(panel)

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def create_file_attachment_input_func(
    attachments: list[FileAttachment], console: Optional[Console] = None
) -> Callable[[str], str]:
    """
    Create a custom input function that includes file attachments.

    This function can be used as the human_input_func in panel discussions
    to include file attachments in human responses.

    Args:
        attachments: List of file attachments to include
        console: Optional console for output

    Returns:
        Custom input function that includes file content
    """
    console = console or Console()

    def attachment_input_func(prompt: str) -> str:
        """Custom input function that includes file attachments."""
        # Display the prompt
        console.print(f"\n[bold yellow]{prompt}[/bold yellow]")

        # Show attachment info
        if attachments:
            console.print(
                f"[dim]Available attachments: {len(attachments)} file(s)[/dim]"
            )
            for attachment in attachments:
                console.print(
                    f"  - {attachment.filename} ({attachment.file_type.value})"
                )

        # Get user input
        response = input("\nYour response: ")

        # Create attached message and return full content
        attached_message = AttachedMessage(
            content=response, attachments=attachments, source="human"
        )

        return attached_message.get_full_content()

    return attachment_input_func
