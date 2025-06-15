"""Base parser class for detecting commands in configuration files."""

import abc
import logging
from pathlib import Path
from typing import List, Optional, Set, Union

from ...models import Command

logger = logging.getLogger(__name__)


class BaseParser(abc.ABC):
    """Abstract base class for command parsers."""

    @classmethod
    @abc.abstractmethod
    def get_supported_files(cls) -> Set[str]:
        """Get the file patterns this parser can handle.

        Returns:
            Set of file patterns (e.g., {"*.py", "*.sh"})
        """
        raise NotImplementedError("Subclasses must implement get_supported_files()")

    @abc.abstractmethod
    def parse(self, content: str, file_path: Optional[Path] = None) -> List[Command]:
        """Parse commands from file content.

        Args:
            content: File content to parse
            file_path: Optional path to the file being parsed

        Returns:
            List of Command objects
        """
        raise NotImplementedError("Subclasses must implement parse()")

    def parse_file(self, file_path: Union[str, Path]) -> List[Command]:
        """Parse commands from a file.

        Args:
            file_path: Path to the file to parse

        Returns:
            List of Command objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            return self.parse(content, file_path=file_path)
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}", exc_info=True)
            return []

    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this parser can handle the file, False otherwise
        """
        file_path = Path(file_path)
        supported_patterns = self.get_supported_files()

        # If no patterns are specified, assume the parser can handle any file
        if not supported_patterns:
            return True

        # Check if the file matches any of the supported patterns
        file_name = file_path.name
        for pattern in supported_patterns:
            if pattern.startswith("*"):
                if file_name.endswith(pattern[1:]):
                    return True
            elif file_name == pattern:
                return True

        return False
