"""File processing utilities for finding and filtering configuration files."""

import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from .pattern_matcher import PatternMatcher

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handles finding and processing configuration files in a project."""

    def __init__(
        self,
        project_root: Union[str, Path],
        include_patterns: Optional[Iterable[str]] = None,
        exclude_patterns: Optional[Iterable[str]] = None,
        follow_links: bool = False,
        max_depth: Optional[int] = None,
    ):
        """Initialize the file processor.

        Args:
            project_root: Root directory of the project
            include_patterns: File patterns to include (if None, all files are included)
            exclude_patterns: File patterns to exclude (if None, no files are excluded)
            follow_links: Whether to follow symbolic links
            max_depth: Maximum directory depth to search (None for no limit)
        """
        self.project_root = Path(project_root).resolve()
        self.include_patterns = set(include_patterns or [])
        self.exclude_patterns = set(exclude_patterns or [])
        self.follow_links = follow_links
        self.max_depth = max_depth
        self.matcher = PatternMatcher()

        # Common directories to exclude by default
        self.default_exclude_dirs = {
            ".git",
            ".svn",
            ".hg",
            ".tox",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".hypothesis",
            "node_modules",
            "bower_components",
            "dist",
            "build",
            "*.egg-info",
        }

    def find_config_files(
        self,
        patterns: Optional[Iterable[str]] = None,
        exclude: Optional[Iterable[str]] = None,
        max_depth: Optional[int] = None,
    ) -> List[Path]:
        """Find configuration files matching the given patterns.

        Args:
            patterns: File patterns to match (overrides include_patterns if provided)
            exclude: File patterns to exclude (overrides exclude_patterns if provided)
            max_depth: Maximum directory depth to search (overrides self.max_depth if provided)

        Returns:
            List of matching file paths
        """
        include = set(patterns) if patterns is not None else self.include_patterns
        exclude = set(exclude) if exclude is not None else self.exclude_patterns
        max_depth = max_depth if max_depth is not None else self.max_depth

        # If no include patterns are specified, include all files
        if not include:
            include = {"*"}

        # Combine exclude patterns with default excludes
        all_exclude = set(self.default_exclude_dirs)
        all_exclude.update(exclude)

        logger.debug("Finding files in %s", self.project_root)
        logger.debug("  Include patterns: %s", include)
        logger.debug("  Exclude patterns: %s", all_exclude)

        found_files = set()

        # Walk the directory tree
        for root, dirs, files in os.walk(
            self.project_root, followlinks=self.follow_links
        ):
            # Skip excluded directories
            rel_root = Path(root).relative_to(self.project_root)

            # Check directory depth
            if max_depth is not None and len(rel_root.parts) >= max_depth:
                del dirs[:]  # Don't recurse deeper
                continue

            # Filter out excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not self.matcher.match_file(
                    str(rel_root / d) + "/", all_exclude, default=False
                )
            ]

            # Process files in current directory
            for file_name in files:
                file_path = rel_root / file_name

                # Skip excluded files
                if self.matcher.match_file(str(file_path), all_exclude, default=False):
                    continue

                # Check if file matches include patterns
                if self.matcher.match_file(str(file_path), include, default=False):
                    found_files.add(self.project_root / file_path)

        return sorted(found_files)

    def find_files(
        self,
        patterns: Optional[Iterable[str]] = None,
        exclude: Optional[Iterable[str]] = None,
        max_depth: Optional[int] = None,
        include_patterns: Optional[Iterable[str]] = None,
        exclude_patterns: Optional[Iterable[str]] = None,
        include: Optional[Iterable[str]] = None,  # Alias for patterns
    ) -> List[Path]:
        """Find files matching the given patterns (alias for find_config_files).

        Args:
            patterns: File patterns to match (overrides include_patterns if provided)
            exclude: File patterns to exclude (overrides exclude_patterns if provided)
            max_depth: Maximum directory depth to search (overrides self.max_depth if provided)
            include_patterns: Alias for patterns (for backward compatibility)
            exclude_patterns: Alias for exclude (for backward compatibility)
            include: Alias for patterns (for backward compatibility)

        Returns:
            List of matching file paths
        """
        # Handle backward compatibility with old parameter names
        if patterns is None:
            if include is not None:
                patterns = include
            elif include_patterns is not None:
                patterns = include_patterns

        if exclude is None and exclude_patterns is not None:
            exclude = exclude_patterns

        return self.find_config_files(patterns, exclude, max_depth)

    def group_files_by_extension(
        self, files: Iterable[Union[str, Path]]
    ) -> Dict[str, List[Path]]:
        """Group files by their file extension.

        Args:
            files: List of file paths

        Returns:
            Dictionary mapping file extensions to lists of file paths
        """
        groups: Dict[str, List[Path]] = {}

        for file_path in map(Path, files):
            ext = file_path.suffix.lower()
            if ext not in groups:
                groups[ext] = []
            groups[ext].append(file_path.resolve())

        return groups

    def filter_files_by_size(
        self,
        files: Iterable[Union[str, Path]],
        min_size: int = 0,
        max_size: Optional[int] = None,
    ) -> List[Path]:
        """Filter files by size.

        Args:
            files: List of file paths
            min_size: Minimum file size in bytes (inclusive)
            max_size: Maximum file size in bytes (inclusive)

        Returns:
            List of file paths that match the size criteria
        """
        result = []

        for file_path in map(Path, files):
            try:
                size = file_path.stat().st_size
                if size >= min_size and (max_size is None or size <= max_size):
                    result.append(file_path.resolve())
            except OSError as e:
                logger.debug("Failed to get size of %s: %s", file_path, e)

        return result

    def find_duplicate_files(
        self, files: Iterable[Union[str, Path]], compare_content: bool = False
    ) -> Dict[str, List[Path]]:
        """Find duplicate files based on name or content.

        Args:
            files: List of file paths to check
            compare_content: If True, compare file contents instead of just names

        Returns:
            Dictionary mapping file names or content hashes to lists of duplicate files
        """
        import hashlib

        duplicates: Dict[str, List[Path]] = {}

        for file_path in map(Path, files):
            try:
                if compare_content:
                    # Calculate file content hash
                    hasher = hashlib.md5()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
                    key = hasher.hexdigest()
                else:
                    # Use file name as key
                    key = file_path.name

                if key not in duplicates:
                    duplicates[key] = []
                duplicates[key].append(file_path.resolve())

            except OSError as e:
                logger.debug("Failed to process %s: %s", file_path, e)

        # Filter out non-duplicates
        return {k: v for k, v in duplicates.items() if len(v) > 1}
