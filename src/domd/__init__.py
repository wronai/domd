"""
TodoMD Package

Automatically detects and tests project commands from various configuration files,
generates TODO.md for failed commands with detailed error reports.

Supports: Makefile, package.json, pyproject.toml, Docker, CI/CD workflows, and more.
"""

__version__ = "2.2.56"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"
__license__ = "Apache-2.0"

from typing import Callable, TypeVar

from .core.project_detection.detector import ProjectCommandDetector

# Define a type variable for the main function
F = TypeVar("F", bound=Callable[..., int])

# Import main function from cli module
try:
    from .cli import main
except ImportError:
    # Fallback main function if cli import fails
    def main() -> int:
        """Fallback main function.

        Returns:
            int: Exit code (1 for error)
        """
        print("Error: Could not import CLI module.")
        print(
            "Please check your installation and ensure all dependencies are installed."
        )
        return 1


__all__ = [
    "ProjectCommandDetector",
    "main",
    "__version__",
]
