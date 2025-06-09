"""
Parsing module for the domd package.

This module provides functionality for parsing various configuration files
and extracting commands from them. It includes support for:

- File discovery and filtering
- Pattern matching for files and commands
- Parser registration and management
- File content processing and analysis

Key Components:
- BaseParser: Abstract base class for all parsers
- ParserRegistry: Registry for managing parser classes
- FileProcessor: Handles file operations and pattern matching
- PatternMatcher: Provides flexible pattern matching capabilities
"""

from .base import BaseParser
from .file_processor import FileProcessor
from .parser_registry import ParserRegistry
from .pattern_matcher import PatternMatcher

__all__ = [
    "BaseParser",
    "ParserRegistry",
    "FileProcessor",
    "PatternMatcher",
]
