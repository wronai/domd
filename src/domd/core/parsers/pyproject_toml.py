"""Parser for pyproject.toml files."""

from typing import Any, Dict, List, Union

from domd.core.commands import Command

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

    def parse(self) -> List[Command]:
        """Parse pyproject.toml and extract project commands.

        Returns:
            List of Command objects
        """
        if not TOML_AVAILABLE or not self.file_path or not self.file_path.exists():
            return []

        from domd.core.commands import Command

        self._commands: List[Command] = []

        try:
            # Read the file as text first
            content = self.file_path.read_text(encoding="utf-8")

            # Try to load with the available TOML library
            if "tomli" in globals():
                import tomli as toml_lib
            else:
                import toml as toml_lib

            if hasattr(toml_lib, "loads"):
                data = toml_lib.loads(content)
            else:
                # Fallback for older versions of toml
                data = toml_lib.loads(content)

            # Extract Poetry scripts
            self._extract_poetry_scripts(data)

            # Extract test commands
            self._extract_test_commands(data)

            # Extract build commands
            self._extract_build_commands(data)
        except Exception as e:
            print(f"Error parsing {self.file_path}: {e}")
            import traceback

            traceback.print_exc()
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
