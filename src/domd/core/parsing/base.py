"""Base classes for configuration file parsers."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for all configuration file parsers."""

    #: Set of file patterns this parser can handle (e.g., ["*.py", "*.pyi"])
    supported_file_patterns: Set[str] = set()

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        file_path: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ):
        """Initialize the parser.

        Args:
            project_root: Root directory of the project
            file_path: Path to the file being parsed (if known)
            **kwargs: Additional parser-specific arguments
        """
        self.project_root = Path(project_root).resolve() if project_root else None
        self.file_path = Path(file_path).resolve() if file_path else None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the parser if not already initialized."""
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self) -> None:
        """Perform any necessary initialization."""
        pass

    @classmethod
    def can_parse(cls, file_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if this parser can handle the file
        """
        if not cls.supported_file_patterns:
            return False

        file_path = Path(file_path)
        return any(file_path.match(pattern) for pattern in cls.supported_file_patterns)

    def parse(
        self, file_path: Optional[Union[str, Path]] = None
    ) -> List[Dict[str, Any]]:
        """Parse the configuration file and extract commands.

        Args:
            file_path: Path to the file to parse (overrides self.file_path if provided)

        Returns:
            List of command dictionaries with the following keys:
            - command: The command string to execute
            - description: Human-readable description of the command
            - source: Source of the command (e.g., file path)
            - type: Type of command (e.g., 'test', 'build', 'lint')
            - metadata: Additional metadata about the command
        """
        if file_path is not None:
            self.file_path = Path(file_path).resolve()

        if self.file_path is None:
            raise ValueError("No file path provided for parsing")

        self.initialize()
        return self._parse_commands()

    @abstractmethod
    def _parse_commands(self) -> List[Dict[str, Any]]:
        """Parse commands from the configuration file.

        Subclasses must implement this method to parse commands from their
        specific configuration format.

        Returns:
            List of command dictionaries
        """
        raise NotImplementedError("Subclasses must implement _parse_commands()")
