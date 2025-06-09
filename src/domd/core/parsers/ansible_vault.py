"""Parser for Ansible Vault files."""

from pathlib import Path
from typing import TYPE_CHECKING, List

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class AnsibleVaultParser(BaseParser):
    """Parser for Ansible Vault encrypted files."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Ansible Vault files."""
        return [
            "**/group_vars/**/*vault*.yml",
            "**/group_vars/**/*vault*.yaml",
            "**/host_vars/**/*vault*.yml",
            "**/host_vars/**/*vault*.yaml",
            "**/*vault*.yml",
            "**/*vault*.yaml",
            "**/.vault_pass.txt",
            "**/vault-password-file",
            "**/.ansible/vault_pass.txt",
        ]

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if the file is an Ansible Vault file or password file."""
        # Check for password files
        if file_path.name in [".vault_pass.txt", "vault-password-file"]:
            return True

        # Check for vault files in standard locations
        if "vault" in file_path.name.lower() and file_path.suffix in [".yml", ".yaml"]:
            # Check if it's in a standard Ansible directory
            parts = file_path.parts
            if "group_vars" in parts or "host_vars" in parts:
                return True

            # Or check file content for vault marker
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    return first_line.startswith("$ANSIBLE_VAULT;")
            except (UnicodeDecodeError, IOError):
                pass

        return False

    def parse(self) -> "List[Command]":
        """Parse Ansible Vault files and extract commands.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not self.file_path or not self.file_path.exists():
            return []

        self._commands: List[Command] = []
        rel_path = self.file_path.relative_to(self.project_root)

        try:
            # Handle password files
            if self.file_path.name in [".vault_pass.txt", "vault-password-file"]:
                cmd = f"# Use with: ansible-vault --vault-password-file={rel_path} ..."
                description = f"Ansible Vault password file: {rel_path}"

                self._commands.append(
                    Command(
                        command=cmd,
                        description=description,
                        type="ansible_vault",
                        source=str(self.file_path),
                        metadata={"vault_type": "password_file", "file": str(rel_path)},
                    )
                )
            else:
                # Handle vault files
                cmd = f"ansible-vault edit {rel_path}"
                description = f"Ansible Vault file: {rel_path}"

                self._commands.append(
                    Command(
                        command=cmd,
                        description=description,
                        type="ansible_vault",
                        source=str(self.file_path),
                        metadata={
                            "vault_type": "encrypted_file",
                            "file": str(rel_path),
                        },
                    )
                )

                # Add decrypt command
                decrypt_cmd = f"ansible-vault decrypt {rel_path}"
                self._commands.append(
                    Command(
                        command=decrypt_cmd,
                        description=f"Decrypt vault file: {rel_path}",
                        type="ansible_vault",
                        source=str(self.file_path),
                        metadata={"vault_type": "decrypt", "file": str(rel_path)},
                    )
                )

        except Exception as e:
            print(f"Error processing Ansible Vault file {self.file_path}: {e}")

        return self._commands
