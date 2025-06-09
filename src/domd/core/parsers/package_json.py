"""Parser for package.json files."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class PackageJsonParser(BaseParser):
    """Parser for package.json files to extract npm scripts."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for package.json."""
        return ["package.json"]

    def parse(self, file_path=None, content=None) -> List[Dict]:
        """Parse package.json and extract npm scripts.

        Args:
            file_path: Path to the package.json file (mutually exclusive with content)
            content: Content of the package.json file (mutually exclusive with file_path)

        Returns:
            List of command dictionaries with 'command', 'description', 'source', and 'type' keys
        """
        import logging
        from pathlib import Path

        logger = logging.getLogger(__name__)
        commands = []

        # Set file path if provided
        if file_path is not None:
            self.file_path = Path(file_path)

        try:
            # If content is provided, parse it directly
            if content is not None:
                data = json.loads(content)
                source = "in-memory"
            # Otherwise, read from file
            elif file_path is not None:
                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    return []
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                source = str(file_path)
            # Fallback to instance file_path if available
            elif (
                hasattr(self, "file_path")
                and self.file_path
                and self.file_path.exists()
            ):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                source = str(self.file_path)
            else:
                logger.warning("No valid file path or content provided")
                return []

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
                        source=source,
                        metadata={
                            "script_name": script_name,
                            "script_command": script_command,
                            "original_command": script_command,
                        },
                    )
                )

        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in {source if 'source' in locals() else 'content'}: {e}"
            )
            return []
        except KeyError as e:
            logger.error(f"Missing expected key in package.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing package.json: {e}", exc_info=True)
            return []

        return self._commands
