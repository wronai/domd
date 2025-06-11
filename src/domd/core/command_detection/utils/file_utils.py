"""File utility functions for command detection."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Set, Union

logger = logging.getLogger(__name__)


def find_files_by_pattern(
    directory: Union[str, Path],
    patterns: Union[str, List[str]],
    exclude_patterns: Optional[Set[str]] = None,
    include_hidden: bool = False,
    max_depth: Optional[int] = None,
) -> List[Path]:
    """Find files matching the given patterns in a directory.

    Args:
        directory: Directory to search in
        patterns: File patterns to match (e.g., "*.py" or ["*.py", "*.sh"])
        exclude_patterns: Patterns to exclude from results
        include_hidden: Whether to include hidden files/directories
        max_depth: Maximum depth to search (None for unlimited)

    Returns:
        List of matching file paths
    """
    if isinstance(patterns, str):
        patterns = [patterns]

    if exclude_patterns is None:
        exclude_patterns = set()

    directory = Path(directory).resolve()
    if not directory.is_dir():
        logger.warning(f"Directory not found: {directory}")
        return []

    matching_files = []

    for root, dirs, files in os.walk(directory, topdown=True):
        # Skip hidden directories if not including hidden
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Check depth limit
        if max_depth is not None:
            current_depth = Path(root).relative_to(directory).parts
            if len(current_depth) >= max_depth:
                continue

        for file in files:
            # Skip hidden files if not including hidden
            if not include_hidden and file.startswith("."):
                continue

            file_path = Path(root) / file
            rel_path = file_path.relative_to(directory)

            # Check exclude patterns
            if any(rel_path.match(pat) for pat in exclude_patterns):
                continue

            # Check include patterns
            if any(rel_path.match(pat) for pat in patterns):
                matching_files.append(file_path.resolve())

    return matching_files


def read_file_safely(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Optional[str]:
    """Read a file safely with error handling.

    Args:
        file_path: Path to the file to read
        encoding: File encoding to use

    Returns:
        File contents as string, or None if there was an error
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def ensure_directory(directory: Union[str, Path]) -> bool:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory

    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False
