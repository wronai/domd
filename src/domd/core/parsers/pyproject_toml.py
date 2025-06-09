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
        logger.warning("Neither tomli nor toml package is available. PyProjectTomlParser will not work.")


class PyProjectTomlParser(BaseParser):
    """Parser for pyproject.toml files to extract Python project commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for pyproject.toml."""
        return ["pyproject.toml"]

    def parse(self) -> List[Command]:
        """Parse pyproject.toml and extract project commands.

        Returns:
            List of Command objects
        """
        logger.debug(f"Starting to parse {self.file_path}")
        
        if not TOML_AVAILABLE:
            logger.error("No TOML parser available. Install 'tomli' or 'toml' package.")
            return []
            
        if not self.file_path or not self.file_path.exists():
            logger.error(f"File not found: {self.file_path}")
            return []

        from domd.core.commands import Command

        self._commands: List[Command] = []

        try:
            logger.debug(f"Reading content from {self.file_path}")
            content = self.file_path.read_text(encoding="utf-8")

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
                
            logger.debug(f"Successfully parsed TOML data: {data.keys() if data else 'empty'}")

            # Extract Poetry scripts
            self._extract_poetry_scripts(data)

            # Extract test commands
            self._extract_test_commands(data)
            # Extract build commands
            self._extract_build_commands(data)
            
            logger.debug(f"Extracted {len(self._commands)} commands from {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}", exc_info=True)
            return []

        return self._commands

    def _extract_poetry_scripts(self, data: Dict[str, Any]) -> None:
        """Extract Poetry scripts section."""
        from domd.core.commands import Command

        try:
            scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
            for script_name, script_target in scripts.items():
                if not script_name or not script_target:
                    continue

                command = f"poetry run {script_name}"
                description = f"Poetry script: {script_name}"

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
        except (AttributeError, KeyError) as e:
            print(f"Error extracting poetry scripts: {e}")
            pass

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
