"""Configuration file handling for project command detection."""

import logging
import os
from pathlib import Path
from typing import List, Optional

from domd.parsing import FileProcessor, PatternMatcher
from domd.parsing.base import BaseParser

logger = logging.getLogger(__name__)


class ConfigFileHandler:
    """Handler for finding and processing configuration files."""

    def __init__(
        self,
        project_path: Path,
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
    ):
        """Initialize the ConfigFileHandler.

        Args:
            project_path: Path to the project root
            exclude_patterns: List of file patterns to exclude
            include_patterns: List of file patterns to include
            ignore_file: Path to the ignore file
        """
        self.project_path = project_path
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.ignore_file = ignore_file

        self.file_processor = FileProcessor(project_root=project_path)
        self.pattern_matcher = PatternMatcher()

    def find_config_files(self, parsers: List[BaseParser]) -> List[Path]:
        """Find all configuration files in the project.

        Args:
            parsers: List of parser instances to use for file detection

        Returns:
            List of Path objects to configuration files
        """
        logger.debug(f"Finding config files in: {self.project_path}")

        # Build exclude patterns
        exclude_patterns = [
            "**/.*",  # Hidden files and directories
            "**/__pycache__/**",
            "**/*.py[cod]",
            "**/*.so",
            "**/*.egg-info/**",
            "**/build/**",
            "**/dist/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/.tox/**",
            "**/.venv/**",
            "**/venv/**",
            "**/env/**",
            *self.exclude_patterns,
        ]

        # Add patterns from ignore file if it exists
        if self.ignore_file and self.ignore_file.exists():
            with open(self.ignore_file) as f:
                ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                exclude_patterns.extend(ignore_patterns)

        # Use the FileProcessor to find files
        all_files = self.file_processor.find_files(
            include=self.include_patterns if self.include_patterns else None,
            exclude=exclude_patterns,
        )

        # Filter files that have a parser
        config_files = []
        for file_path in all_files:
            if self._has_parser_for_file(file_path, parsers):
                config_files.append(file_path)
                logger.debug(f"Found config file: {file_path}")

        logger.debug(f"Found {len(config_files)} config files")
        return config_files

    def _has_parser_for_file(self, file_path: Path, parsers: List[BaseParser]) -> bool:
        """Check if any parser can handle the given file.

        Args:
            file_path: Path to the file to check
            parsers: List of parser instances

        Returns:
            True if a parser can handle the file
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        for parser in parsers:
            try:
                # Wywołaj can_parse jako metodę klasową, a nie instancji
                parser_class = parser.__class__
                if hasattr(parser_class, "can_parse"):
                    can_parse = parser_class.can_parse(file_path)
                    if can_parse:
                        return True
            except Exception as e:
                logger.warning(
                    f"Error checking if parser {parser.__class__.__name__} can parse {file_path}: {e}"
                )

        return False

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file should be processed
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        # Use FileProcessor to check if file should be processed
        relative_path = str(file_path.relative_to(self.project_path))

        # Check exclude patterns
        if self.pattern_matcher.match_any_pattern(relative_path, self.exclude_patterns):
            return False

        # Check include patterns (if any)
        if self.include_patterns:
            return self.pattern_matcher.match_any_pattern(
                relative_path, self.include_patterns
            )

        return True
