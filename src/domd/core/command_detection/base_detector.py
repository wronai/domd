"""Base command detector class for finding and managing project commands."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .handlers import CommandHandler, ConfigFileHandler
from .models import Command, CommandResult
from .parsers import ParserRegistry
from .utils import get_virtualenv_info

logger = logging.getLogger(__name__)


class CommandDetector:
    """Base class for detecting and managing project commands."""

    def __init__(
        self,
        project_path: Union[str, Path] = ".",
        timeout: int = 60,
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        todo_file: Union[str, Path] = "TODO.md",
        done_file: Union[str, Path] = "DONE.md",
        script_file: Union[str, Path] = "todo.sh",
        ignore_file: str = ".doignore",
        venv_path: Optional[str] = None,
    ):
        """Initialize the command detector.

        Args:
            project_path: Path to the project root
            timeout: Command execution timeout in seconds
            exclude_patterns: List of file patterns to exclude
            include_patterns: List of file patterns to include
            todo_file: Path to the TODO file
            done_file: Path to the DONE file
            script_file: Path to the script file
            ignore_file: Path to the ignore file
            venv_path: Path to the virtual environment
        """
        self.project_path = Path(project_path).resolve()
        self.timeout = timeout
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []

        # Resolve file paths relative to project_path
        self.todo_file = (self.project_path / Path(todo_file)).resolve()
        self.done_file = (self.project_path / Path(done_file)).resolve()
        self.script_file = (self.project_path / Path(script_file)).resolve()
        self.ignore_file = self.project_path / Path(ignore_file)

        # Initialize virtual environment
        self.venv_path = venv_path
        self.venv_info = get_virtualenv_info(venv_path or self.project_path)

        # Command ignore patterns (separate from file exclude patterns)
        self.ignore_patterns = []

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all component handlers and services."""
        # Initialize command execution components
        self.command_executor = self._create_command_executor()
        self.command_runner = self._create_command_runner()

        # Initialize handlers
        self.config_handler = self._create_config_handler()
        self.command_handler = self._create_command_handler()

        # Initialize parsers
        self.parser_registry = self._create_parser_registry()
        self.parsers = self._initialize_parsers()

        # Initialize command storage
        self._initialize_command_storage()

    def _create_command_executor(self):
        """Create and return a command executor instance."""
        from ..services.command_executor import CommandExecutor

        return CommandExecutor(timeout=self.timeout)

    def _create_command_runner(self):
        """Create and return a command runner instance."""
        from ..services.command_runner import CommandRunner

        return CommandRunner(executor=self.command_executor)

    def _create_config_handler(self) -> ConfigFileHandler:
        """Create and return a config file handler."""
        return ConfigFileHandler(
            project_path=self.project_path,
            exclude_patterns=self.exclude_patterns,
            include_patterns=self.include_patterns,
            ignore_file=self.ignore_file,
        )

    def _create_command_handler(self) -> CommandHandler:
        """Create and return a command handler."""
        return CommandHandler(
            project_path=self.project_path,
            command_runner=self.command_runner,
            timeout=self.timeout,
            ignore_patterns=self.ignore_patterns,
        )

    def _create_parser_registry(self) -> ParserRegistry:
        """Create and return a parser registry."""
        return ParserRegistry()

    def _initialize_command_storage(self):
        """Initialize command storage references."""
        self.failed_commands = self.command_handler.failed_commands
        self.successful_commands = self.command_handler.successful_commands
        self.ignored_commands = self.command_handler.ignored_commands

    def _initialize_parsers(self) -> List[Any]:
        """Initialize parsers for detecting commands in configuration files.

        Returns:
            List of parser instances
        """
        parsers = []

        # Try to get parsers from registry first
        try:
            parsers = self.parser_registry.get_parsers()
            logger.debug(
                f"Found {len(parsers)} parser(s) in registry: "
                f"{[p.__class__.__name__ for p in parsers]}"
            )
        except Exception as e:
            logger.warning(f"Failed to get parsers from registry: {e}")
            parsers = self._get_legacy_parsers()

        logger.info(f"Initialized {len(parsers)} parsers")
        return parsers

    def _get_legacy_parsers(self) -> List[Any]:
        """Get legacy parsers as fallback."""
        try:
            from domd.parsers import get_all_parsers

            parser_classes = get_all_parsers()
            return [cls() for cls in parser_classes]
        except ImportError as e:
            logger.warning(f"Failed to import legacy parsers: {e}")
            return []

    def scan_project(self) -> List[Command]:
        """Scan the project for commands in configuration files.

        This should be implemented by subclasses to provide specific
        scanning behavior for different types of projects.

        Returns:
            List of Command objects
        """
        raise NotImplementedError("Subclasses must implement scan_project()")

    def test_commands(self, commands: List[Union[Command, Dict]]) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        self.command_handler.test_commands(commands)

    def should_ignore_command(self, command: Union[str, Dict, Command]) -> bool:
        """Check if a command should be ignored based on ignore patterns.

        Args:
            command: Command to check (string, dict, or Command object)

        Returns:
            True if the command should be ignored, False otherwise
        """
        return self.command_handler.should_ignore_command(command)

    def get_ignore_reason(self, command: Union[str, Dict, Command]) -> Optional[str]:
        """Get the reason why a command is ignored.

        Args:
            command: Command to check (string, dict, or Command object)

        Returns:
            Reason string or None if not ignored
        """
        if self.should_ignore_command(command):
            return "Matched ignore pattern in .doignore file"
        return None
