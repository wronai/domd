"""Parser for Ansible roles."""

from pathlib import Path
from typing import TYPE_CHECKING, List

import yaml

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class AnsibleRoleParser(BaseParser):
    """Parser for Ansible roles."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Ansible roles."""
        return [
            "**/roles/*/tasks/main.yml",
            "**/roles/*/tasks/main.yaml",
            "**/roles/*/meta/main.yml",
            "**/roles/*/meta/main.yaml",
        ]

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if the file is part of an Ansible role."""
        parts = file_path.parts
        if "roles" not in parts:
            return False

        role_index = parts.index("roles")
        if role_index + 1 >= len(parts) - 2:  # Need at least roles/role_name/tasks/...
            return False

        # Check if it's a tasks or meta main file
        return parts[-2] in ["tasks", "meta"] and parts[-1] in ["main.yml", "main.yaml"]

    def _get_role_name(self, file_path: Path) -> str:
        """Extract role name from file path."""
        parts = file_path.parts
        role_index = parts.index("roles")
        if role_index + 1 < len(parts):
            return parts[role_index + 1]
        return "unknown"

    def parse(self, content: str = None) -> "List[Command]":
        """Parse Ansible role and extract commands.

        Args:
            content: Optional content of the file to parse. If not provided, will read from file_path.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not self.file_path or not self.file_path.exists():
            return []

        self._commands: List[Command] = []
        role_name = self._get_role_name(self.file_path)
        role_path = self.file_path.parent.parent

        # Only process the main tasks file to avoid duplicates
        if self.file_path.name != "main.yml" and self.file_path.name != "main.yaml":
            return []

        # Check if we already processed this role
        if any(
            cmd.metadata.get("role_name") == role_name
            for cmd in self._commands
            if hasattr(cmd, "metadata")
        ):
            return []

        # If content is not provided, read from file
        if content is None and not self.file_path.is_dir():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                # If we can't read the file, return empty list
                return []

        try:
            # Get relative path if file is in project directory, otherwise use full path
            try:
                role_rel_path = role_path.parent.parent.relative_to(self.project_root)
            except ValueError:
                role_rel_path = role_path.parent.parent

            # Create a command to run the role directly
            cmd = f"ansible-playbook {role_rel_path}/site.yml --tags {role_name}"
            description = f"Ansible role: {role_name}"

            self._commands.append(
                Command(
                    command=cmd,
                    description=description,
                    type="ansible_role",
                    source=str(self.file_path),
                    metadata={
                        "role_name": role_name,
                        "role_path": str(role_path.relative_to(self.project_root)),
                    },
                )
            )

            # If this is the meta/main.yml, also check for dependencies
            if "meta" in self.file_path.parts:
                try:
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        meta = yaml.safe_load(f)

                    if isinstance(meta, dict) and "dependencies" in meta:
                        deps = meta["dependencies"]
                        if isinstance(deps, list) and deps:
                            dep_cmd = f"ansible-galaxy install -r {role_path}/meta/requirements.yml"
                            self._commands.append(
                                Command(
                                    command=dep_cmd,
                                    description=f"Install dependencies for role: {role_name}",
                                    type="ansible_galaxy",
                                    source=str(self.file_path),
                                    metadata={
                                        "role_name": role_name,
                                        "dependencies": deps,
                                    },
                                )
                            )
                except (yaml.YAMLError, UnicodeDecodeError) as e:
                    print(f"Error parsing role meta {self.file_path}: {e}")

        except Exception as e:
            print(f"Error processing Ansible role {role_name}: {e}")

        return self._commands
