"""Virtual environment handling for project command detection."""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_virtualenv_info(path: Optional[str] = None) -> Dict[str, Any]:
    """Get information about a virtual environment.

    Args:
        path: Path to check for virtual environment

    Returns:
        Dictionary with virtual environment information
    """
    try:
        if path:
            path = str(Path(path).resolve())
            logger.debug(f"Checking for virtualenv at: {path}")

            # Check common virtualenv locations
            venv_dirs = [
                path,  # Direct path
                os.path.join(path, ".venv"),  # .venv in project
                os.path.join(path, "venv"),  # venv in project
                os.path.join(path, "env"),  # env in project
            ]

            for venv_dir in venv_dirs:
                if not os.path.isdir(venv_dir):
                    continue

                # Check for Python executable in bin/Scripts directory
                bin_dir = "Scripts" if sys.platform == "win32" else "bin"
                python_path = os.path.join(venv_dir, bin_dir, "python")
                if sys.platform == "win32":
                    python_path += ".exe"

                if os.path.isfile(python_path):
                    logger.debug(f"Found virtualenv at: {venv_dir}")
                    activate_script = (
                        "activate.bat" if sys.platform == "win32" else "activate"
                    )
                    activate_path = os.path.join(venv_dir, bin_dir, activate_script)

                    return {
                        "exists": True,
                        "path": venv_dir,
                        "python_path": python_path,
                        "activate_command": f"source {activate_path}"
                        if sys.platform != "win32"
                        else activate_path,
                    }

        logger.debug("No virtualenv found")
        return {
            "exists": False,
            "path": None,
            "python_path": None,
            "activate_command": None,
        }

    except Exception as e:
        logger.warning(f"Error detecting virtualenv: {e}", exc_info=True)
        return {
            "exists": False,
            "path": None,
            "python_path": None,
            "activate_command": None,
        }


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
