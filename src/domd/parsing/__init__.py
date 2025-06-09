"""
Parsing module for the domd package.

This module is a backward compatibility layer that imports and re-exports
classes from the core.parsing module.
"""

from domd.core.parsing import BaseParser, FileProcessor, ParserRegistry, PatternMatcher

__all__ = [
    "BaseParser",
    "ParserRegistry",
    "FileProcessor",
    "PatternMatcher",
]
