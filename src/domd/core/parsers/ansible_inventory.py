"""Parser for Ansible inventory files."""

import os
from pathlib import Path
from typing import TYPE_CHECKING, List

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class AnsibleInventoryParser(BaseParser):
    """Parser for Ansible inventory files and directories."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Ansible inventory."""
        return [
            "**/inventory/**/*",
            "**/inventory*",
            "**/hosts",
            "**/hosts.ini",
            "**/inventory.ini",
            "**/production",
            "**/staging",
            "**/development",
        ]

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if the file is an Ansible inventory file."""
        # Skip directories
        if file_path.is_dir():
            return False

        # Check for common inventory file extensions
        if file_path.suffix.lower() in [".ini", ".cfg", ".yml", ".yaml"]:
            return True

        # Check for common inventory file names without extension
        if file_path.name in ["hosts", "inventory"]:
            return True

        # Check if file is executable (might be a dynamic inventory script)
        if file_path.is_file() and os.access(file_path, os.X_OK):
            return True

        return False

    def _is_dynamic_inventory(self, file_path: Path) -> bool:
        """Check if the file is a dynamic inventory script."""
        if not file_path.is_file():
            return False

        # Check if file is executable
        if not os.access(file_path, os.X_OK):
            return False

        # Check for shebang or specific content patterns
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                return first_line.startswith("#!") or "ansible-inventory" in first_line
        except (UnicodeDecodeError, IOError):
            return False

    def parse(self) -> "List[Command]":
        """Parse Ansible inventory and extract commands.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not self.file_path or not self.file_path.exists():
            return []

        self._commands: List[Command] = []

        try:
            rel_path = self.file_path.relative_to(self.project_root)

            if self._is_dynamic_inventory(self.file_path):
                # Dynamic inventory script
                cmd = f"ansible-inventory -i {rel_path} --list"
                description = f"Dynamic inventory: {rel_path}"

                self._commands.append(
                    Command(
                        command=cmd,
                        description=description,
                        type="ansible_inventory",
                        source=str(self.file_path),
                        metadata={"inventory_type": "dynamic", "file": str(rel_path)},
                    )
                )
            else:
                # Static inventory file
                cmd = f"ansible all -i {rel_path} -m ping"
                description = f"Test inventory: {rel_path}"

                self._commands.append(
                    Command(
                        command=cmd,
                        description=description,
                        type="ansible_inventory",
                        source=str(self.file_path),
                        metadata={"inventory_type": "static", "file": str(rel_path)},
                    )
                )

                # If this is an inventory directory, also suggest using it directly
                if self.file_path.is_dir():
                    dir_cmd = f"ansible all -i {rel_path}/ -m ping"
                    self._commands.append(
                        Command(
                            command=dir_cmd,
                            description=f"Test inventory directory: {rel_path}",
                            type="ansible_inventory",
                            source=str(self.file_path),
                            metadata={
                                "inventory_type": "directory",
                                "file": str(rel_path),
                            },
                        )
                    )

        except Exception as e:
            print(f"Error processing Ansible inventory {self.file_path}: {e}")

        return self._commands
