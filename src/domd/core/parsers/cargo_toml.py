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

    def parse(self, file_path=None) -> List[Dict]:
        """Parse Cargo.toml and extract Rust project commands.

        Args:
            file_path: Optional path to the Cargo.toml file

        Returns:
            List of command dictionaries
        """
        if file_path is None:
            file_path = self.file_path

        if not TOML_AVAILABLE or not file_path.exists():
            return []

        self._commands = []
        self.file_path = file_path  # Update the instance file_path

        try:
            # Read as text first to handle encoding
            content = file_path.read_text()
            # Parse with toml
            data = toml.loads(content)

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
        from domd.core.commands import Command

        basic_commands = [
            ("cargo check", "Check Rust code"),
            ("cargo build", "Build Rust project"),
            ("cargo run", "Run the Rust project"),
            ("cargo test", "Run Rust tests"),
            ("cargo clippy", "Lint Rust code"),
            ("cargo fmt", "Format Rust code"),
            ("cargo doc --open", "Build and open documentation"),
        ]

        for cmd, desc in basic_commands:
            self._commands.append(
                Command(
                    command=cmd,
                    description=desc,
                    type="cargo_command",
                    source=str(self.file_path),
                )
            )

    def _extract_workspace_commands(self, data: Dict[str, Any]) -> None:
        """Extract commands from workspace members."""
        from domd.core.commands import Command

        try:
            workspace = data.get("workspace", {})
            members = workspace.get("members", [])

            for member in members:
                # Add commands for each workspace member
                self._commands.append(
                    Command(
                        command=f"cargo build -p {member}",
                        description=f"Build workspace member: {member}",
                        type="cargo_workspace",
                        source=str(self.file_path),
                    )
                )
        except (AttributeError, KeyError):
            pass

    def _extract_package_commands(self, data: Dict[str, Any]) -> None:
        """Extract commands from package metadata."""
        from domd.core.commands import Command

        try:
            package = data.get("package", {})
            name = package.get("name", "")

            if name:
                # Add package-specific commands
                self._commands.append(
                    Command(
                        command=f"cargo build -p {name}",
                        description=f"Build package: {name}",
                        type="cargo_package",
                        source=str(self.file_path),
                    )
                )
        except (AttributeError, KeyError):
            pass
