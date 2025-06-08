import os
import subprocess
import sys
import venv
from pathlib import Path


def create_virtualenv(venv_dir):
    """Create a Python virtual environment."""
    print(f"Creating virtual environment in {venv_dir}...")
    venv.create(venv_dir, with_pip=True)

    # Get the Python executable from the virtual environment
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"

    return python_exe, pip_exe


def install_package(pip_exe, package_path):
    """Install the package in development mode."""
    print(f"Installing package from {package_path}...")
    subprocess.check_call([str(pip_exe), "install", "-e", str(package_path)])


def run_tests(python_exe, test_dir):
    """Run the package tests."""
    print("Running tests...")
    subprocess.check_call([str(python_exe), "-m", "pytest", "-v", str(test_dir)])


def main():
    # Set up paths
    project_root = Path(__file__).parent.parent
    venv_dir = project_root / ".venv"

    # Create virtual environment
    python_exe, pip_exe = create_virtualenv(venv_dir)

    # Install the package in development mode
    install_package(pip_exe, project_root)

    # Run tests
    test_dir = project_root / "tests"
    if test_dir.exists():
        run_tests(python_exe, test_dir)
    else:
        print(f"No tests found in {test_dir}")

    print("\nInstallation and testing completed successfully!")
    print(f"Virtual environment: {venv_dir}")
    print(f"Python executable: {python_exe}")


if __name__ == "__main__":
    main()
