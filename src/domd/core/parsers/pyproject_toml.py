"""Parser for pyproject.toml files."""

from typing import Any, Dict, List

# Try to import tomli (Python 3.11+) or toml (older Python)
try:
    import tomli as toml

    TOML_AVAILABLE = True
except ImportError:
    try:
        import toml

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

from .base import BaseParser


class PyProjectTomlParser(BaseParser):
    """Parser for pyproject.toml files to extract Python project commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for pyproject.toml."""
        return ["pyproject.toml"]

    def parse(self) -> List[Dict]:
        """Parse pyproject.toml and extract project commands.

        Returns:
            List of command dictionaries
        """
        if not TOML_AVAILABLE or not self.file_path.exists():
            return []

        self._commands = []

        try:
            with open(self.file_path, "rb") as f:
                data = toml.load(f)

            # Extract Poetry scripts
            self._extract_poetry_scripts(data)

            # Extract test commands
            self._extract_test_commands(data)

            # Extract build commands
            self._extract_build_commands(data)

        except Exception as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands

    def _extract_poetry_scripts(self, data: Dict[str, Any]) -> None:
        """Extract Poetry scripts section."""
        try:
            scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
            for script_name, script_target in scripts.items():
                if not script_name or not script_target:
                    continue

                command = f"poetry run {script_name}"
                description = f"Poetry script: {script_name}"

                self._commands.append(
                    self._create_command_dict(
                        command=command,
                        description=description,
                        command_type="poetry_script",
                    )
                )
        except (AttributeError, KeyError):
            pass

    def _extract_test_commands(self, data: Dict[str, Any]) -> None:
        """Extract test commands from pyproject.toml."""
        try:
            # Check for pytest configuration
            if "pytest" in data.get("tool", {}):
                command = "pytest"
                description = "Run pytest"

                self._commands.append(
                    self._create_command_dict(
                        command=command,
                        description=description,
                        command_type="pytest",
                    )
                )

            # Check for tox configuration
            if "tox" in data.get("tool", {}):
                command = "tox"
                description = "Run tox"

                self._commands.append(
                    self._create_command_dict(
                        command=command,
                        description=description,
                        command_type="tox",
                    )
                )
        except (AttributeError, KeyError):
            pass

    def _extract_build_commands(self, data: Dict[str, Any]) -> None:
        """Extract build-related commands."""
        try:
            # Check for build system requirements
            build_backend = data.get("build-system", {}).get("build-backend", "")

            if build_backend:
                command = "python -m build"
                description = "Build the package"

                self._commands.append(
                    self._create_command_dict(
                        command=command,
                        description=description,
                        command_type="build",
                    )
                )
        except (AttributeError, KeyError):
            pass
