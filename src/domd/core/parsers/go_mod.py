"""Parser for Go module files (go.mod and go.work)."""

import re
from typing import Dict, List, Tuple

from .base import BaseParser


class GoModParser(BaseParser):
    """Parser for Go module files to extract Go project commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Go module files."""
        return ["go.mod", "go.work"]

    def parse(self) -> List[Dict]:
        """Parse Go module files and extract Go project commands.

        Returns:
            List of command dictionaries
        """
        if not self.file_path.exists():
            return []

        self._commands = []

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
        basic_commands = [
            ("go build", "Build Go package"),
            ("go test", "Run Go tests"),
            ("go test -v ./...", "Run all tests with verbose output"),
            ("go mod tidy", "Add missing and remove unused modules"),
            ("go fmt ./...", "Format all Go files"),
            ("go vet ./...", "Run Go vet on all packages"),
        ]

        for cmd, desc in basic_commands:
            self._commands.append(
                self._create_command_dict(
                    command=cmd,
                    description=desc,
                    command_type="go",
                )
            )

    def _parse_module_file(self) -> None:
        """Parse the Go module file and extract module-specific commands."""
        content = self.file_path.read_text(encoding="utf-8")

        # Extract module name
        module_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
        if module_match:
            module_name = module_match.group(1)
            self._commands.append(
                self._create_command_dict(
                    command=f"go build {module_name}/...",
                    description=f"Build all packages in module: {module_name}",
                    command_type="go_module",
                )
            )

        # Check for Go version
        go_version_match = re.search(r"^go\s+(\d+\.\d+)", content, re.MULTILINE)
        if go_version_match:
            go_version = go_version_match.group(1)
            self._commands.append(
                self._create_command_dict(
                    command=f"go{go_version} build",
                    description=f"Build with Go {go_version}",
                    command_type="go_versioned",
                )
            )

        # If this is a workspace file, add workspace-specific commands
        if self.file_path.name == "go.work":
            self._parse_workspace_file(content)

    def _parse_workspace_file(self, content: str) -> None:
        """Parse go.work file and extract workspace-specific commands."""
        # Find all use directives in the workspace file
        use_dirs = re.findall(r"use\s+([^\s\n]+)", content)

        for dir_name in use_dirs:
            # Add commands for each directory in the workspace
            self._commands.append(
                self._create_command_dict(
                    command=f"go work use {dir_name}",
                    description=f"Use directory in workspace: {dir_name}",
                    command_type="go_workspace",
                )
            )

            # Add build commands for each directory
            self._commands.append(
                self._create_command_dict(
                    command=f"go build ./{dir_name}",
                    description=f"Build package in directory: {dir_name}",
                    command_type="go_build",
                )
            )
