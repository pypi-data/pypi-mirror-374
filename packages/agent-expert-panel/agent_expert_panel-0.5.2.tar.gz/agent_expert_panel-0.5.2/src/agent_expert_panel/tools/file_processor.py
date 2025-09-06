"""
File processing tools for handling file attachments.

This module provides tools to read and process different file types,
converting them to text content for use in agent discussions.
"""

import json
import csv
import logging
from pathlib import Path
import yaml

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ..models.file_attachment import FileAttachment, FileType, FileProcessingError


logger = logging.getLogger(__name__)


class FileProcessor:
    """Main file processor that handles different file types."""

    def __init__(
        self, supported_types: list[FileType] = None, max_file_size_mb: float = 10.0
    ):
        """
        Initialize FileProcessor with configuration.

        Args:
            supported_types: List of supported file types. If None, all types are supported.
            max_file_size_mb: Maximum file size in megabytes
        """
        if supported_types is None:
            # Default to all file types
            self.supported_types = list(FileType)
        else:
            self.supported_types = supported_types

        self.max_file_size_mb = max_file_size_mb
        self._statistics = {
            "total_files_processed": 0,
            "successful_processes": 0,
            "failed_processes": 0,
            "total_size_processed_mb": 0.0,
        }

    def is_file_type_supported(self, file_type: FileType) -> bool:
        """Check if a file type is supported by this processor."""
        return file_type in self.supported_types

    def process_file_instance(self, file_path: Path | FileAttachment) -> FileAttachment:
        """
        Process a file and return FileAttachment with content.

        Args:
            file_path: Either a Path or FileAttachment object

        Returns:
            FileAttachment with content populated
        """
        try:
            if isinstance(file_path, Path):
                # Check if file exists first
                if not file_path.exists():
                    return self._create_processing_result(
                        file_path,
                        FileType.TEXT,  # Default file type for non-existent files
                        success=False,
                        error_message=f"File does not exist: {file_path}",
                    )
                file_attachment = FileAttachment.from_path(file_path)
            else:
                file_attachment = file_path

            # Validate file type is supported
            if not self.is_file_type_supported(file_attachment.file_type):
                return self._create_processing_result(
                    file_attachment.file_path,
                    file_attachment.file_type,
                    success=False,
                    error_message=f"File type {file_attachment.file_type.value} not supported",
                )

            # Validate file size
            self._validate_file_size(file_attachment.file_path)

            content = self._extract_content(file_attachment)
            file_attachment.content = content

            # Add additional metadata based on file type
            if file_attachment.file_type == FileType.JSON:
                try:
                    import json

                    # Try to parse the JSON content, skipping the header if present
                    json_text = (
                        content.split("\n\n", 1)[1] if "\n\n" in content else content
                    )
                    json.loads(json_text)
                    file_attachment.metadata["json_valid"] = True
                except (json.JSONDecodeError, IndexError):
                    file_attachment.metadata["json_valid"] = False

            # Update statistics
            self._statistics["total_files_processed"] += 1
            self._statistics["successful_processes"] += 1
            file_size = file_attachment.file_path.stat().st_size / (1024 * 1024)
            self._statistics["total_size_processed_mb"] += file_size

            return file_attachment
        except Exception as e:
            self._statistics["total_files_processed"] += 1
            self._statistics["failed_processes"] += 1

            # Get the file path to use in error handling
            if isinstance(file_path, Path):
                error_file_path = file_path
                error_file_type = FileType.TEXT  # Default type
            else:
                error_file_path = file_path.file_path
                error_file_type = file_path.file_type

            return self._create_processing_result(
                error_file_path, error_file_type, success=False, error_message=str(e)
            )

    def process_multiple_files(self, file_paths: list[Path]) -> list[FileAttachment]:
        """Process multiple files and return list of FileAttachments."""
        results = []
        for file_path in file_paths:
            result = self.process_file_instance(file_path)
            results.append(result)
        return results

    def batch_process_directory(
        self, directory_path: Path, file_pattern: str = "*"
    ) -> list[FileAttachment]:
        """Process all files in a directory matching the pattern."""
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            return []

        matching_files = list(directory.glob(file_pattern))
        supported_files = [
            f for f in matching_files if f.is_file() and is_supported_file(f)
        ]

        return self.process_multiple_files(supported_files)

    def get_processing_statistics(self) -> dict[str, any]:
        """Get processing statistics."""
        stats = self._statistics.copy()
        # Add user-friendly aliases
        stats["successful_files"] = stats["successful_processes"]
        stats["failed_files"] = stats["failed_processes"]
        # Add file types processed (placeholder for now)
        stats["file_types_processed"] = []  # TODO: Track file types processed
        return stats

    def reset_statistics(self) -> None:
        """Reset processing statistics."""
        self._statistics = {
            "total_files_processed": 0,
            "successful_processes": 0,
            "failed_processes": 0,
            "total_size_processed_mb": 0.0,
        }

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions."""
        return get_supported_extensions()

    def is_extension_supported(self, extension: str) -> bool:
        """Check if a file extension is supported."""
        return extension.lower() in self.get_supported_extensions()

    def _validate_file_size(self, file_path: Path, max_size_mb: float = None) -> None:
        """Validate file size against limits."""
        if max_size_mb is None:
            max_size_mb = self.max_file_size_mb

        if not file_path.exists():
            raise FileProcessingError(file_path, "File does not exist")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise FileProcessingError(
                file_path,
                f"File size ({file_size_mb:.1f}MB) exceeds limit ({max_size_mb:.1f}MB)",
            )

    def _get_file_metadata(self, file_path: Path) -> dict[str, any]:
        """Get file metadata."""
        stat = file_path.stat()
        return {
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "modified_time": stat.st_mtime,  # Keep for backward compatibility
            "extension": file_path.suffix,
            "file_extension": file_path.suffix,  # Keep for backward compatibility
            "file_name": file_path.name,
        }

    def _create_processing_result(
        self,
        file_path: Path,
        file_type: FileType,
        success: bool = True,
        content: str = "",
        error_message: str = "",
        metadata: dict = None,
    ) -> FileAttachment:
        """Create a processing result FileAttachment."""
        # Get file size and metadata if file exists, otherwise use defaults
        if file_path.exists():
            file_size = file_path.stat().st_size
            if metadata is None:
                metadata = self._get_file_metadata(file_path)
        else:
            file_size = 0
            if metadata is None:
                metadata = {}

        # Temporarily skip file validation for non-existent files
        original_skip = getattr(FileAttachment, "_skip_file_validation", False)
        if not file_path.exists():
            FileAttachment._skip_file_validation = True

        try:
            attachment = FileAttachment(
                file_path=file_path,
                filename=file_path.name,
                file_type=file_type,
                file_size=file_size,
                content=content if success else None,
                metadata=metadata,
                success=success,
                error_message=error_message if not success else None,
            )
        finally:
            # Restore original validation setting
            FileAttachment._skip_file_validation = original_skip

        return attachment

    def _detect_file_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        # Try to detect encoding by reading first few bytes
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(1024)

            # Simple heuristic encoding detection
            try:
                raw_data.decode("utf-8")
                return "utf-8"
            except UnicodeDecodeError:
                pass

            try:
                raw_data.decode("latin-1")
                return "latin-1"
            except UnicodeDecodeError:
                pass

            return "ascii"
        except Exception:
            return "utf-8"  # Default fallback

    def _extract_text_content(self, file_path: Path) -> str:
        """Extract text content from file."""
        return self._read_text_file(file_path)

    def _extract_json_content(self, file_path: Path) -> str:
        """Extract JSON content from file."""
        return self._read_json_file(file_path)

    def _extract_csv_content(self, file_path: Path) -> str:
        """Extract CSV content from file."""
        return self._read_csv_file(file_path)

    # Static method for backward compatibility with original API
    @staticmethod
    def process_file(file_attachment: FileAttachment) -> FileAttachment:
        """
        Process a file attachment and extract its text content (static version).

        Args:
            file_attachment: The file attachment to process

        Returns:
            FileAttachment with populated content field
        """
        return FileProcessor.process_file_static(file_attachment)

    # Static method for backward compatibility
    @staticmethod
    def process_file_static(file_attachment: FileAttachment) -> FileAttachment:
        """
        Process a file attachment and extract its text content (static version).

        Args:
            file_attachment: The file attachment to process

        Returns:
            FileAttachment with populated content field

        Raises:
            FileProcessingError: If file processing fails
        """
        # Create a temporary instance to use the instance methods
        temp_processor = FileProcessor()
        return temp_processor.process_file_instance(file_attachment)

    def _extract_content(self, file_attachment: FileAttachment) -> str:
        """Extract text content based on file type (instance method)."""
        return self._extract_content_static(file_attachment)

    @staticmethod
    def _extract_content_static(file_attachment: FileAttachment) -> str:
        """Extract text content based on file type."""
        file_type = file_attachment.file_type
        file_path = file_attachment.file_path
        if file_type == FileType.TEXT:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.MARKDOWN:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.CSV:
            return FileProcessor._read_csv_file(file_path)
        elif file_type == FileType.JSON:
            return FileProcessor._read_json_file(file_path)
        elif file_type == FileType.PDF:
            return FileProcessor._read_pdf_file(file_path)
        elif file_type == FileType.YAML:
            return FileProcessor._read_yaml_file(file_path)
        elif file_type == FileType.PYTHON:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.XML:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.HTML:
            return FileProcessor._read_text_file(file_path)
        else:
            # Fallback to text reading
            return FileProcessor._read_text_file(file_path)

    @staticmethod
    def _read_text_file(file_path: Path) -> str:
        """Read a plain text file."""
        # Try multiple encodings
        encodings = ["utf-8", "utf-16", "latin-1", "ascii"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except UnicodeError:
                # This includes UTF-16 BOM errors and other Unicode-related issues
                continue
            except Exception as e:
                # If we get a non-encoding error (like FileNotFoundError),
                # don't try other encodings
                raise FileProcessingError(file_path, f"Failed to read text file: {e}")

        # If all encodings fail, read as binary and replace invalid chars
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return content.decode("utf-8", errors="replace")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read text file: {e}")

    @staticmethod
    def _read_csv_file(file_path: Path) -> str:
        """Read a CSV file and convert to formatted text."""
        try:
            content_lines = []
            with open(file_path, "r", encoding="utf-8", newline="") as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except csv.Error:
                    delimiter = ","

                reader = csv.reader(f, delimiter=delimiter)

                # Read and format rows
                rows = list(reader)
                if not rows:
                    return "Empty CSV file"

                # Add header
                content_lines.append(f"CSV File: {file_path.name}")
                content_lines.append(
                    f"Rows: {len(rows)}, Columns: {len(rows[0]) if rows else 0}"
                )

                content_lines.append("")

                # Add column headers
                if rows:
                    headers = rows[0]
                    content_lines.append("| " + " | ".join(headers) + " |")
                    content_lines.append(
                        "| " + " | ".join(["---"] * len(headers)) + " |"
                    )

                    # Add data rows (limit to first 10 for readability)
                    for i, row in enumerate(rows[1:11], 1):
                        # Pad row to match header length
                        padded_row = row + [""] * (len(headers) - len(row))
                        content_lines.append(
                            "| " + " | ".join(padded_row[: len(headers)]) + " |"
                        )

                    if len(rows) > 11:
                        content_lines.append(f"... and {len(rows) - 11} more rows")

                return "\n".join(content_lines)

        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read CSV file: {e}")

    @staticmethod
    def _read_json_file(file_path: Path) -> str:
        """Read a JSON file and convert to formatted text."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Pretty format the JSON
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)

            return f"JSON File: {file_path.name}\n\n{formatted_json}"

        except json.JSONDecodeError as e:
            raise FileProcessingError(file_path, f"Invalid JSON format: {e}")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read JSON file: {e}")

    @staticmethod
    def _read_pdf_file(file_path: Path) -> str:
        """Read a PDF file and extract text."""
        if not pdfplumber and not PyPDF2:
            raise FileProcessingError(
                file_path,
                "PDF support not available. Install pdfplumber or PyPDF2: pip install pdfplumber",
            )

        try:
            # Try pdfplumber first (better text extraction)
            if pdfplumber:
                return FileProcessor._read_pdf_with_pdfplumber(file_path)
            else:
                return FileProcessor._read_pdf_with_pypdf2(file_path)
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read PDF file: {e}")

    @staticmethod
    def _read_pdf_with_pdfplumber(file_path: Path) -> str:
        """Read PDF using pdfplumber."""

        content_lines = [f"PDF File: {file_path.name}\n"]
        with pdfplumber.open(file_path) as pdf:
            content_lines.append(f"Pages: {len(pdf.pages)}\n")

            for i, page in enumerate(pdf.pages[:10], 1):  # Limit to first 10 pages
                text = page.extract_text()
                if text:
                    content_lines.append(f"--- Page {i} ---")
                    content_lines.append(text.strip())
                    content_lines.append("")

            if len(pdf.pages) > 10:
                content_lines.append(f"... and {len(pdf.pages) - 10} more pages")

        return "\n".join(content_lines)

    @staticmethod
    def _read_pdf_with_pypdf2(file_path: Path) -> str:
        """Read PDF using PyPDF2 (fallback)."""
        content_lines = [f"PDF File: {file_path.name}\n"]

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            content_lines.append(f"Pages: {len(reader.pages)}\n")
            for i, page in enumerate(reader.pages[:10], 1):  # Limit to first 10 pages
                text = page.extract_text()
                if text:
                    content_lines.append(f"--- Page {i} ---")
                    content_lines.append(text.strip())
                    content_lines.append("")

            if len(reader.pages) > 10:
                content_lines.append(f"... and {len(reader.pages) - 10} more pages")

        return "\n".join(content_lines)

    @staticmethod
    def _read_yaml_file(file_path: Path) -> str:
        """Read a YAML file and convert to formatted text."""
        if not yaml:
            raise FileProcessingError(
                file_path,
                "YAML support not available. Install PyYAML: pip install PyYAML",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Convert to formatted YAML
            formatted_yaml = yaml.dump(data, default_flow_style=False, indent=2)

            return f"YAML File: {file_path.name}\n\n{formatted_yaml}"

        except yaml.YAMLError as e:
            raise FileProcessingError(file_path, f"Invalid YAML format: {e}")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read YAML file: {e}")


def process_file_attachment(file_path: str | Path) -> FileAttachment:
    """
    Convenience function to create and process a file attachment.

    Args:
        file_path: Path to the file to attach

    Returns:
        Processed FileAttachment with content

    Raises:
        FileProcessingError: If file processing fails
    """
    attachment = FileAttachment.from_path(file_path)
    return FileProcessor.process_file_static(attachment)


def get_supported_extensions() -> list[str]:
    """Get list of supported file extensions."""
    return [
        ".txt",
        ".md",
        ".markdown",
        ".csv",
        ".json",
        ".yaml",
        ".yml",
        ".py",
        ".xml",
        ".html",
        ".htm",
        ".pdf",
    ]


def is_supported_file(file_path: Path | str) -> bool:
    """Check if a file is supported for attachment."""
    path = Path(file_path)
    return path.suffix.lower() in get_supported_extensions()
