"""Parser for composer.json files."""

import json
from typing import List

from ..commands import Command
from .base import BaseParser


class ComposerJsonParser(BaseParser):
    """Parser for composer.json files."""

    @property
    def supported_file_patterns(self) -> List[str]:
        return ["composer.json"]

    def parse(self) -> List[Command]:
        """Parse a composer.json file and return a list of commands.

        Returns:
            List of Command objects.
        """
        commands = []
        if not self.file_path:
            return commands

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Add composer install command
            commands.append(
                Command(
                    command="composer install",
                    type="composer_install",
                    description="Install Composer dependencies",
                    source=str(self.file_path),
                )
            )

            # Add scripts from composer.json
            scripts = data.get("scripts", {})
            for script_name, script_command in scripts.items():
                if isinstance(script_command, str):
                    commands.append(
                        Command(
                            command=f"composer {script_name}",
                            type="composer_script",
                            description=f"Composer script: {script_name}",
                            source=str(self.file_path),
                        )
                    )

        except (json.JSONDecodeError, OSError):
            # Log error or handle as needed
            pass

        return commands
