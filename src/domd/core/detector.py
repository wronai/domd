"""Core functionality for detecting and managing project commands."""

import datetime
import importlib
import importlib.util
import inspect
import json
import logging
import os
import pkgutil
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from ..core.commands import Command, CommandResult
from ..core.commands.executor import CommandExecutor
from ..core.parsers.base import BaseParser
from ..core.reporters.done_md import DoneMDReporter
from ..core.reporters.todo_md import TodoMDReporter
from ..utils.virtualenv import get_virtualenv_info

logger = logging.getLogger(__name__)


def get_available_parsers() -> List[Type[BaseParser]]:
    """Dynamically discover all available parser classes.

    Returns:
        List of parser classes that inherit from BaseParser
    """
    try:
        from . import parsers

        parser_classes = []

        # Get all modules in the parsers package
        for _, modname, _ in pkgutil.iter_modules(parsers.__path__):
            # Skip private modules
            if modname.startswith("_"):
                continue

            # Import the module
            module = importlib.import_module(f".{modname}", "domd.core.parsers")

            # Find all classes that inherit from BaseParser
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseParser)
                    and obj != BaseParser
                    and obj.__module__ == module.__name__
                ):
                    parser_classes.append(obj)

        return parser_classes
    except Exception as e:
        logger.warning(f"Failed to discover parsers: {e}")
        return []


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
        venv_path: Optional[str] = None,
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
            venv_path: Optional path to virtual environment (auto-detected if None)
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

        # Initialize virtual environment
        self.venv_info = self._setup_virtualenv(venv_path)

        # Initialize components with virtualenv support
        self.command_executor = CommandExecutor(
            timeout=timeout, cwd=self.project_path, env=self._get_environment()
        )

        self.todo_reporter = TodoMDReporter(self.todo_file)
        self.done_reporter = DoneMDReporter(self.done_file)
        self.parsers = self._initialize_parsers()

        # Command storage and patterns
        self.ignore_patterns = []  # Patterns for commands to ignore
        self.failed_commands: List[Dict] = []
        self.successful_commands: List[Dict] = []
        self.ignored_commands: List[Dict] = []

    def _setup_virtualenv(self, venv_path: Optional[str] = None) -> Dict[str, Any]:
        """Set up virtual environment for command execution.

        Args:
            venv_path: Optional path to virtual environment

        Returns:
            Dictionary with virtual environment information with the following keys:
                - exists: bool - Whether the virtual environment exists
                - path: Optional[str] - Path to the virtual environment
                - activate_command: Optional[str] - Command to activate the virtual environment
                - python_path: Optional[str] - Path to the Python interpreter in the virtual environment
        """
        try:
            if venv_path:
                # Use explicitly provided virtualenv path
                logger.debug(f"Using provided virtualenv path: {venv_path}")
                venv_info = get_virtualenv_info(venv_path)
            else:
                # Try to auto-detect virtualenv in project directory
                logger.debug(f"Auto-detecting virtualenv in: {self.project_path}")
                venv_info = get_virtualenv_info(str(self.project_path))

            if venv_info["exists"]:
                logger.info(f"Using virtual environment at: {venv_info['path']}")
                if venv_info.get("activate_command"):
                    logger.debug(f"Activation command: {venv_info['activate_command']}")
                if venv_info.get("python_path"):
                    logger.debug(f"Python interpreter: {venv_info['python_path']}")
            else:
                logger.debug("No virtual environment detected")

            return venv_info

        except Exception as e:
            logger.warning(f"Error detecting virtual environment: {e}", exc_info=True)
            return {
                "exists": False,
                "path": None,
                "activate_command": None,
                "python_path": None,
            }

    def _get_environment(self) -> Dict[str, str]:
        """Get environment variables for command execution.

        Returns:
            Dictionary with environment variables with virtualenv paths included

        This method ensures that the virtual environment's bin/Scripts directory
        is included in the PATH, allowing commands to find executables installed
        in the virtual environment.
        """
        env = os.environ.copy()

        # Add virtual environment's bin/scripts to PATH if available
        if self.venv_info.get("path"):
            venv_path = self.venv_info["path"]
            if sys.platform == "win32":
                bin_path = os.path.join(venv_path, "Scripts")
            else:
                bin_path = os.path.join(venv_path, "bin")

            if os.path.exists(bin_path):
                # Add to the beginning of PATH to ensure virtualenv binaries take precedence
                env["PATH"] = f"{bin_path}{os.pathsep}{env.get('PATH', '')}"

                # Set VIRTUAL_ENV for Python tools that check this
                env["VIRTUAL_ENV"] = venv_path

                # On Windows, we also need to set PYTHONHOME to None to avoid conflicts
                if sys.platform == "win32" and "PYTHONHOME" in env:
                    del env["PYTHONHOME"]

        return env

    def execute_command(
        self,
        command: Union[str, List[str]],
        timeout: Optional[int] = None,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = False,
    ) -> Dict[str, Any]:
        """Execute a command with proper environment setup.

        Args:
            command: Command to execute (string or list of args)
            timeout: Optional timeout in seconds
            cwd: Working directory for the command
            env: Additional environment variables to include
            check: If True, raises an exception on non-zero exit code

        Returns:
            Dictionary with command execution results

        The returned dictionary contains:
            - success: bool - Whether the command succeeded
            - return_code: int - The exit code of the command
            - execution_time: float - Time taken in seconds
            - output: str - Combined stdout and stderr
            - stdout: str - Standard output
            - stderr: str - Standard error
            - command: str - The executed command
        """
        # Ensure command is a string for logging
        command_str = command if isinstance(command, str) else " ".join(command)
        logger.info(f"Executing command: {command_str}")

        # Prepare the environment
        exec_env = self._get_environment()
        if env:
            # Update with custom environment variables, ensuring all values are strings
            for key, value in (env or {}).items():
                if value is not None:
                    exec_env[str(key)] = str(value)
                elif key in exec_env:
                    del exec_env[key]

        # Execute the command
        try:
            result = self.command_executor.execute(
                command=command,
                timeout=timeout or self.timeout,
                cwd=cwd or self.project_path,
                env=exec_env,
                check=check,
            )

            # Convert result to dictionary for backward compatibility
            result_dict = {
                "success": result.success,
                "return_code": result.return_code,
                "execution_time": result.execution_time,
                "output": (result.stdout or "") + "\n" + (result.stderr or ""),
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "command": command_str,
            }

            # Log the result
            if result.success:
                logger.info(f"Command succeeded in {result.execution_time:.2f}s")
                self.successful_commands.append(result_dict)
            else:
                logger.error(f"Command failed with code {result.return_code}")
                if result.stderr:
                    logger.error(
                        f"Error output: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}"
                    )
                self.failed_commands.append(result_dict)

            return result_dict

        except Exception as e:
            # Handle any exceptions and return a consistent result dictionary
            error_msg = str(e)
            logger.error(f"Error executing command: {error_msg}")

            result_dict = {
                "success": False,
                "return_code": -1,
                "execution_time": 0.0,
                "output": error_msg,
                "stdout": "",
                "stderr": error_msg,
                "command": command_str,
            }

            self.failed_commands.append(result_dict)
            return result_dict

    def run_in_venv(self, command: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """Run a command in the virtual environment.

        This is a convenience method that ensures the command runs with the
        virtual environment's Python interpreter if available.

        Args:
            command: Command to execute (string or list of arguments)
            **kwargs: Additional arguments to pass to execute_command

        Returns:
            Dictionary with command execution results containing:
                - success: bool - Whether the command succeeded
                - return_code: int - The exit code of the command
                - execution_time: float - Time taken in seconds
                - output: str - Combined stdout and stderr
                - stdout: str - Standard output
                - stderr: str - Standard error
                - command: str - The executed command
        """
        # Ensure command is a list for easier manipulation
        cmd_list = command if isinstance(command, list) else shlex.split(str(command))

        # If we have a virtual environment and the command starts with 'python',
        # use the virtual environment's Python interpreter
        if self.venv_info.get("exists") and self.venv_info.get("python_path"):
            if cmd_list and cmd_list[0] in ("python", "python3"):
                cmd_list[0] = self.venv_info["python_path"]

        # Execute the command with the environment setup
        result = self.execute_command(command=cmd_list, **kwargs)

        # Ensure the result has all expected fields
        if "output" not in result and "stdout" in result and "stderr" in result:
            result["output"] = (
                result.get("stdout", "") + "\n" + result.get("stderr", "")
            ).strip()

        return result

    def create_llm_optimized_todo_md(self) -> None:
        """Generate a TODO.md file with failed commands and fix suggestions.

        This method creates a markdown file with detailed information about
        failed commands to help with debugging and fixing issues.
        """

        def command_to_dict(cmd):
            if hasattr(cmd, "command"):  # It's a Command object
                return {
                    "command": cmd.command,
                    "source": getattr(cmd, "source", ""),
                    "description": getattr(cmd, "description", ""),
                    "error": getattr(cmd, "error", "Unknown error"),
                    "return_code": getattr(cmd, "return_code", -1),
                    "execution_time": getattr(cmd, "execution_time", 0),
                    "metadata": getattr(cmd, "metadata", {}),
                }
            return cmd  # Already a dictionary

        # Convert Command objects to dictionaries for the reporter
        failed_cmds = [command_to_dict(cmd) for cmd in self.failed_commands]
        successful_cmds = [command_to_dict(cmd) for cmd in self.successful_commands]

        # Generate the report
        report_data = {
            "failed_commands": failed_cmds,
            "successful_commands": successful_cmds,
            "project_path": str(self.project_path),
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Write the report
        self.todo_reporter.write_report(report_data)

    def _initialize_parsers(self) -> List[BaseParser]:
        """Initialize all available parsers.

        Returns:
            List of parser instances initialized with the project root
        """
        parser_classes = get_available_parsers()
        parsers = []
        for parser_class in parser_classes:
            try:
                # Initialize each parser with the project root as a Path object
                parser = parser_class(project_root=self.project_path)
                parsers.append(parser)
            except Exception as e:
                logger.warning(
                    f"Failed to initialize parser {parser_class.__name__}: {e}"
                )
        return parsers

    def scan_project(self) -> List[Dict]:
        """Scan the project for commands in various configuration files.

        Returns:
            List of command dictionaries
        """
        logger.debug("Starting project scan in: %s", self.project_path)
        if not self.project_path.exists():
            logger.error("Project path does not exist: %s", self.project_path)
            return []

        commands = []
        logger.debug(
            "Available parsers: %s", [p.__class__.__name__ for p in self.parsers]
        )

        # Find all configuration files
        config_files = self._find_config_files()
        logger.debug("Found %d config files: %s", len(config_files), config_files)

        # Process each file with appropriate parser
        for file_path in config_files:
            try:
                logger.debug("Processing file: %s", file_path)
                parser = self._get_parser_for_file(file_path)
                logger.debug("Found parser for %s: %s", file_path, parser)
                if parser and hasattr(parser, "parse"):
                    logger.debug("Parser has parse method")
                    # Check if parse method accepts a file_path parameter
                    parse_method = parser.parse
                    import inspect

                    sig = inspect.signature(parse_method)

                    try:
                        # Try calling with file_path if the method accepts it
                        if "file_path" in sig.parameters:
                            logger.debug("Calling parse with file_path parameter")
                            file_commands = parser.parse(file_path=file_path)
                        else:
                            logger.debug("Calling parse without parameters")
                            file_commands = parser.parse()

                        if file_commands:
                            logger.debug(
                                "Found %d commands in %s", len(file_commands), file_path
                            )
                            commands.extend(file_commands)
                        else:
                            logger.debug("No commands found in %s", file_path)
                    except Exception as e:
                        logger.error("Error calling parse method: %s", e, exc_info=True)
                        raise
                else:
                    logger.debug("No suitable parser found for %s", file_path)
            except Exception as e:
                logger.error("Error parsing %s: %s", file_path, e, exc_info=True)
                continue

        logger.debug("Total commands found: %d", len(commands))
        return commands

    def _find_config_files(self) -> List[Path]:
        """Find all configuration files in the project.

        Returns:
            List of Path objects to configuration files
        """
        config_files = set()
        logger.debug("Finding config files in: %s", self.project_path)
        logger.debug(
            "Available parsers: %s", [p.__class__.__name__ for p in self.parsers]
        )

        # Get all supported file patterns from parsers
        supported_patterns = set()
        for parser in self.parsers:
            try:
                # Get the patterns safely, handling both properties and attributes
                patterns = []
                if hasattr(parser, "supported_file_patterns"):
                    patterns = parser.supported_file_patterns
                    if callable(patterns):
                        patterns = patterns()  # Call if it's a property

                    # Convert to list if it's not already iterable
                    if isinstance(patterns, (list, tuple, set)):
                        patterns = list(patterns)
                    else:
                        patterns = [str(patterns)]

                    logger.debug(
                        "Parser %s supports patterns: %s",
                        parser.__class__.__name__,
                        patterns,
                    )
                    supported_patterns.update(patterns)
                else:
                    # If no patterns, use a default pattern
                    logger.debug(
                        "No patterns found for parser %s, using default",
                        parser.__class__.__name__,
                    )
                    supported_patterns.add("*")
            except Exception as e:
                logger.warning(
                    f"Failed to get patterns from {parser.__class__.__name__}: {e}",
                    exc_info=True,
                )

        logger.debug("Supported patterns: %s", supported_patterns)

        # Find all matching files in the project
        found_files = set()
        for pattern in supported_patterns:
            try:
                logger.debug("Searching for pattern: %s", pattern)
                for file_path in self.project_path.rglob(pattern):
                    if self._should_process_file(file_path):
                        resolved = file_path.resolve()
                        found_files.add(resolved)
                        logger.debug("Found file: %s", resolved)
            except Exception as e:
                logger.warning("Error searching for pattern %s: %s", pattern, e)

        logger.debug("Found %d config files: %s", len(found_files), found_files)
        return list(found_files)

    def _get_parser_for_file(self, file_path: Path) -> Optional[BaseParser]:
        """Get the appropriate parser for a file.

        Args:
            file_path: Path to the file to parse

        Returns:
            Parser instance or None if no suitable parser found
        """
        logger.debug("Finding parser for file: %s", file_path)
        logger.debug(
            "Available parsers: %s", [p.__class__.__name__ for p in self.parsers]
        )

        for parser in self.parsers:
            try:
                logger.debug("Trying parser: %s", parser.__class__.__name__)
                can_parse = parser.can_parse(file_path)
                logger.debug(
                    "Parser %s can_parse(%s): %s",
                    parser.__class__.__name__,
                    file_path.name,
                    can_parse,
                )

                if can_parse:
                    # For mock parsers or already initialized parsers, return them directly
                    is_mock = hasattr(parser, "_is_mock") or hasattr(
                        parser, "_mock_return_value"
                    )
                    has_file_path = hasattr(parser, "file_path")

                    logger.debug(
                        "  is_mock: %s, has_file_path: %s", is_mock, has_file_path
                    )

                    if is_mock or has_file_path:
                        logger.debug(
                            "Using existing parser: %s (is_mock=%s, has_file_path=%s)",
                            parser,
                            is_mock,
                            has_file_path,
                        )
                        # Update the file path on the parser
                        parser.file_path = file_path
                        if (
                            not hasattr(parser, "project_path")
                            or parser.project_path is None
                        ):
                            parser.project_path = self.project_path
                        return parser
                    # For real parsers that haven't been initialized yet, create a new instance with the file path
                    logger.debug("Creating new parser instance for: %s", file_path)
                    # Try both initialization styles for compatibility
                    try:
                        return parser.__class__(
                            file_path=file_path, project_path=self.project_path
                        )
                    except Exception as e:
                        logger.debug(
                            "Failed to initialize with kwargs, trying positional args: %s",
                            e,
                        )
                        return parser.__class__(file_path, self.project_path)

            except Exception as e:
                logger.warning(
                    f"Error checking if parser {parser.__class__.__name__} can parse {file_path}: {e}",
                    exc_info=True,
                )

        logger.debug("No suitable parser found for: %s", file_path)
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

    def test_commands(self, commands: List) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        self.failed_commands = []
        self.successful_commands = []
        self.ignored_commands = []

        for cmd in commands:
            if self._should_ignore_command(cmd):
                self.ignored_commands.append(cmd)
                continue

            # Make a copy of the command to avoid modifying the original
            if hasattr(cmd, "command"):  # It's a Command object
                # Create a dictionary representation
                cmd_dict = {
                    "command": cmd.command,
                    "type": getattr(cmd, "type", ""),
                    "description": getattr(cmd, "description", ""),
                    "source": getattr(cmd, "source", ""),
                    "metadata": getattr(cmd, "metadata", {}),
                }
            else:  # It's a dictionary
                cmd_dict = cmd.copy()

            # Execute the command
            is_success = self._execute_command(cmd_dict)

            # Add to appropriate list based on execution result
            if is_success:
                self.successful_commands.append(cmd_dict)
            else:
                # Ensure these fields exist in the dict
                if "return_code" not in cmd_dict:
                    cmd_dict["return_code"] = -1
                if "error" not in cmd_dict:
                    cmd_dict["error"] = "Unknown error"
                self.failed_commands.append(cmd_dict)

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

    def _execute_command(self, cmd_info) -> bool:
        """Execute a single command and update the command info with results.

        Args:
            cmd_info: Either a Command object or a dictionary containing command information

        Returns:
            bool: True if command executed successfully, False otherwise
        """
        if hasattr(cmd_info, "command"):  # It's a Command object
            command = cmd_info.command
            cwd = getattr(cmd_info, "cwd", self.project_path)
            timeout = getattr(cmd_info, "timeout", self.timeout)
        else:  # It's a dictionary
            command = cmd_info.get("command", "")
            cwd = str(cmd_info.get("cwd", self.project_path))
            timeout = cmd_info.get("timeout", self.timeout)

        logger.info("Executing command: %s", command)

        try:
            # Execute the command through the command executor
            result = self.command_executor.execute(
                command=command, timeout=timeout, cwd=cwd, env=cmd_info.get("env")
            )

            # Update command info with results
            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "execution_time", result.execution_time)
                setattr(cmd_info, "stdout", result.stdout)
                setattr(cmd_info, "stderr", result.stderr)
                setattr(cmd_info, "return_code", result.return_code)
                if not result.success:
                    setattr(cmd_info, "error", result.stderr or "Command failed")
            else:  # Dictionary
                cmd_info.update(
                    {
                        "execution_time": result.execution_time,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.return_code,
                        "success": result.success,
                    }
                )
                if not result.success:
                    cmd_info["error"] = result.stderr or "Command failed"

            return result.success

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {e.timeout} seconds"
            logger.error(error_msg)

            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "error", error_msg)
                setattr(cmd_info, "return_code", -1)
            else:  # Dictionary
                cmd_info.update(
                    {"error": error_msg, "return_code": -1, "success": False}
                )
            return False

        except Exception as e:
            error_msg = str(e)
            logger.error("Error executing command '%s': %s", command, error_msg)

            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "error", str(e))
            else:  # Dictionary
                cmd_info["error"] = str(e)
            return False

    def _should_ignore_command(self, cmd) -> bool:
        """Check if a command should be ignored based on ignore rules.

        Args:
            cmd: Either a Command object or a dictionary containing command information

        Returns:
            bool: True if command should be ignored
        """
        # Convert Command object to dict if needed
        if hasattr(cmd, "to_dict"):
            cmd_dict = cmd.to_dict()
        else:
            cmd_dict = cmd

        # Check ignore patterns
        command_str = cmd_dict.get("command", "")
        for pattern in self.ignore_patterns:
            if self._match_pattern(command_str, pattern):
                return True

        return False

    # The execute_command method is defined above with full functionality
