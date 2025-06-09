"""Utilities for virtual environment detection and activation."""

import os
import sys
from typing import Any, Dict, Optional


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


def get_environment(venv_info: Dict[str, Any]) -> Dict[str, str]:
    """Get environment variables for command execution with virtualenv.

    Args:
        venv_info: Dictionary with virtual environment information

    Returns:
        Dictionary with environment variables with virtualenv paths included
    """
    # Import the function from project_detection.virtualenv to avoid duplication
    from domd.core.project_detection.virtualenv import get_virtualenv_environment

    # Call the implementation from project_detection.virtualenv
    return get_virtualenv_environment(venv_info)


def setup_virtualenv(venv_path: Optional[str] = None) -> Dict[str, Any]:
    """Set up virtual environment for command execution.

    Args:
        venv_path: Optional path to virtual environment

    Returns:
        Dictionary with virtual environment information
    """
    if venv_path:
        venv_info = get_virtualenv_info(venv_path)
    else:
        venv_info = {
            "exists": False,
            "path": None,
            "activate_command": None,
            "python_path": None,
        }

    return venv_info


def get_virtualenv_info(project_path: str) -> Dict[str, Any]:
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
    # Import the function from project_detection.virtualenv to avoid duplication
    from domd.core.project_detection.virtualenv import (
        get_virtualenv_info as get_venv_info,
    )

    # Call the implementation from project_detection.virtualenv
    venv_info = get_venv_info(project_path)

    # If the function doesn't return the expected format, provide defaults
    if not isinstance(venv_info, dict):
        return {
            "exists": False,
            "path": None,
            "activate_command": None,
            "python_path": None,
        }

    # Ensure the returned dictionary has all expected keys
    venv_info.setdefault(
        "exists", "path" in venv_info and venv_info["path"] is not None
    )
    venv_info.setdefault("activate_command", None)
    venv_info.setdefault("python_path", None)

    return venv_info
