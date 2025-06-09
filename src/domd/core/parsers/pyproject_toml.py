"""Parser for pyproject.toml files."""

import logging
from typing import Any, Dict, List

from ..commands.command import Command
from .base import BaseParser

logger = logging.getLogger(__name__)

# Try to import tomli (Python 3.11+) or toml (older Python)
try:
    import tomli as toml  # noqa: F401

    TOML_AVAILABLE = True
except ImportError:
    try:
        import toml  # noqa: F401, F811

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False
        logger.warning(
            "Neither tomli nor toml package is available. PyProjectTomlParser will not work."
        )


class PyProjectTomlParser(BaseParser):
    """Parser for pyproject.toml files to extract Python project commands.

    This parser extracts commands from the [tool.poetry.scripts] section of pyproject.toml files.
    It handles both simple commands and combined commands (using '&&' to chain commands).

    For combined commands (e.g., "black . && isort . && flake8"), the parser will:
    1. Create a single command for the entire combined command
    2. Create individual commands for each part of the combined command

    Each command is wrapped with 'poetry run' to ensure it runs in the correct environment.
    """

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for pyproject.toml."""
        return ["pyproject.toml"]

    def parse(self, content: str = None) -> List[Command]:
        """Parse pyproject.toml and extract project commands.

        Args:
            content: Optional content of the file to parse. If not provided, will read from file_path.

        Returns:
            List of Command objects
        """
        logger.debug(f"Starting to parse {self.file_path}")

        if not TOML_AVAILABLE:
            logger.error("No TOML parser available. Install 'tomli' or 'toml' package.")
            return []

        if content is None and (not self.file_path or not self.file_path.exists()):
            logger.error(f"File not found and no content provided: {self.file_path}")
            return []

        from domd.core.commands import Command

        self._commands: List[Command] = []

        try:
            # If content is not provided, read from file
            if content is None:
                logger.debug(f"Reading content from {self.file_path}")
                content = self.file_path.read_text(encoding="utf-8")
            else:
                logger.debug("Using provided content for parsing")

            # Try to load with the available TOML library
            if "tomli" in globals():
                import tomli as toml_lib

                logger.debug("Using tomli for TOML parsing")
            else:
                import toml as toml_lib

                logger.debug("Using toml for TOML parsing")

            if hasattr(toml_lib, "loads"):
                data = toml_lib.loads(content)
            else:
                # Fallback for older versions of toml
                data = toml_lib.loads(content)

            logger.debug(
                f"Successfully parsed TOML data: {data.keys() if data else 'empty'}"
            )

            # Extract Poetry scripts
            self._extract_poetry_scripts(data)

            # Extract test commands
            self._extract_test_commands(data)
            # Extract build commands
            self._extract_build_commands(data)

            logger.debug(
                f"Extracted {len(self._commands)} commands from {self.file_path}"
            )

        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}", exc_info=True)
            return []

        return self._commands

    def _extract_poetry_scripts(self, data: Dict[str, Any]) -> None:
        """Extract Poetry scripts section."""
        from domd.core.commands import Command

        try:
            logger.debug("Extracting Poetry scripts...")
            tool_data = data.get("tool", {})
            logger.debug(f"Tool data: {tool_data.keys() if tool_data else 'empty'}")

            poetry_data = tool_data.get("poetry", {})
            logger.debug(
                f"Poetry data: {poetry_data.keys() if poetry_data else 'empty'}"
            )

            scripts = poetry_data.get("scripts", {})
            logger.debug(f"Found {len(scripts)} scripts: {list(scripts.keys())}")

            for script_name, script_target in scripts.items():
                if not script_name or not script_target:
                    logger.debug(
                        f"Skipping empty script name or target: name={script_name}, target={script_target}"
                    )
                    continue

                # Check if the script target contains multiple commands with '&&'
                if isinstance(script_target, str) and "&&" in script_target:
                    # For lint scripts with multiple commands, we want to execute them as a single command
                    # to match the original behavior
                    command = f"poetry run {script_name}"
                    description = f"Poetry script: {script_name}"

                    logger.debug(f"Adding combined command: {command}")

                    self._commands.append(
                        Command(
                            command=command,
                            description=description,
                            type="poetry_script",
                            source=str(self.file_path),
                            metadata={
                                "script_name": script_name,
                                "script_target": script_target,
                                "original_command": script_target,
                                "is_combined": True,
                            },
                        )
                    )
                    logger.debug(f"Added combined command: {command}")

                    # Also add individual commands for better discoverability
                    sub_commands = [
                        cmd.strip() for cmd in script_target.split("&&") if cmd.strip()
                    ]
                    for i, sub_cmd in enumerate(sub_commands, 1):
                        cmd = f"poetry run {sub_cmd.strip()}"
                        desc = f"Part of '{script_name}': {sub_cmd.strip()}"

                        logger.debug(f"Adding sub-command: {cmd}")

                        self._commands.append(
                            Command(
                                command=cmd,
                                description=desc,
                                type="poetry_script_part",
                                source=str(self.file_path),
                                metadata={
                                    "script_name": f"{script_name}: {i}",
                                    "script_target": sub_cmd.strip(),
                                    "original_command": script_target,
                                    "is_part_of": script_name,
                                    "part_number": i,
                                    "total_parts": len(sub_commands),
                                },
                            )
                        )
                        logger.debug(f"Added sub-command: {cmd}")
                else:
                    # Single command
                    command = f"poetry run {script_name}"
                    description = f"Poetry script: {script_name}"

                    logger.debug(f"Adding command: {command}")

                    self._commands.append(
                        Command(
                            command=command,
                            description=description,
                            type="poetry_script",
                            source=str(self.file_path),
                            metadata={
                                "script_name": script_name,
                                "script_target": script_target,
                                "original_command": script_target,
                            },
                        )
                    )
                    logger.debug(f"Added command: {command}")

            logger.debug(
                f"Total commands after extracting Poetry scripts: {len(self._commands)}"
            )

        except (AttributeError, KeyError) as e:
            logger.error(f"Error extracting poetry scripts: {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Unexpected error extracting poetry scripts: {e}", exc_info=True
            )

    def _extract_test_commands(self, data: Dict[str, Any]) -> None:
        """Extract test commands from pyproject.toml."""
        from domd.core.commands import Command

        try:
            # Check for pytest configuration
            if "pytest" in data.get("tool", {}):
                command = "pytest"
                description = "Run pytest"

                self._commands.append(
                    Command(
                        command=command,
                        description=description,
                        type="pytest",
                        source=str(self.file_path),
                    )
                )

            # Check for tox configuration
            if "tox" in data.get("tool", {}):
                command = "tox"
                description = "Run tox"

                self._commands.append(
                    Command(
                        command=command,
                        description=description,
                        type="tox",
                        source=str(self.file_path),
                    )
                )
        except (AttributeError, KeyError) as e:
            print(f"Error extracting test commands: {e}")
            pass

    def _extract_build_commands(self, data: Dict[str, Any]) -> None:
        """Extract build-related commands."""
        from domd.core.commands import Command

        try:
            # Check for build system requirements
            build_backend = data.get("build-system", {}).get("build-backend", "")

            if build_backend:
                command = "python -m build"
                description = "Build the package"

                self._commands.append(
                    Command(
                        command=command,
                        description=description,
                        type="build",
                        source=str(self.file_path),
                    )
                )
        except (AttributeError, KeyError) as e:
            print(f"Error extracting build commands: {e}")
            pass
