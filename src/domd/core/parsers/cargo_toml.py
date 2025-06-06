"""Parser for Cargo.toml files (Rust projects)."""

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


class CargoTomlParser(BaseParser):
    """Parser for Cargo.toml files to extract Rust project commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Cargo.toml."""
        return ["Cargo.toml"]

    def parse(self) -> List[Dict]:
        """Parse Cargo.toml and extract Rust project commands.

        Returns:
            List of command dictionaries
        """
        if not TOML_AVAILABLE or not self.file_path.exists():
            return []

        self._commands = []

        try:
            with open(self.file_path, "rb") as f:
                data = toml.load(f)

            # Always include basic cargo commands
            self._add_basic_commands()

            # Extract custom commands from workspace or package
            self._extract_workspace_commands(data)
            self._extract_package_commands(data)

        except Exception as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands

    def _add_basic_commands(self) -> None:
        """Add basic cargo commands."""
        basic_commands = [
            ("cargo check", "Check Rust code"),
            ("cargo build", "Build Rust project"),
            ("cargo test", "Run Rust tests"),
            ("cargo clippy", "Lint Rust code"),
            ("cargo fmt", "Format Rust code"),
        ]

        for cmd, desc in basic_commands:
            self._commands.append(
                self._create_command_dict(
                    command=cmd,
                    description=desc,
                    command_type="cargo",
                )
            )

    def _extract_workspace_commands(self, data: Dict[str, Any]) -> None:
        """Extract commands from workspace members."""
        try:
            workspace = data.get("workspace", {})
            members = workspace.get("members", [])

            for member in members:
                # Add commands for each workspace member
                self._commands.append(
                    self._create_command_dict(
                        command=f"cargo build -p {member}",
                        description=f"Build workspace member: {member}",
                        command_type="cargo_workspace",
                    )
                )
        except (AttributeError, KeyError):
            pass

    def _extract_package_commands(self, data: Dict[str, Any]) -> None:
        """Extract commands from package metadata."""
        try:
            package = data.get("package", {})
            name = package.get("name", "")

            if name:
                # Add package-specific commands
                self._commands.append(
                    self._create_command_dict(
                        command=f"cargo build -p {name}",
                        description=f"Build package: {name}",
                        command_type="cargo_package",
                    )
                )
        except (AttributeError, KeyError):
            pass
