"""Project command detector for finding and executing commands in project files."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.command_execution import CommandExecutor, CommandRunner
from domd.core.commands import Command
from domd.core.project_detection.command_handling import CommandHandler
from domd.core.project_detection.config_files import ConfigFileHandler
from domd.core.project_detection.virtualenv import (
    get_virtualenv_environment,
    get_virtualenv_info,
)
from domd.parsing import FileProcessor, ParserRegistry, PatternMatcher
from domd.parsing.base import BaseParser
from domd.reporting import MarkdownFormatter, Reporter

logger = logging.getLogger(__name__)


class ProjectCommandDetector:
    """Detects and executes commands in project configuration files."""

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
        """Initialize the project command detector.

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
        # Store ignore_file as a Path object relative to project_path
        self.ignore_file = self.project_path / Path(ignore_file)

        # Initialize virtual environment
        self.venv_path = venv_path
        self.venv_info = get_virtualenv_info(venv_path or self.project_path)

        # Command ignore patterns (separate from file exclude patterns)
        self.ignore_patterns = []

        # Initialize components
        self.command_executor = CommandExecutor(timeout=timeout)
        self.command_runner = CommandRunner(
            executor=self.command_executor,
        )
        self.reporter = Reporter(
            output_dir=self.project_path,
            formatters={
                "todo": MarkdownFormatter(title="TODO Commands"),
                "done": MarkdownFormatter(title="DONE Commands"),
            },
        )
        self.parser_registry = ParserRegistry()
        self.file_processor = FileProcessor(project_root=self.project_path)
        self.pattern_matcher = PatternMatcher()

        # Initialize handlers
        self.config_handler = ConfigFileHandler(
            project_path=self.project_path,
            exclude_patterns=self.exclude_patterns,
            include_patterns=self.include_patterns,
            ignore_file=self.ignore_file,
        )
        self.command_handler = CommandHandler(
            project_path=self.project_path,
            command_runner=self.command_runner,
            timeout=self.timeout,
            ignore_patterns=self.ignore_patterns,
        )

        # Initialize parsers
        self.parsers = self._initialize_parsers()

        # Command storage (references to command_handler storage)
        self.failed_commands = self.command_handler.failed_commands
        self.successful_commands = self.command_handler.successful_commands
        self.ignored_commands = self.command_handler.ignored_commands

        # Add ignore_parser attribute for backward compatibility
        self.ignore_parser = self

    def _initialize_parsers(self) -> List[BaseParser]:
        """Initialize parsers for detecting commands in configuration files.

        Returns:
            List of parser instances
        """
        logger.debug("Starting parser initialization...")

        # Discover parsers from the domd.core.parsers package
        try:
            logger.debug("Discovering parsers from domd.core.parsers...")
            self.parser_registry.discover_parsers("domd.core.parsers")
            logger.debug("Parser discovery completed")
        except Exception as e:
            logger.error(f"Failed to discover parsers: {e}", exc_info=True)

        # Get all parsers from the registry
        parsers = self.parser_registry.get_all_parsers()
        logger.debug(f"Found {len(parsers)} parsers in registry")

        # Log the names of the parsers found
        if parsers:
            logger.debug(
                f"Parser classes found: {[p.__class__.__name__ for p in parsers]}"
            )
        else:
            logger.warning("No parsers found in registry, using legacy parsers")

            # Fallback to legacy parsers if needed
            try:
                logger.debug("Attempting to use legacy parser import...")
                from domd.parsers import get_all_parsers

                parser_classes = get_all_parsers()
                logger.debug(f"Found {len(parser_classes)} legacy parser classes")

                # Create parser instances instead of using classes directly
                parsers = []
                for parser_class in parser_classes:
                    try:
                        # Create parser instance
                        parser_instance = parser_class()
                        parsers.append(parser_instance)
                        logger.debug(f"Initialized parser: {parser_class.__name__}")
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize parser {parser_class.__name__}: {e}",
                            exc_info=True,
                        )
            except ImportError as e:
                logger.error(f"Failed to import legacy parsers: {e}", exc_info=True)
                parsers = []

        logger.info(f"Initialized {len(parsers)} parsers")
        return parsers

    def _should_process_file(self, file_path: Union[str, Path]) -> bool:
        """Check if a file should be processed based on include/exclude patterns.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file should be processed, False otherwise
        """
        # Convert to Path and make relative to project path
        path = Path(file_path)
        try:
            rel_path = path.relative_to(self.project_path)
        except ValueError:
            # File is outside project path
            return False

        # Check if file is in an excluded directory
        for part in rel_path.parts:
            if part.startswith(".") or part in (
                "node_modules",
                "venv",
                ".venv",
                "env",
                "__pycache__",
            ):
                return False

        # If include patterns are specified, file must match at least one
        if self.include_patterns:
            for pattern in self.include_patterns:
                if self.pattern_matcher.match_file(str(rel_path), {pattern}):
                    return True
            return False

        # If exclude patterns are specified, file must not match any
        for pattern in self.exclude_patterns:
            if self.pattern_matcher.match_file(str(rel_path), {pattern}):
                return False

        return True

    def _get_environment(self) -> Dict[str, str]:
        """Get environment variables for command execution.

        Returns:
            Dictionary with environment variables
        """
        return get_virtualenv_environment(self.venv_info)

    def scan_project(self) -> List[Command]:
        """Scan the project for commands in configuration files.

        Returns:
            List of Command objects
        """
        logger.info(f"Scanning project: {self.project_path}")

        # Find configuration files
        config_files = self.config_handler.find_config_files(self.parsers)
        logger.info(f"Found {len(config_files)} configuration files")

        # Parse files and collect commands
        all_commands = []

        for file_path in config_files:
            try:
                # Try to get parser from registry first
                parser = self.parser_registry.get_parser_for_file(file_path)

                # If no parser found in registry, try legacy method
                if not parser:
                    parser = self._get_parser_for_file(file_path)

                if not parser:
                    logger.warning(f"No parser found for {file_path}")
                    continue

                logger.debug(f"Parsing {file_path} with {parser.__class__.__name__}")

                # Odczytaj zawartość pliku
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue

                # Set the file_path on the parser if it has that attribute
                if hasattr(parser, "file_path"):
                    parser.file_path = file_path

                # Try different ways to call the parse method
                try:
                    import inspect

                    sig = inspect.signature(parser.parse)

                    if "file_path" in sig.parameters and "content" in sig.parameters:
                        commands = parser.parse(content=content, file_path=file_path)
                    elif "content" in sig.parameters:
                        commands = parser.parse(content=content)
                    elif "file_path" in sig.parameters:
                        commands = parser.parse(file_path=file_path)
                    else:
                        # Last resort - try passing content as the first argument
                        commands = parser.parse(content)

                    # Add file path to commands if not already present
                    for cmd in commands:
                        if isinstance(cmd, dict) and "file" not in cmd:
                            cmd["file"] = str(file_path)
                        elif hasattr(cmd, "file") and not cmd.file:
                            cmd.file = str(file_path)

                    all_commands.extend(commands)
                    logger.debug(f"Found {len(commands)} commands in {file_path}")

                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}", exc_info=True)
                    continue
            except Exception as e:
                logger.error(
                    f"Unexpected error processing {file_path}: {e}", exc_info=True
                )
                continue

        logger.info(f"Found {len(all_commands)} commands in total")

        # Konwertuj wszystkie słowniki na obiekty Command
        result_commands = []
        for cmd in all_commands:
            if isinstance(cmd, dict):
                command = Command(
                    command=cmd.get("command", ""),
                    type=cmd.get("type", ""),
                    description=cmd.get("description", ""),
                    source=cmd.get("source", ""),
                    file=cmd.get("file", ""),
                    metadata=cmd.get("metadata", {}),
                )
                result_commands.append(command)
            else:
                # Już jest obiektem Command lub podobnym
                result_commands.append(cmd)

        return result_commands

    def _get_parser_for_file(self, file_path: Path) -> Optional[BaseParser]:
        """Get a parser for a specific file (legacy method).

        Args:
            file_path: Path to the file

        Returns:
            Parser instance or None if no parser found
        """
        for parser in self.parsers:
            try:
                if hasattr(parser, "can_parse") and parser.can_parse(file_path):
                    return parser
            except Exception as e:
                logger.warning(
                    f"Error checking parser {parser.__class__.__name__}: {e}"
                )

        return None

    def test_commands(self, commands: List) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        # Clear any previous command results
        self.command_handler.failed_commands = []
        self.command_handler.successful_commands = []
        self.command_handler.ignored_commands = []

        # Test the commands using the command handler
        self.command_handler.test_commands(commands)

        # Ensure our references are up to date
        self.failed_commands = self.command_handler.failed_commands
        self.successful_commands = self.command_handler.successful_commands
        self.ignored_commands = self.command_handler.ignored_commands

        logger.info(
            f"Command test results - "
            f"Failed: {len(self.failed_commands)}, "
            f"Successful: {len(self.successful_commands)}, "
            f"Ignored: {len(self.ignored_commands)}"
        )

    def execute_command(self, command, **kwargs) -> Dict[str, Any]:
        """Execute a command with proper environment setup.

        Args:
            command: Command to execute (string or list of args)
            **kwargs: Additional arguments to pass to command_handler

        Returns:
            Dictionary with command execution results
        """
        return self.command_handler.execute_command(command, **kwargs)

    def run_in_venv(self, command, **kwargs) -> Dict[str, Any]:
        """Run a command in the virtual environment.

        Args:
            command: Command to execute (string or list of args)
            **kwargs: Additional arguments to pass to command_handler

        Returns:
            Dictionary with command execution results
        """
        # Get environment variables for virtualenv
        venv_env = self._get_environment()

        # Pass the environment to command_handler.run_in_venv
        return self.command_handler.run_in_venv(command, venv_env=venv_env, **kwargs)

    def _execute_command(self, command_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command with the given information.

        This is a backward compatibility method for tests.

        Args:
            command_info: Dictionary with command information
                - command: Command to execute
                - cwd: Working directory
                - env: Environment variables
                - timeout: Timeout in seconds

        Returns:
            Dictionary with command execution results
        """
        command = command_info.get("command")
        cwd = command_info.get("cwd", self.project_path)
        env = command_info.get("env")
        timeout = command_info.get("timeout", self.timeout)

        # Use the command handler to execute the command
        return self.command_handler.execute_command(
            command=command, cwd=cwd, env=env, timeout=timeout
        )

    def _find_config_files(self) -> List[Path]:
        """Find configuration files in the project.

        This is a backward compatibility method for tests.

        Returns:
            List of configuration file paths
        """
        # Initialize parsers if not already done
        if not hasattr(self, "parsers") or not self.parsers:
            self.parsers = self._initialize_parsers()

        # Use the config handler to find configuration files
        return self.config_handler.find_config_files(self.parsers)

    def generate_reports(self) -> Dict[str, Path]:
        """Generate reports for successful and failed commands.

        Returns:
            Dictionary with report file paths
        """
        logger.info("Generating reports")

        # Konwertuj obiekty Command na słowniki
        failed_commands_dicts = []
        for cmd in self.failed_commands:
            if hasattr(cmd, "to_dict"):
                # Jeśli to obiekt Command, użyj metody to_dict
                cmd_dict = cmd.to_dict()
                # Dodaj dodatkowe pola wymagane przez formater bezpośrednio z atrybutów
                if hasattr(cmd, "return_code"):
                    cmd_dict["return_code"] = getattr(cmd, "return_code")
                elif hasattr(cmd, "metadata") and isinstance(cmd.metadata, dict):
                    cmd_dict["return_code"] = cmd.metadata.get("return_code", -1)
                else:
                    cmd_dict["return_code"] = -1

                if hasattr(cmd, "error"):
                    cmd_dict["error"] = getattr(cmd, "error")
                elif hasattr(cmd, "metadata") and isinstance(cmd.metadata, dict):
                    cmd_dict["error"] = cmd.metadata.get("error", "")
                else:
                    cmd_dict["error"] = ""

                if hasattr(cmd, "execution_time"):
                    cmd_dict["execution_time"] = getattr(cmd, "execution_time")
                elif hasattr(cmd, "metadata") and isinstance(cmd.metadata, dict):
                    cmd_dict["execution_time"] = cmd.metadata.get("execution_time", 0)
                else:
                    cmd_dict["execution_time"] = 0

                if hasattr(cmd, "success"):
                    cmd_dict["success"] = getattr(cmd, "success")

                if hasattr(cmd, "stdout"):
                    cmd_dict["stdout"] = getattr(cmd, "stdout")

                if hasattr(cmd, "stderr"):
                    cmd_dict["stderr"] = getattr(cmd, "stderr")

                failed_commands_dicts.append(cmd_dict)
            elif isinstance(cmd, dict):
                # Jeśli to już słownik, użyj go bezpośrednio
                failed_commands_dicts.append(cmd)

        successful_commands_dicts = []
        for cmd in self.successful_commands:
            if hasattr(cmd, "to_dict"):
                cmd_dict = cmd.to_dict()
                # Dodaj dodatkowe pola wymagane przez formater bezpośrednio z atrybutów
                if hasattr(cmd, "execution_time"):
                    cmd_dict["execution_time"] = getattr(cmd, "execution_time")
                elif hasattr(cmd, "metadata") and isinstance(cmd.metadata, dict):
                    cmd_dict["execution_time"] = cmd.metadata.get("execution_time", 0)
                else:
                    cmd_dict["execution_time"] = 0

                if hasattr(cmd, "success"):
                    cmd_dict["success"] = getattr(cmd, "success")

                if hasattr(cmd, "stdout"):
                    cmd_dict["stdout"] = getattr(cmd, "stdout")

                successful_commands_dicts.append(cmd_dict)
            elif isinstance(cmd, dict):
                # Jeśli to już słownik, użyj go bezpośrednio
                successful_commands_dicts.append(cmd)

        # Przygotuj dane dla raportów
        failed_data = {
            "commands": failed_commands_dicts,
            "failed_commands": failed_commands_dicts,
            "successful_commands": [],
            "ignored_commands": [],
        }

        successful_data = {
            "commands": successful_commands_dicts,
            "failed_commands": [],
            "successful_commands": successful_commands_dicts,
            "ignored_commands": [],
        }

        # Użyj formatera bezpośrednio
        todo_formatter = self.reporter._formatter_instances.get("todo")
        if not todo_formatter:
            # Jeśli nie ma instancji formatera, utwórz nową
            todo_formatter = MarkdownFormatter(title="TODO Commands")

        # Sformatuj dane i zapisz do pliku
        todo_content = todo_formatter.format_report(failed_data)
        self.todo_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.todo_file, "w", encoding="utf-8") as f:
            f.write(todo_content)

        # To samo dla raportu DONE
        done_formatter = self.reporter._formatter_instances.get("done")
        if not done_formatter:
            done_formatter = MarkdownFormatter(title="DONE Commands")

        done_content = done_formatter.format_report(successful_data)
        self.done_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.done_file, "w", encoding="utf-8") as f:
            f.write(done_content)

        # Generate shell script if needed
        if self.script_file:
            self._generate_shell_script()

        return {
            "todo": self.todo_file,
            "done": self.done_file,
            "script": self.script_file if self.script_file else None,
        }

    def _generate_shell_script(self) -> None:
        """Generate a shell script to fix failed commands."""
        logger.info(f"Generating shell script: {self.script_file}")

        script_lines = [
            "#!/bin/bash",
            "# Auto-generated script to fix failed commands",
            "# Generated by domd",
            "",
            "set -e",
            "",
        ]

        for cmd in self.failed_commands:
            if isinstance(cmd, dict):
                command = cmd.get("command", "")
            else:
                command = getattr(cmd, "command", "")

            if command:
                script_lines.append(f"echo 'Running: {command}'")
                script_lines.append(command)
                script_lines.append("")

        with open(self.script_file, "w") as f:
            f.write("\n".join(script_lines))

        # Make script executable
        try:
            import os

            os.chmod(self.script_file, 0o755)
        except Exception as e:
            logger.warning(f"Could not make script executable: {e}")

    def create_llm_optimized_todo_md(self) -> None:
        """Generate a TODO.md file with failed commands and fix suggestions."""
        try:
            # Create the TODO.md file with a header
            with open(self.todo_file, "w", encoding="utf-8") as f:
                f.write("# 🤖 TODO - LLM Task List for Command Fixes\n\n")
                f.write("## ❌ Failed Commands\n\n")

                # Add failed commands to the TODO.md file
                if self.failed_commands:
                    for cmd in self.failed_commands:
                        # Handle both dictionary and object formats
                        cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__

                        # Skip if command or error is missing
                        if not cmd_dict.get("command") or not cmd_dict.get("error"):
                            continue

                        command = cmd_dict["command"]
                        error = cmd_dict["error"]
                        source = cmd_dict.get("source", "Unknown")

                        f.write(f"### 🔧 Fix: {command}\n")  # noqa: E231
                        f.write(f"- [ ] **Command**: `{command}`  \n")  # noqa: E231
                        f.write(f"- **Error**: {error}  \n")  # noqa: E231
                        f.write(f"- **Source**: `{source}`\n")  # noqa: E231
                        f.write("- **Fix Suggestion**: \n\n")  # noqa: E231
                        f.write(
                            "  ```bash\n  # Suggested fix\n  # Replace with the correct command\n  ```\n\n"
                        )
                else:
                    f.write("No failed commands found. 🎉\n\n")

                # Add a section for successful commands
                f.write("---\n\n")
                f.write("## ✅ Successful Commands\n\n")
                if self.successful_commands:
                    for cmd in self.successful_commands:
                        # Handle both dictionary and object formats
                        cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__

                        # Skip if command is missing
                        if not cmd_dict.get("command"):
                            continue

                        command = cmd_dict["command"]
                        source = cmd_dict.get("source", "Unknown")

                        f.write(f"- [x] `{command}`  \n")  # noqa: E231
                        f.write(f"  - Source: `{source}`\n")  # noqa: E231
                else:
                    f.write("No commands were executed successfully.\n")

                # Add footer
                f.write("\n---\n")
                f.write("Generated by [DOMD](https://github.com/wronai/domd)")

            logger.info(f"Created TODO.md file at {self.todo_file}")
        except Exception as e:
            logger.error(f"Failed to create TODO.md file: {e}")
            raise

    def scan_and_initialize(self) -> List[Dict[str, Any]]:
        """Scan the project, test commands, and generate reports.

        This method combines functionality from scan_project, test_commands, and generate_reports
        for backward compatibility with the CLI interface.

        Returns:
            List of command dictionaries
        """
        logger.info("Starting scan_and_initialize")

        # Step 1: Scan the project for commands
        commands = self.scan_project()

        # Step 2: Load ignore patterns from .doignore file
        self._load_ignore_patterns()

        # Step 3: Test the commands
        self.test_commands(commands)

        # Step 4: Generate reports
        self.generate_reports()

        return commands

    def _load_ignore_patterns(self) -> None:
        """Load ignore patterns from .doignore file."""
        if not self.ignore_file.exists():
            logger.debug(f"Ignore file not found: {self.ignore_file}")
            return

        try:
            with open(self.ignore_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            patterns = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)

            self.ignore_patterns = patterns
            self.command_handler.ignore_patterns = patterns
            logger.info(
                f"Loaded {len(patterns)} ignore patterns from {self.ignore_file}"
            )
        except Exception as e:
            logger.error(f"Error loading ignore patterns: {e}")

    def should_ignore_command(self, command):
        """Check if a command should be ignored based on ignore patterns.

        Args:
            command: Command string to check

        Returns:
            True if the command should be ignored, False otherwise
        """
        return self.command_handler.should_ignore_command({"command": command})

    def get_ignore_reason(self, command):
        """Get the reason why a command is ignored.

        Args:
            command: Command string to check

        Returns:
            Reason string or None if not ignored
        """
        # For now, we just return a generic reason
        if self.should_ignore_command(command):
            return "Matched ignore pattern in .doignore file"
        return None

    @property
    def ignore_file_path(self):
        """Get the path to the ignore file.

        Returns:
            Path object for the ignore file
        """
        return self.ignore_file

    def generate_doignore_template(self):
        """Generate a template .doignore file.

        Returns:
            True if the file was created, False otherwise
        """
        try:
            # Create parent directories if they don't exist
            self.ignore_file.parent.mkdir(parents=True, exist_ok=True)

            # Don't overwrite existing file
            if self.ignore_file.exists():
                logger.info(f"Ignore file already exists: {self.ignore_file}")
                return True

            # Default ignore patterns
            default_patterns = [
                "# TodoMD Ignore File (.doignore)",
                "# Lines starting with # are comments",
                "# Each line is a pattern to ignore commands",
                "# Examples:",
                "# make test-integration  # Ignore specific command",
                "# make test-*            # Ignore commands matching wildcard",
                "# *ansible*              # Ignore commands containing 'ansible'",
                "",
                "# Common patterns to ignore",
                "make clean",
                "make clean-*",
                "make *-clean",
                "make docs-*",
                "make serve-*",
                "make publish*",
                "make release-*",
                "make bump-*",
                "make tag",
                "make git-*",
                "make deps-update",
                "make watch-*",
                "# Add your custom ignore patterns below",
                "",
            ]

            # Write the template
            with open(self.ignore_file, "w", encoding="utf-8") as f:
                f.write("\n".join(default_patterns))

            logger.info(f"Created ignore file template: {self.ignore_file}")
            return True
        except Exception as e:
            logger.error(f"Error creating ignore file template: {e}")
            return False
