"""
Core functionality for the domd package.

This package provides the core components for the domd tool, which helps with
discovering, organizing, and executing project-specific commands from various
configuration files.

Submodules:
- command_execution: For executing commands with timeouts and retries
- parsing: For parsing configuration files and extracting commands
- reporting: For generating reports on command execution and results
- utils: Utility functions and helpers

Key Components:
- ProjectCommandDetector: Main entry point for discovering project commands
- CommandExecutor/Runner: For executing commands with various options
- ParserRegistry: For managing different configuration file parsers
- Reporter: For generating reports in various formats
"""

# Import submodules to make them available as domd.core.<submodule>
from . import command_execution, parsing, reporting, utils

# Re-export commonly used components
from .command_execution import (
    CommandContext,
    CommandExecutor,
    CommandResult,
    CommandRunner,
)
from .parsing import BaseParser, FileProcessor, ParserRegistry, PatternMatcher

# Import main components from submodules
from .project_detection.detector import ProjectCommandDetector  # Main entry point
from .reporting import (
    BaseFormatter,
    ConsoleFormatter,
    JsonFormatter,
    MarkdownFormatter,
    Reporter,
)

__all__ = [
    # Main entry point
    "ProjectCommandDetector",
    # Submodules
    "command_execution",
    "parsing",
    "reporting",
    "utils",
    # Command execution components
    "CommandExecutor",
    "CommandRunner",
    "CommandResult",
    "CommandContext",
    # Parsing components
    "BaseParser",
    "ParserRegistry",
    "FileProcessor",
    "PatternMatcher",
    # Reporting components
    "Reporter",
    "BaseFormatter",
    "MarkdownFormatter",
    "ConsoleFormatter",
    "JsonFormatter",
]
