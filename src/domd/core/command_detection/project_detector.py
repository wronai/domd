"""Project command detector implementation."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .base_detector import CommandDetector
from .handlers import CommandHandler, ConfigFileHandler
from .models import Command
from .parsers import ParserRegistry

logger = logging.getLogger(__name__)


class ProjectCommandDetector(CommandDetector):
    """Detects and manages commands in project files with support for subdirectories."""

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
        super().__init__(
            project_path=project_path,
            timeout=timeout,
            exclude_patterns=exclude_patterns,
            include_patterns=include_patterns,
            todo_file=todo_file,
            done_file=done_file,
            script_file=script_file,
            ignore_file=ignore_file,
            venv_path=venv_path,
        )

        # Initialize project-specific components
        self._initialize_project_components()

    def _initialize_project_components(self) -> None:
        """Initialize project-specific components."""
        # Initialize parser registry and discover parsers
        self.parser_registry = ParserRegistry()
        self._discover_parsers()

        # Initialize handlers
        self.config_handler = ConfigFileHandler(
            project_path=self.project_path,
            exclude_patterns=self.exclude_patterns,
            include_patterns=self.include_patterns,
            ignore_file=self.ignore_file,
        )

        # Initialize command handler
        self.command_handler = CommandHandler(
            project_path=self.project_path,
            command_runner=self.command_runner,
            timeout=self.timeout,
            ignore_patterns=self.ignore_patterns,
        )

        # Update command storage references
        self._update_command_storage()

    def _discover_parsers(self) -> None:
        """Discover and register parsers."""
        try:
            # Try to discover parsers from the default location
            self.parser_registry.discover_parsers()

            # If no parsers found, try legacy import
            if not self.parser_registry.get_parsers():
                self._import_legacy_parsers()
        except Exception as e:
            logger.warning(f"Failed to discover parsers: {e}")
            self._import_legacy_parsers()

    def _import_legacy_parsers(self) -> None:
        """Import parsers using the legacy method."""
        try:
            from domd.parsers import get_all_parsers

            parser_classes = get_all_parsers()
            for parser_class in parser_classes:
                self.parser_registry.register(parser_class)
            logger.info(f"Imported {len(parser_classes)} legacy parsers")
        except ImportError as e:
            logger.warning(f"Failed to import legacy parsers: {e}")

    def scan_project(self) -> List[Command]:
        """Scan the project for commands in configuration files.

        Scans both the root directory and subdirectories (up to 2 levels deep)
        for README.md files and processes commands in their respective contexts.

        Returns:
            List of Command objects
        """
        logger.info(f"Scanning project: {self.project_path}")
        all_commands = []

        # 1. Scan root directory for configuration files
        config_files = self.config_handler.find_config_files(self.parsers)
        logger.info(f"Found {len(config_files)} configuration files in root directory")

        # Process root directory files
        for file_path in config_files:
            all_commands.extend(self._process_file_commands(file_path))

        # 2. Scan first and second level subdirectories for README.md files
        self._scan_subdirectories(all_commands)

        logger.info(f"Found {len(all_commands)} commands in total")
        return self._convert_to_command_objects(all_commands)

    def _scan_subdirectories(self, all_commands: List[Command]) -> None:
        """Scan subdirectories for README.md files and process commands.

        Args:
            all_commands: List to append found commands to
        """
        try:
            logger.debug(f"Starting directory scan in: {self.project_path}")

            # First level directories
            for level1_item in sorted(self.project_path.iterdir()):
                if not level1_item.is_dir() or level1_item.name.startswith("."):
                    continue

                logger.info(f"Processing first level directory: {level1_item.name}")

                # Process level 1 README
                self._process_directory_readme(level1_item, all_commands)

                # Second level directories
                for level2_item in sorted(level1_item.iterdir()):
                    if not level2_item.is_dir() or level2_item.name.startswith("."):
                        continue

                    logger.info(
                        f"  Processing second level directory: {level1_item.name}/{level2_item.name}"
                    )
                    # Process level 2 README
                    self._process_directory_readme(
                        level2_item, all_commands, level1_item.name
                    )

        except Exception as e:
            logger.error(f"Error scanning directories: {e}", exc_info=True)

    def _process_directory_readme(
        self,
        directory: Path,
        all_commands: List[Command],
        parent_dir: Optional[str] = None,
    ) -> None:
        """Process a README.md file in a directory.

        Args:
            directory: Directory containing the README.md
            all_commands: List to append found commands to
            parent_dir: Name of parent directory (for second-level directories)
        """
        readme_path = directory / "README.md"
        if not readme_path.exists() or not readme_path.is_file():
            return

        # Determine display path for logging and source
        if parent_dir:
            display_path = f"{parent_dir}/{directory.name}/README.md"
        else:
            display_path = f"{directory.name}/README.md"

        logger.info(f"Found README.md: {display_path}")

        # Process README.md in directory
        commands = self._process_file_commands(readme_path)

        # Update command metadata with directory context
        for cmd in commands:
            if isinstance(cmd, dict):
                cmd_metadata = cmd.setdefault("metadata", {})
                cmd_metadata["cwd"] = str(directory)
                cmd_metadata["source"] = display_path
            elif hasattr(cmd, "metadata"):
                if not hasattr(cmd.metadata, "get") or not callable(cmd.metadata.get):
                    cmd.metadata = {"original_metadata": cmd.metadata}
                cmd.metadata["cwd"] = str(directory)
                if not getattr(cmd, "source", None):
                    cmd.source = display_path

        all_commands.extend(commands)
        logger.info(f"Found {len(commands)} commands in {display_path}")

    def _process_file_commands(self, file_path: Path) -> List[Dict]:
        """Process a single file and extract commands.

        Args:
            file_path: Path to the file to process

        Returns:
            List of command dictionaries with metadata
        """
        logger.debug(f"Processing file: {file_path}")
        commands = []

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return commands

        try:
            # Get the appropriate parser for the file
            parser = self.parser_registry.get_parser_for_file(file_path)
            if not parser:
                logger.debug(f"No parser found for file: {file_path}")
                return commands

            # Set the file_path on the parser if it has that attribute
            if hasattr(parser, "file_path"):
                parser.file_path = str(file_path)

            # Parse commands from file
            file_commands = []
            if hasattr(parser, "parse_file") and callable(parser.parse_file):
                file_commands = parser.parse_file(str(file_path))
            elif hasattr(parser, "parse") and callable(parser.parse):
                # Try different calling conventions
                try:
                    file_commands = parser.parse()
                except (TypeError, AttributeError):
                    try:
                        file_commands = parser.parse(str(file_path))
                    except (TypeError, AttributeError):
                        try:
                            content = file_path.read_text(encoding="utf-8")
                            file_commands = parser.parse(content)
                        except Exception as e:
                            logger.error(f"Error parsing {file_path} with content: {e}")
                            return []

            # Add file path to commands if not already present
            for cmd in file_commands:
                if isinstance(cmd, dict):
                    cmd["file"] = str(file_path)
                    if "source" not in cmd:
                        cmd["source"] = str(file_path.relative_to(self.project_path))
                elif hasattr(cmd, "file") and not cmd.file:
                    cmd.file = str(file_path)
                    if not hasattr(cmd, "source") or not cmd.source:
                        cmd.source = str(file_path.relative_to(self.project_path))

            commands.extend(file_commands)
            logger.debug(f"Found {len(file_commands)} commands in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)

        return commands

    def _convert_to_command_objects(self, commands: List[Any]) -> List[Command]:
        """Convert command dictionaries to Command objects.

        Args:
            commands: List of command dictionaries or Command objects

        Returns:
            List of Command objects
        """
        result_commands = []

        for cmd in commands:
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
                # Already a Command object or similar
                result_commands.append(cmd)

        return result_commands

    def _update_command_storage(self) -> None:
        """Update references to command storage lists."""
        if hasattr(self, "command_handler"):
            self.failed_commands = self.command_handler.failed_commands
            self.successful_commands = self.command_handler.successful_commands
            self.ignored_commands = self.command_handler.ignored_commands
