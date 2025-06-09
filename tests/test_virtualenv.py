"""Tests for virtual environment support in DoMD."""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from domd.core.detector import ProjectCommandDetector


def create_mock_venv(venv_path: str, python_path: Optional[str] = None) -> None:
    """Create a mock virtual environment for testing.

    Args:
        venv_path: Path where to create the virtual environment
        python_path: Optional path to the Python interpreter to use
    """
    os.makedirs(venv_path, exist_ok=True)

    # Create bin directory and activate script
    if sys.platform == "win32":
        bin_dir = os.path.join(venv_path, "Scripts")
        activate_script = os.path.join(bin_dir, "activate.bat")
    else:
        bin_dir = os.path.join(venv_path, "bin")
        activate_script = os.path.join(bin_dir, "activate")

    os.makedirs(bin_dir, exist_ok=True)

    # Create a simple activate script
    with open(activate_script, "w") as f:
        f.write("# Mock activate script\n")
        f.write(f'export VIRTUAL_ENV="{venv_path}"\n')

    # Make it executable on Unix-like systems
    if sys.platform != "win32":
        os.chmod(activate_script, 0o755)

    # Create a mock Python executable
    python_exe = os.path.join(bin_dir, "python")
    if sys.platform == "win32":
        python_exe += ".exe"

    # Create a simple Python script that returns version when called with --version
    with open(python_exe, "w") as f:
        f.write("#!/bin/sh\n")
        f.write('if [ "$1" = "--version" ]; then\n')
        f.write('    echo "Python 3.9.0"  # Mock Python version\n')
        f.write("    exit 0\n")
        f.write("fi\n")
        f.write('echo "Python command not implemented in mock" >&2\n')
        f.write("exit 1\n")

    # Make the script executable
    os.chmod(python_exe, 0o755)

    # Also create a python3 symlink on Unix-like systems
    if sys.platform != "win32":
        os.symlink("python", os.path.join(bin_dir, "python3"))


@pytest.fixture
def temp_project():
    """Create a temporary project directory with a virtual environment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create a simple Python file
        (project_path / "main.py").write_text("print('Hello, World!')\n")

        # Create a requirements.txt
        (project_path / "requirements.txt").write_text("pytest\nblack\n")

        yield project_path


@pytest.fixture
def venv_project(temp_project):
    """Create a project with a virtual environment."""
    venv_path = temp_project / ".venv"
    create_mock_venv(str(venv_path), sys.executable)
    return temp_project


def test_virtualenv_detection(venv_project):
    """Test that virtual environments are properly detected."""
    detector = ProjectCommandDetector(project_path=venv_project)

    # Check that the virtual environment was detected
    assert "exists" in detector.venv_info
    assert detector.venv_info["exists"] is True
    assert "path" in detector.venv_info
    assert str(venv_project / ".venv") in detector.venv_info["path"]

    # Check that the Python path is set correctly
    if sys.platform == "win32":
        expected_python = os.path.join(
            detector.venv_info["path"], "Scripts", "python.exe"
        )
    else:
        expected_python = os.path.join(detector.venv_info["path"], "bin", "python")

    assert detector.venv_info.get("python_path") == expected_python


def test_execute_command_in_venv(venv_project):
    """Test executing a command in a virtual environment."""
    detector = ProjectCommandDetector(project_path=venv_project)

    # Test running a Python command that should use the virtual environment's Python
    result = detector.run_in_venv(["python", "--version"])

    # The command should succeed
    assert result["success"] is True
    assert result["return_code"] == 0

    # The output should contain the Python version
    assert "Python" in result["stdout"]


def test_execute_command_with_env_vars(venv_project):
    """Test executing a command with custom environment variables."""
    detector = ProjectCommandDetector(project_path=venv_project)

    # Test with custom environment variables
    env_vars = {"CUSTOM_VAR": "test_value"}

    # Create a temporary Python script to test environment variables
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
import os
print(os.environ.get("CUSTOM_VAR", "NOT_FOUND"), end="")
"""
        )
        script_path = f.name

    try:
        # Execute the script with the custom environment
        cmd = [sys.executable, script_path]

        print(f"Executing command: {cmd}")
        print(f"Environment: {env_vars}")

        result = detector.execute_command(cmd, env=env_vars)

        print(f"Command result: {result}")
        print(f"stdout: {result.get('stdout')}")
        print(f"stderr: {result.get('stderr')}")

        # The command should succeed and the output should contain our variable
        assert (
            result["success"] is True
        ), f"Command failed with return code {result.get('return_code')}"
        assert (
            result["return_code"] == 0
        ), f"Expected return code 0, got {result.get('return_code')}"
        assert (
            "test_value" in (result.get("stdout") or "").strip()
        ), f"Expected 'test_value' in stdout, got: {result.get('stdout')}"
    finally:
        # Clean up the temporary file
        try:
            os.unlink(script_path)
        except OSError:
            # File might have been deleted or not exist
            pass


def test_missing_virtualenv(temp_project):
    """Test behavior when no virtual environment is present."""
    # Create a detector in a project without a virtual environment
    detector = ProjectCommandDetector(project_path=temp_project)

    # The virtual environment should not be detected
    assert "exists" in detector.venv_info
    assert detector.venv_info["exists"] is False

    # Running a command should still work
    if sys.platform == "win32":
        cmd = ["cmd", "/c", "echo Hello"]
    else:
        cmd = ["echo", "Hello"]

    result = detector.run_in_venv(cmd)
    assert result["success"] is True
    assert "Hello" in result["stdout"]


def test_custom_venv_path(temp_project):
    """Test specifying a custom virtual environment path."""
    # Create a virtual environment in a custom location
    custom_venv = temp_project / "custom_venv"
    create_mock_venv(str(custom_venv), sys.executable)

    # Create a detector with the custom virtual environment
    detector = ProjectCommandDetector(
        project_path=temp_project, venv_path=str(custom_venv)
    )

    # The specified virtual environment should be detected
    assert detector.venv_info["exists"] is True
    assert str(custom_venv) in detector.venv_info["path"]

    # Running a command should work with the custom virtual environment
    result = detector.run_in_venv(["python", "--version"])
    assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
