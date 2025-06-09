"""Parser for Makefiles."""

import re
from pathlib import Path
from typing import List

from ..commands.command import Command
from .base import BaseParser


class MakefileParser(BaseParser):
    """Parser for Makefiles to extract targets as commands."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Makefiles."""
        return ["Makefile", "makefile", "GNUmakefile"]

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if the file is a Makefile."""
        return (
            file_path.name.lower() in ["makefile", "gnumakefile"]
            or file_path.name == "Makefile"
        )

    def parse(self) -> "List[Command]":
        """Parse Makefile and extract targets as commands.

        Returns:
            List of Command objects
        """
        if not self.file_path.exists():
            return []

        self._commands = []
        content = self.file_path.read_text(encoding="utf-8")

        # Pattern to match Makefile targets
        # This matches targets that:
        # 1. Start at the beginning of a line (with optional leading whitespace)
        # 2. Are not .PHONY or other special targets
        # 3. Don't contain special characters (simplified)
        target_pattern = re.compile(
            r"^\s*([a-zA-Z][a-zA-Z0-9_-]*)\s*:.*?\n(?:\t.*\n)*", re.MULTILINE
        )

        for match in target_pattern.finditer(content):
            target = match.group(1).strip()
            if not target or target.startswith("."):
                continue

            command = f"make {target}"
            description = f"Make target: {target}"

            self._commands.append(
                Command(
                    command=command,
                    description=description,
                    type="make_target",
                    source=str(self.file_path),
                    metadata={"target": target, "original_command": command},
                )
            )

        return self._commands
