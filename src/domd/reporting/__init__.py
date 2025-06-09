"""
Reporting module for the domd package.

This module is a backward compatibility layer that imports and re-exports
classes from the core.reporting module.
"""

from domd.core.reporting import (
    BaseFormatter,
    ConsoleFormatter,
    JsonFormatter,
    MarkdownFormatter,
    Reporter,
)

__all__ = [
    "Reporter",
    "BaseFormatter",
    "MarkdownFormatter",
    "ConsoleFormatter",
    "JsonFormatter",
]
