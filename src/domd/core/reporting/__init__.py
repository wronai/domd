"""
Reporting module for the domd package.

This module provides functionality for generating various types of reports,
including command execution summaries, test results, and code analysis reports.
It supports multiple output formats and provides flexible formatting options.

Key Components:
- Reporter: Main class for managing and generating reports
- BaseFormatter: Abstract base class for all formatters
- Formatters: Built-in formatters for different output formats
  - MarkdownFormatter: For Markdown output
  - JsonFormatter: For JSON output
  - ConsoleFormatter: For console/terminal output
"""

from .formatters import (
    BaseFormatter,
    ConsoleFormatter,
    JsonFormatter,
    MarkdownFormatter,
)
from .reporter import Reporter

__all__ = [
    "Reporter",
    "BaseFormatter",
    "MarkdownFormatter",
    "ConsoleFormatter",
    "JsonFormatter",
]
