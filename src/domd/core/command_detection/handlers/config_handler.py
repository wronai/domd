"""Handler for finding and processing configuration files."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ...services.file_processor import FileProcessor
from ...services.pattern_matcher import PatternMatcher

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
        self.exclude_patterns = set(exclude_patterns or [])
        self.include_patterns = set(include_patterns or [])
        self.ignore_file = ignore_file
        self.file_processor = FileProcessor(project_root=project_path)
        self.pattern_matcher = PatternMatcher()

        # Load ignore patterns from file if provided
        if self.ignore_file and self.ignore_file.exists():
            self._load_ignore_patterns()

    def find_config_files(self, parsers: List[Any]) -> List[Path]:
        """Find all configuration files that can be parsed by the given parsers.

        Args:
            parsers: List of parser instances that can parse configuration files

        Returns:
            List of Path objects to configuration files
        """
        if not parsers:
            logger.warning("No parsers provided, cannot find config files")
            return []

        # Get all supported file patterns from parsers
        supported_patterns: Set[str] = set()
        for parser in parsers:
            if hasattr(parser, "get_supported_files"):
                patterns = parser.get_supported_files()
                if patterns:
                    supported_patterns.update(patterns)

        if not supported_patterns:
            logger.warning("No supported file patterns found in parsers")
            return []

        logger.debug(f"Looking for files matching patterns: {supported_patterns}")

        # Find all files matching the patterns
        matched_files = self.file_processor.find_files(
            patterns=supported_patterns,
            exclude_patterns=self.exclude_patterns,
            include_patterns=self.include_patterns,
            max_depth=3,  # Limit depth for performance
        )

        logger.info(f"Found {len(matched_files)} configuration files")
        return matched_files

    def _load_ignore_patterns(self) -> None:
        """Load ignore patterns from the ignore file."""
        if not self.ignore_file or not self.ignore_file.exists():
            return

        try:
            with open(self.ignore_file, "r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                self.exclude_patterns.update(patterns)
                logger.info(
                    f"Loaded {len(patterns)} ignore patterns from {self.ignore_file}"
                )
        except Exception as e:
            logger.error(f"Error loading ignore patterns from {self.ignore_file}: {e}")

    def should_process_file(self, file_path: Union[str, Path]) -> bool:
        """Check if a file should be processed based on include/exclude patterns.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file should be processed, False otherwise
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        if not file_path.exists() or not file_path.is_file():
            return False

        # Convert to relative path for pattern matching
        try:
            rel_path = file_path.relative_to(self.project_path)
        except ValueError:
            # File is outside project directory
            return False

        # Check exclude patterns first
        if self.pattern_matcher.match_any_pattern(str(rel_path), self.exclude_patterns):
            return False

        # If include patterns are specified, file must match at least one
        if self.include_patterns and not self.pattern_matcher.match_any_pattern(
            str(rel_path), self.include_patterns
        ):
            return False

        return True
