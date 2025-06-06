"""Core functionality for detecting and managing project commands."""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

from .commands.executor import CommandExecutor, CommandResult
from .parsers import BaseParser
from .reporters.done_md import DoneMDReporter
from .reporters.todo_md import TodoMDReporter

logger = logging.getLogger(__name__)


def get_available_parsers() -> List[Type[BaseParser]]:
    """Dynamically discover all available parser classes.

    Returns:
        List of parser classes that inherit from BaseParser
    """
    from . import parsers

    parser_classes = []

    # Get all modules in the parsers package
    for _, modname, _ in pkgutil.iter_modules(parsers.__path__):
        try:
            # Import the module
            module = importlib.import_module(f"{parsers.__name__}.{modname}")

            # Find all classes that inherit from BaseParser
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseParser)
                    and obj != BaseParser
                    and obj.__module__ == module.__name__
                ):
                    parser_classes.append(obj)
        except ImportError as e:
            logger.warning("Failed to import parser module %s: %s", modname, e)

    return parser_classes


class ProjectCommandDetector:
    """Detects and manages project commands from various configuration files."""

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
    ):
        """Initialize the ProjectCommandDetector.

        Args:
            project_path: Path to the project root
            timeout: Default command execution timeout in seconds
            exclude_patterns: List of file patterns to exclude
            include_patterns: List of file patterns to include (if specified, only these are included)
            todo_file: Path to the TODO.md file
            done_file: Path to the DONE.md file
            script_file: Path to the todo.sh script
            ignore_file: Name of the ignore file
        """
        self.project_path = Path(project_path).resolve()
        self.timeout = timeout
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []

        # Initialize paths
        self.todo_file = self.project_path / todo_file
        self.done_file = self.project_path / done_file
        self.script_file = self.project_path / script_file
        self.ignore_file = self.project_path / ignore_file

        # Initialize components
        self.command_executor = CommandExecutor(timeout=timeout, cwd=self.project_path)
        self.todo_reporter = TodoMDReporter(self.todo_file)
        self.done_reporter = DoneMDReporter(self.done_file)
        self.parsers = self._initialize_parsers()

        # Command storage
        self.failed_commands: List[Dict] = []
        self.successful_commands: List[Dict] = []
        self.ignored_commands: List[Dict] = []

    def _initialize_parsers(self) -> List[Type[BaseParser]]:
        """Get all available parser classes.

        Returns:
            List of parser classes that can be instantiated with a file path
        """
        return get_available_parsers()

    def scan_project(self) -> List[Dict]:
        """Scan the project for commands in various configuration files.

        Returns:
            List of command dictionaries
        """
        if not self.project_path.exists():
            logger.error("Project path does not exist: %s", self.project_path)
            return []

        commands = []

        # Process files using the appropriate parsers
        for file_path in self._find_config_files():
            try:
                parser = self._get_parser_for_file(file_path)
                if parser:
                    file_commands = parser.parse()
                    commands.extend(file_commands)
            except Exception as e:
                logger.error(
                    "Error processing file %s: %s", file_path, e, exc_info=True
                )

        return commands

    def _find_config_files(self) -> List[Path]:
        """Find all configuration files in the project.

        Returns:
            List of Path objects to configuration files
        """
        config_files = set()

        # Get all supported file patterns from parsers
        supported_patterns = set()
        for parser_class in self.parsers:
            # Get the patterns by instantiating the parser with a dummy path
            try:
                dummy_path = self.project_path / "dummy"
                parser = parser_class(dummy_path, self.project_path)
                patterns = parser.supported_file_patterns
                supported_patterns.update(patterns)
            except Exception as e:
                logger.warning(
                    f"Failed to get patterns from {parser_class.__name__}: {e}"
                )

        # Find all matching files in the project
        for pattern in supported_patterns:
            for file_path in self.project_path.rglob(pattern):
                if self._should_process_file(file_path):
                    config_files.add(file_path.resolve())

        return list(config_files)

    def _get_parser_for_file(self, file_path: Path) -> Optional[BaseParser]:
        """Get the appropriate parser for a file.

        Args:
            file_path: Path to the file to parse

        Returns:
            Parser instance or None if no suitable parser found
        """
        for parser_class in self.parsers:
            try:
                # Create a temporary instance to check if it can parse the file
                temp_parser = parser_class(file_path, self.project_path)
                if temp_parser.can_parse(file_path):
                    return temp_parser
            except Exception as e:
                logger.warning(
                    f"Error creating parser {parser_class.__name__} for {file_path}: {e}"
                )
        return None

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed.

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if the file should be processed
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        relative_path = str(file_path.relative_to(self.project_path))

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if self._match_pattern(relative_path, pattern):
                return False

        # Check include patterns (if any)
        if self.include_patterns:
            for pattern in self.include_patterns:
                if self._match_pattern(relative_path, pattern):
                    return True
            return False

        return True

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern.

        Args:
            path: Path to check
            pattern: Pattern to match against

        Returns:
            bool: True if the path matches the pattern
        """
        try:
            # Handle directory patterns with trailing /*
            if pattern.endswith("/*"):
                dir_pattern = pattern[:-2]
                return path.startswith(dir_pattern + "/")

            # Handle glob patterns
            if "*" in pattern or "?" in pattern or "[" in pattern:
                import fnmatch

                return fnmatch.fnmatch(path, pattern)

            # Simple string match
            return pattern in path

        except Exception as e:
            logger.warning("Error matching pattern '%s': %s", pattern, e)
            return False

    def test_commands(self, commands: List[Dict]) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of command dictionaries to test
        """
        self.failed_commands = []
        self.successful_commands = []

        for cmd in commands:
            if self._should_ignore_command(cmd):
                self.ignored_commands.append(cmd)
                continue

            result = self._execute_command(cmd)

            if result.success:
                self.successful_commands.append(
                    {
                        **cmd,
                        "execution_time": result.execution_time,
                    }
                )
            else:
                self.failed_commands.append(
                    {
                        **cmd,
                        "execution_time": result.execution_time,
                        "return_code": result.return_code,
                        "error": result.error,
                    }
                )

    def generate_reports(self) -> None:
        """Generate TODO.md and DONE.md reports."""
        # Generate TODO.md with failed commands
        if self.failed_commands:
            self.todo_reporter.write_report(
                {
                    "failed_commands": self.failed_commands,
                    "successful_commands": self.successful_commands,
                    "project_path": str(self.project_path),
                }
            )

        # Generate DONE.md with successful commands
        if self.successful_commands:
            self.done_reporter.write_report(
                {
                    "successful_commands": self.successful_commands,
                    "project_path": str(self.project_path),
                }
            )

    def _execute_command(self, cmd_info: Dict) -> CommandResult:
        """Execute a single command and return the result.

        Args:
            cmd_info: Command information dictionary

        Returns:
            CommandResult with execution details
        """
        command = cmd_info.get("command", "")
        cwd = cmd_info.get("cwd", self.project_path)
        timeout = cmd_info.get("timeout", self.timeout)

        logger.info("Executing command: %s", command)
        return self.command_executor.execute(command, timeout=timeout, cwd=cwd)

    def _should_ignore_command(self, cmd: Dict) -> bool:
        """Check if a command should be ignored based on ignore rules.

        Args:
            cmd: Command dictionary

        Returns:
            bool: True if command should be ignored
        """
        # TODO: Implement ignore rules logic
        return False
