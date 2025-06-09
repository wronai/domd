"""
File-related utility functions for the domd package.

This module provides utility functions for file operations such as reading,
writing, and finding files, as well as directory management.
"""

import os
import os.path
from pathlib import Path
from typing import Generator, List, Optional, Set, Union


def ensure_directory(directory: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory: The directory path to ensure exists.
    """
    os.makedirs(directory, exist_ok=True)


def find_files(
    directory: Union[str, Path],
    patterns: Union[str, List[str]] = None,
    exclude_dirs: Optional[Set[str]] = None,
) -> Generator[Path, None, None]:
    """
    Recursively find files in a directory matching the given patterns.

    Args:
        directory: The directory to search in.
        patterns: File patterns to match (e.g., '*.py' or ['*.py', '*.txt']).
                 If None, all files are matched.
        exclude_dirs: Set of directory names to exclude from the search.

    Yields:
        Path objects for matching files.
    """
    if isinstance(patterns, str):
        patterns = [patterns]

    if exclude_dirs is None:
        exclude_dirs = set()

    directory = Path(directory)

    for item in directory.iterdir():
        if item.name in exclude_dirs:
            continue

        if item.is_dir():
            yield from find_files(item, patterns, exclude_dirs)
        elif patterns is None or any(item.match(p) for p in patterns):
            yield item


def read_file(file_path: Union[str, Path]) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read.

    Returns:
        The contents of the file as a string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: Union[str, Path], content: str) -> None:
    """
    Write content to a file, creating parent directories if needed.

    Args:
        file_path: Path to the file to write.
        content: Content to write to the file.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
