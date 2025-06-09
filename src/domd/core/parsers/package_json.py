"""Parser for package.json files."""

import json
from typing import TYPE_CHECKING, List

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class PackageJsonParser(BaseParser):
    """Parser for package.json files to extract npm scripts."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for package.json."""
        return ["package.json"]

    def parse(self) -> "List[Command]":
        """Parse package.json and extract npm scripts as commands.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not self.file_path.exists():
            return []

        self._commands: List[Command] = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract scripts
            scripts = data.get("scripts", {})
            for script_name, script_command in scripts.items():
                if not script_name or not script_command:
                    continue

                command = f"npm run {script_name}"
                description = f"NPM script: {script_name}"

                self._commands.append(
                    Command(
                        command=command,
                        description=description,
                        type="npm_script",
                        source=str(self.file_path),
                        metadata={
                            "script_name": script_name,
                            "script_command": script_command,
                            "original_command": script_command,
                        },
                    )
                )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands
