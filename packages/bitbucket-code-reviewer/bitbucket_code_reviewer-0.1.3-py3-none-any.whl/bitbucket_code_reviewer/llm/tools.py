"""LangChain tools for the code review agent."""

from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

from ..core.models import DirectoryListing, FileContent


class CodeReviewTools:
    """Collection of tools for the code review agent."""

    def __init__(self, working_directory: str = "."):
        """Initialize tools with working directory.

        Args:
            working_directory: Base directory for file operations
        """
        self.working_directory = Path(working_directory).resolve()

    @tool
    def read_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> FileContent:
        """Read the contents of a file, optionally limiting to specific line ranges.

        Args:
            file_path: Path to the file to read (relative to working directory)
            start_line: Optional starting line number (1-indexed)
            end_line: Optional ending line number (1-indexed)

        Returns:
            FileContent object with the file contents
        """
        full_path = self.working_directory / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError as err:
            raise ValueError(f"Cannot read binary file: {file_path}") from err

        lines = content.splitlines()

        # Apply line range filtering if specified
        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)

            # Validate line numbers
            if start_line and (start_line < 1 or start_line > len(lines)):
                raise ValueError(f"Invalid start_line: {start_line}")
            if end_line and (end_line < 1 or end_line > len(lines)):
                raise ValueError(f"Invalid end_line: {end_line}")
            if start_idx >= end_idx:
                raise ValueError(
                    f"start_line ({start_line}) must be less than end_line ({end_line})"
                )

            selected_lines = lines[start_idx:end_idx]
            content = "\n".join(selected_lines)

        return FileContent(
            file_path=file_path,
            content=content,
            start_line=start_line,
            end_line=end_line,
        )

    @tool
    def list_directory(self, path: str = ".") -> DirectoryListing:
        """List the contents of a directory.

        Args:
            path: Directory path to list (relative to working directory)

        Returns:
            DirectoryListing object with files and subdirectories
        """
        full_path = self.working_directory / path

        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not full_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        try:
            entries = list(full_path.iterdir())
        except PermissionError as err:
            raise ValueError(f"Permission denied accessing directory: {path}") from err

        files = []
        directories = []

        for entry in sorted(entries):
            if entry.is_file():
                files.append(entry.name)
            elif entry.is_dir() and not entry.name.startswith("."):  # Skip hidden dirs
                directories.append(entry.name)

        return DirectoryListing(
            path=path,
            files=files,
            directories=directories,
        )

    @tool
    def get_file_info(self, file_path: str) -> dict:
        """Get basic information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        full_path = self.working_directory / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = full_path.stat()

        return {
            "file_path": file_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": full_path.is_file(),
            "extension": full_path.suffix,
        }

    @tool
    def search_files(self, pattern: str, path: str = ".") -> list[str]:
        """Search for files matching a pattern in a directory tree.

        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.md")
            path: Starting directory path

        Returns:
            List of matching file paths
        """
        full_path = self.working_directory / path

        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        try:
            matches = list(full_path.glob(pattern))
        except ValueError as err:
            raise ValueError(f"Invalid glob pattern: {pattern}") from err

        # Convert to relative paths
        relative_matches = []
        for match in matches:
            if match.is_file():
                relative_matches.append(str(match.relative_to(self.working_directory)))

        return sorted(relative_matches)


# Factory function to create tools with working directory
def create_code_review_tools(working_directory: str = ".") -> list:
    """Create a list of code review tools.

    Args:
        working_directory: Base directory for file operations

    Returns:
        List of LangChain tools
    """
    tools_instance = CodeReviewTools(working_directory)

    return [
        tools_instance.read_file,
        tools_instance.list_directory,
        tools_instance.get_file_info,
        tools_instance.search_files,
    ]
