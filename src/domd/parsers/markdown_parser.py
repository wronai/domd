"""Markdown file parser for extracting commands from README files."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)

class MarkdownParser(BaseParser):
    """Parser for Markdown files to extract commands from code blocks."""

    supported_file_patterns = ["**/README.md", "**/*.md"]

    def _parse_commands(self) -> List[Dict[str, Any]]:
        """Parse commands from markdown file.

        Returns:
            List of command dictionaries with 'command', 'description', 'source', and 'type' keys
        """
        if not self.file_path or not self.file_path.exists():
            return []

        try:
            content = self.file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading {self.file_path}: {e}")
            return []

        commands = []
        in_code_block = False
        current_command = ""
        current_lang = ""

        # Look for code blocks with bash, shell, or no language specified
        code_block_pattern = re.compile(r'```(?:bash|shell|sh)?\s*\n(.*?)\n```', re.DOTALL)
        
        for match in code_block_pattern.finditer(content):
            code_block = match.group(1).strip()
            if not code_block:
                continue
                
            # Split into lines and clean up
            lines = [line.strip() for line in code_block.split('\n') if line.strip()]
            for line in lines:
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue
                    
                # Add the command
                commands.append({
                    'command': line,
                    'description': f'Command from {self.file_path.name}',
                    'type': 'shell',
                    'source': str(self.file_path.relative_to(self.project_root) if self.project_root else self.file_path),
                    'metadata': {
                        'line_number': content[:match.start()].count('\n') + 1,
                        'file': str(self.file_path.relative_to(self.project_root) if self.project_root else self.file_path),
                    }
                })

        logger.debug(f"Found {len(commands)} commands in {self.file_path}")
        return commands

def get_parsers() -> List[type]:
    """Return list of parser classes in this module."""
    return [MarkdownParser]
