"""Utility functions for path handling in DoMD."""

import os
from pathlib import Path
from typing import Optional, Union


def to_relative_path(
    path: Union[str, Path], 
    base: Optional[Union[str, Path]] = None
) -> str:
    """Convert an absolute path to a relative path for logging and display.
    
    Args:
        path: The path to convert (can be absolute or relative)
        base: The base path to make relative to. If None, uses current working directory.
        
    Returns:
        str: A relative path if possible, otherwise the original path as string
    """
    if not path:
        return str(path)
        
    path_obj = Path(path).expanduser().resolve()
    
    # If path doesn't exist, return as string without resolution
    if not path_obj.exists():
        return str(path)
        
    # Try to make path relative to base or cwd
    try:
        base_path = Path(base).resolve() if base else Path.cwd()
        return str(path_obj.relative_to(base_path))
    except (ValueError, RuntimeError):
        # If we can't make it relative (e.g., different drives on Windows), return as string
        return str(path_obj)


def safe_path_display(
    path: Union[str, Path], 
    base: Optional[Union[str, Path]] = None,
    hide_home: bool = True
) -> str:
    """Get a safe, user-friendly path for display in logs and UI.
    
    Args:
        path: The path to format
        base: Base path to make relative to
        hide_home: If True, replace home directory with ~
        
    Returns:
        str: A safe, user-friendly path string
    """
    if not path:
        return str(path)
        
    path_str = str(path)
    
    # Handle home directory replacement
    if hide_home:
        try:
            home = str(Path.home())
            if path_str.startswith(home):
                return f"~{os.sep}{path_str[len(home) + 1:]}"
        except RuntimeError:  # Can't determine home directory
            pass
    
    # Convert to relative path if possible
    return to_relative_path(path_str, base)
