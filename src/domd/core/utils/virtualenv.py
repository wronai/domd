"""Utilities for virtual environment detection and activation."""

import os
import sys
from typing import Dict, Optional


def find_virtualenv(project_path: str) -> Optional[str]:
    """Find virtual environment in the project directory.

    Args:
        project_path: Path to the project root or directly to a virtual environment

    Returns:
        Path to the virtual environment or None if not found
    """
    # Check if the given path is already a virtual environment
    if (
        os.path.exists(os.path.join(project_path, "pyvenv.cfg"))
        or os.path.exists(os.path.join(project_path, "bin", "activate"))
        or os.path.exists(os.path.join(project_path, "Scripts", "activate"))
    ):
        return project_path

    # Otherwise check standard locations
    venv_paths = [
        os.path.join(project_path, "venv"),
        os.path.join(project_path, ".venv"),
        os.path.join(project_path, "env"),
    ]

    for path in venv_paths:
        if (
            os.path.exists(os.path.join(path, "pyvenv.cfg"))
            or os.path.exists(os.path.join(path, "bin", "activate"))
            or os.path.exists(os.path.join(path, "Scripts", "activate"))
        ):
            return path
    return None


def get_activate_command(venv_path: str) -> Optional[str]:
    """Get the command to activate virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Activation command or None if not applicable
    """
    if not venv_path or not os.path.exists(venv_path):
        return None

    if sys.platform == "win32":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        if os.path.exists(activate_script):
            return f"call {activate_script}"
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        if os.path.exists(activate_script):
            return f"source {activate_script}"

    return None


def get_virtualenv_info(project_path: str) -> Dict[str, any]:
    """Get information about virtual environment.

    Args:
        project_path: Path to the project root

    Returns:
        Dictionary with virtual environment information containing:
            - exists: bool - Whether the virtual environment exists
            - path: Optional[str] - Path to the virtual environment
            - activate_command: Optional[str] - Command to activate the virtual environment
            - python_path: Optional[str] - Path to the Python interpreter in the virtual environment
    """
    # Default return value when no virtual environment is found
    default_result = {
        "exists": False,
        "path": None,
        "activate_command": None,
        "python_path": None,
    }

    venv_path = find_virtualenv(project_path)
    if not venv_path:
        return default_result

    activate_cmd = get_activate_command(venv_path)
    python_path = None

    # Try to get Python interpreter path
    if sys.platform == "win32":
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_path, "bin", "python")

    if python_path and not os.path.exists(python_path):
        python_path = None

    return {
        "exists": True,
        "path": venv_path,
        "activate_command": activate_cmd,
        "python_path": python_path,
    }
