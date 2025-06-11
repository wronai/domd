"""Parser for package.json files."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.core.parsing.base import BaseParser


class PackageJsonParser(BaseParser):
    """Parser for package.json files to extract npm scripts."""

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        file_path: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the PackageJsonParser.

        Args:
            project_root: Root directory of the project
            file_path: Path to the package.json file
            **kwargs: Additional arguments passed to the base class
        """
        super().__init__(project_root=project_root, file_path=file_path, **kwargs)

    # Supported file patterns for package.json
    supported_file_patterns = ["package.json"]

    def parse(
        self,
        file_path: Optional[Union[str, Path]] = None,
        content: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Parse package.json and extract npm scripts.

        Args:
            file_path: Path to the file to parse (overrides self.file_path if provided)
            content: Optional content to parse instead of reading from file

        Returns:
            List of command dictionaries with 'command', 'description', 'source', and 'type' keys
        """
        if file_path is not None:
            self.file_path = Path(file_path).resolve()

        if content is None:
            if self.file_path is None or not self.file_path.exists():
                logging.warning(f"File not found: {self.file_path}")
                return []
            try:
                content = self.file_path.read_text(encoding="utf-8")
            except Exception as e:
                logging.error(f"Error reading file {self.file_path}: {e}")
                return []

        self.initialize()
        return self._parse_commands(content)

    def _parse_commands(self, content: str) -> List[Dict[str, Any]]:
        """Parse commands from package.json content.

        Args:
            content: The content of the package.json file

        Returns:
            List of command dictionaries with 'command', 'description', 'source', and 'type' keys
        """
        commands = []

        try:
            data = json.loads(content)

            # Extract scripts
            scripts = data.get("scripts", {})
            for script_name, script_command in scripts.items():
                if not script_name or not script_command:
                    continue

                command = f"npm run {script_name}"
                description = f"NPM script: {script_name}"

                commands.append(
                    {
                        "command": command,
                        "description": description,
                        "type": "npm_script",
                        "source": str(self.file_path),
                        "metadata": {
                            "script_name": script_name,
                            "script_command": script_command,
                            "original_command": script_command,
                        },
                    }
                )

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {self.file_path}: {e}")
            return []
        except Exception as e:
            logging.error(f"Error parsing package.json {self.file_path}: {e}")
            return []

        return commands
