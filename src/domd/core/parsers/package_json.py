"""Parser for package.json files."""

import json
from typing import Dict, List

from .base import BaseParser


class PackageJsonParser(BaseParser):
    """Parser for package.json files to extract npm scripts."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for package.json."""
        return ["package.json"]

    def parse(self) -> List[Dict]:
        """Parse package.json and extract npm scripts as commands.

        Returns:
            List of command dictionaries
        """
        if not self.file_path.exists():
            return []

        self._commands = []

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
                    self._create_command_dict(
                        command=command,
                        description=description,
                        command_type="npm_script",
                    )
                )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands
