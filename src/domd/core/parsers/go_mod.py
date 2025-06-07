"""Parser for Go module files (go.mod and go.work)."""

import re
from typing import Dict, List

from .base import BaseParser


class GoModParser(BaseParser):
    """Parser for Go module files to extract Go project commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Go module files."""
        return ["go.mod", "go.work"]

    def parse(self, file_path=None) -> List[Dict]:
        """Parse Go module files and extract Go project commands.

        Args:
            file_path: Optional path to the go.mod or go.work file

        Returns:
            List of command dictionaries
        """
        if file_path is None:
            file_path = self.file_path

        if not file_path.exists():
            return []

        self._commands = []
        self.file_path = file_path  # Update the instance file_path

        try:
            # Add basic Go commands
            self._add_basic_commands()

            # Parse the module file
            self._parse_module_file()

        except Exception as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands

    def _add_basic_commands(self) -> None:
        """Add basic Go commands."""
        from domd.core.commands import Command

        basic_commands = [
            ("go build", "Build Go package"),
            ("go run .", "Run the main package"),
            ("go run main.go", "Run main.go file"),
            ("go test", "Run Go tests"),
            ("go test -v ./...", "Run all tests with verbose output"),
            ("go mod tidy", "Add missing and remove unused modules"),
            ("go fmt ./...", "Format all Go files"),
            ("go vet ./...", "Run Go vet on all packages"),
        ]

        for cmd, desc in basic_commands:
            self._commands.append(
                Command(
                    command=cmd,
                    description=desc,
                    type="go_command",
                    source=str(self.file_path),
                )
            )

    def _parse_module_file(self) -> None:
        """Parse the Go module file and extract module-specific commands."""
        from domd.core.commands import Command

        content = self.file_path.read_text(encoding="utf-8")

        # Extract module name
        module_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
        if module_match:
            module_name = module_match.group(1)
            self._commands.append(
                Command(
                    command=f"go build {module_name}/...",
                    description=f"Build all packages in module: {module_name}",
                    type="go_module",
                    source=str(self.file_path),
                )
            )

        # Check for Go version
        go_version_match = re.search(r"^go\s+(\d+\.\d+)", content, re.MULTILINE)
        if go_version_match:
            go_version = go_version_match.group(1)
            self._commands.append(
                Command(
                    command=f"go{go_version} build",
                    description=f"Build with Go {go_version}",
                    type="go_command",
                    source=str(self.file_path),
                )
            )

        # If this is a workspace file, add workspace-specific commands
        if self.file_path.name == "go.work":
            self._parse_workspace_file(content)

    def _parse_workspace_file(self, content: str) -> None:
        """Parse go.work file and extract workspace-specific commands."""
        from domd.core.commands import Command

        # Find all use directives in the workspace file
        use_dirs = re.findall(r"use\s+([^\s\n]+)", content)

        for dir_name in use_dirs:
            # Add commands for each directory in the workspace
            self._commands.append(
                Command(
                    command=f"go work use {dir_name}",
                    description=f"Use directory in workspace: {dir_name}",
                    type="go_workspace",
                    source=str(self.file_path),
                )
            )

            # Add build commands for each directory
            self._commands.append(
                Command(
                    command=f"go build ./{dir_name}",
                    description=f"Build package in directory: {dir_name}",
                    type="go_build",
                    source=str(self.file_path),
                )
            )
