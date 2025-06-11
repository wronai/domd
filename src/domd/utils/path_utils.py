"""Utility functions for path handling in DoMD."""

import os
from pathlib import Path
from typing import Optional, Union


def to_relative_path(
    path: Union[str, Path, None], base: Optional[Union[str, Path]] = None
) -> str:
    """Convert an absolute path to a relative path for logging and display.

    Args:
        path: The path to convert (can be absolute or relative)
        base: The base path to make relative to. If None, uses current working directory.

    Returns:
        str: A relative path if possible, otherwise the original path as string.
             Returns empty string if path is None.
    """
    if path is None:
        return ""

    path_str = str(path).strip()
    if not path_str:
        return ""

    path_obj = Path(path_str).expanduser()

    # If path doesn't exist, return as string without resolution
    if not path_obj.exists():
        return path_str

    # Resolve the path to handle symlinks and normalize
    try:
        path_obj = path_obj.resolve()
    except (RuntimeError, OSError):
        return path_str

    # Try to make path relative to base or cwd
    try:
        base_path = Path(base).resolve() if base else Path.cwd()
        if path_obj == base_path:
            return "."
        return str(path_obj.relative_to(base_path))
    except (ValueError, RuntimeError):
        # If we can't make it relative (e.g., different drives on Windows), return as string
        return str(path_obj)


def safe_path_display(
    path: Union[str, Path, None],
    base: Optional[Union[str, Path]] = None,
    hide_home: bool = True,
) -> str:
    """Get a safe, user-friendly path for display in logs and UI.

    Args:
        path: The path to format. If None, returns an empty string.
        base: Base path to make relative to
        hide_home: If True, replace home directory with ~

    Returns:
        str: A safe, user-friendly path string, or empty string if path is None
    """
    if path is None:
        return ""

    path_str = str(path).strip()
    if not path_str:
        return ""

    # Handle home directory replacement
    if hide_home:
        try:
            home = str(Path.home())
            if path_str.startswith(home):
                return f"~{os.sep}{path_str[len(home):].lstrip(os.sep)}"
        except (RuntimeError, KeyError):  # Can't determine home directory
            pass

    # Convert to relative path if possible
    return to_relative_path(path_str, base)
