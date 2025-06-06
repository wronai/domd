"""
TodoMD Package

Automatically detects and tests project commands from various configuration files,
generates TODO.md for failed commands with detailed error reports.

Supports: Makefile, package.json, pyproject.toml, Docker, CI/CD workflows, and more.
"""

__version__ = "0.1.1"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"
__license__ = "Apache-2.0"

from .detector import ProjectCommandDetector

# Import main function from cli module
try:
    from .cli import main
except ImportError as e:
    # Fallback main function if cli import fails
    def main():
        """Fallback main function."""
        print("Error: Could not import CLI module.")
        print(f"Import error: {e}")
        print("Please check your installation.")
        return 1

__all__ = [
    "ProjectCommandDetector",
    "main",
    "__version__",
]