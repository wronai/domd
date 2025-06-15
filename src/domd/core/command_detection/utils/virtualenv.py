"""Utilities for working with Python virtual environments."""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


def get_virtualenv_info(venv_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Get information about a Python virtual environment.

    Args:
        venv_path: Path to the virtual environment. If None, tries to detect automatically.

    Returns:
        Dictionary containing virtual environment information:
        - path: Path to the virtual environment
        - exists: Whether the virtual environment exists
        - python: Path to the Python interpreter in the virtual environment
        - version: Python version string
    """
    result: Dict[str, Any] = {
        "path": None,
        "exists": False,
        "python": None,
        "version": None,
    }

    # Try to detect virtual environment if path not provided
    if venv_path is None:
        # Check if we're running in a virtual environment
        if hasattr(sys, "real_prefix"):
            # Virtualenv
            venv_path = sys.prefix
        elif hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix:
            # venv
            venv_path = sys.prefix
        else:
            # Not in a virtual environment
            return result

    venv_path = Path(venv_path).resolve()
    result["path"] = str(venv_path)

    if not venv_path.exists():
        return result

    result["exists"] = True

    # Find Python interpreter
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if python_path.exists():
        result["python"] = str(python_path)

        # Get Python version
        try:
            import subprocess

            version_output = subprocess.check_output(
                [str(python_path), "--version"], stderr=subprocess.STDOUT, text=True
            )
            result["version"] = version_output.strip()
        except Exception as e:
            logger.warning(f"Failed to get Python version from {python_path}: {e}")

    return result


def get_virtualenv_environment(venv_info: Dict[str, Any]) -> Dict[str, str]:
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
