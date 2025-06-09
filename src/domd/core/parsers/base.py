"""Base parser interface for configuration files."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar

T = TypeVar("T", bound="BaseParser")


class BaseParser(ABC):
    """Abstract base class for all configuration file parsers."""

    def __init__(
        self, file_path: Optional[Path] = None, project_root: Optional[Path] = None
    ):
        """Initialize the parser.

        Args:
            file_path: Optional path to the configuration file
            project_root: Optional project root path (defaults to file's parent if file_path is provided)
        """
        self.file_path = file_path.resolve() if file_path else None
        self.project_root = (
            project_root.resolve()
            if project_root
            else (self.file_path.parent if self.file_path else Path.cwd())
        )
        self._commands: List[Dict] = []

    @property
    @abstractmethod
    def supported_file_patterns(self) -> List[str]:
        """Return a list of file patterns this parser supports.

        Returns:
            List of file patterns (e.g., ["Makefile", "makefile"])
        """
        pass

    @classmethod
    def can_parse(cls: Type[T], file_path: Path) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if this parser can handle the file
        """
        # Create a temporary instance to access the property
        try:
            # Create an instance without file_path to access supported_file_patterns
            parser = cls()
            patterns = parser.supported_file_patterns
            return any(
                file_path.name == pattern or file_path.match(pattern)
                for pattern in patterns
            )
        except Exception as e:
            import logging

            logging.warning(
                f"Error checking if {cls.__name__} can parse {file_path}: {e}"
            )
            return False

    @abstractmethod
    def parse(self) -> List[Dict]:
        """Parse the configuration file and extract commands.

        Returns:
            List of command dictionaries with 'command', 'description', 'source', and 'type' keys
        """
        pass

    def _create_command_dict(
        self,
        command: str,
        description: str,
        command_type: str,
        source: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Helper method to create a consistent command dictionary.

        Args:
            command: The command string to execute
            description: Human-readable description of the command
            command_type: Type of command (e.g., 'make_target', 'npm_script')
            source: Optional source identifier (defaults to file path)
            **kwargs: Additional command metadata

        Returns:
            Command dictionary
        """
        return {
            "command": command,
            "description": description,
            "source": source or str(self.file_path.relative_to(self.project_root)),
            "type": command_type,
            "cwd": str(self.file_path.parent),
            **kwargs,
        }
