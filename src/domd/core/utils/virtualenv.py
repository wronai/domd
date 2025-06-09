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
    env = os.environ.copy()

    # Add virtual environment's bin/scripts to PATH if available
    if venv_info.get("path"):
        venv_path = venv_info["path"]
        if sys.platform == "win32":
            bin_path = os.path.join(venv_path, "Scripts")
        else:
            bin_path = os.path.join(venv_path, "bin")

        if os.path.exists(bin_path):
            # Add to the beginning of PATH to ensure virtualenv binaries take precedence
            env["PATH"] = f"{bin_path}{os.pathsep}{env.get('PATH', '')}"

            # Set VIRTUAL_ENV for Python tools that check this
            env["VIRTUAL_ENV"] = venv_path

            # On Windows, we also need to set PYTHONHOME to None to avoid conflicts
            if sys.platform == "win32" and "PYTHONHOME" in env:
                del env["PYTHONHOME"]

    return env


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
