"""Pattern matching utilities for file and command patterns."""

import fnmatch
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Union

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Handles pattern matching for files and commands."""

    def __init__(self, case_sensitive: bool = False):
        """Initialize the pattern matcher.

        Args:
            case_sensitive: Whether pattern matching should be case-sensitive
        """
        self.case_sensitive = case_sensitive
        self._compiled_patterns: Dict[str, Pattern] = {}

    def match_file(
        self,
        file_path: Union[str, Path],
        patterns: Union[str, List[str]],
        default: bool = False,
    ) -> bool:
        """Check if a file path matches any of the given patterns.

        Args:
            file_path: Path to the file to check
            patterns: Pattern or list of patterns to match against
            default: Default value if no patterns are provided

        Returns:
            bool: True if the file matches any pattern, False otherwise
        """
        if not patterns:
            return default

        if isinstance(patterns, str):
            patterns = [patterns]

        file_path = str(file_path)

        for pattern in patterns:
            # Handle directory patterns with trailing /*
            if pattern.endswith("/*"):
                dir_pattern = pattern[:-2]
                if file_path.startswith(dir_pattern + "/"):
                    return True
                continue

            # Handle regex patterns
            if pattern.startswith("re:"):
                try:
                    regex = self._compile_regex(pattern[3:], fullmatch=True)
                    if regex.search(file_path):
                        return True
                except re.error as e:
                    logger.warning("Invalid regex pattern '%s': %s", pattern[3:], e)
                continue

            # Handle glob patterns
            if "*" in pattern or "?" in pattern or "[" in pattern:
                if fnmatch.fnmatch(file_path, pattern):
                    return True
                continue

            # Simple string match
            if pattern in file_path:
                return True

        return False

    def match_command(
        self, command: str, patterns: Union[str, List[str]], default: bool = False
    ) -> bool:
        """Check if a command matches any of the given patterns.

        Args:
            command: Command string to check
            patterns: Pattern or list of patterns to match against
            default: Default value if no patterns are provided

        Returns:
            bool: True if the command matches any pattern, False otherwise
        """
        if not patterns:
            return default

        if isinstance(patterns, str):
            patterns = [patterns]

        for pattern in patterns:
            # Handle regex patterns
            if pattern.startswith("re:"):
                try:
                    regex = self._compile_regex(pattern[3:], fullmatch=False)
                    if regex.search(command):
                        return True
                except re.error as e:
                    logger.warning("Invalid regex pattern '%s': %s", pattern[3:], e)
                continue

            # Handle glob patterns
            if "*" in pattern or "?" in pattern or "[" in pattern:
                if fnmatch.fnmatch(command, pattern):
                    return True
                continue

            # Simple string match
            if pattern in command:
                return True

        return False

    def _compile_regex(self, pattern: str, fullmatch: bool = False) -> Pattern:
        """Compile a regex pattern with caching.

        Args:
            pattern: Regex pattern to compile
            fullmatch: If True, the pattern must match the entire string

        Returns:
            Compiled regex pattern

        Raises:
            re.error: If the pattern is invalid
        """
        cache_key = f"{pattern}:{fullmatch}:{self.case_sensitive}"

        if cache_key in self._compiled_patterns:
            return self._compiled_patterns[cache_key]

        flags = 0 if self.case_sensitive else re.IGNORECASE

        if fullmatch:
            if not (pattern.startswith("^") and pattern.endswith("$")):
                pattern = f"^{pattern}$"

        try:
            compiled = re.compile(pattern, flags)
            self._compiled_patterns[cache_key] = compiled
            return compiled
        except re.error as e:
            logger.error("Failed to compile regex pattern '%s': %s", pattern, e)
            raise

    def filter_files(
        self,
        files: List[Union[str, Path]],
        include: Optional[Union[str, List[str]]] = None,
        exclude: Optional[Union[str, List[str]]] = None,
    ) -> List[Path]:
        """Filter a list of files based on include/exclude patterns.

        Args:
            files: List of file paths to filter
            include: Patterns to include (if None, all files are included)
            exclude: Patterns to exclude (if None, no files are excluded)

        Returns:
            Filtered list of file paths
        """
        result = []

        for file_path in map(Path, files):
            # Skip non-existent files
            if not file_path.exists() or not file_path.is_file():
                continue

            # Apply include patterns
            if include is not None and not self.match_file(
                file_path, include, default=False
            ):
                continue

            # Apply exclude patterns
            if exclude is not None and self.match_file(
                file_path, exclude, default=False
            ):
                continue

            result.append(file_path.resolve())

        return result

    def filter_commands(
        self,
        commands: List[Dict[str, Any]],
        include: Optional[Union[str, List[str]]] = None,
        exclude: Optional[Union[str, List[str]]] = None,
        command_key: str = "command",
    ) -> List[Dict[str, Any]]:
        """Filter a list of commands based on include/exclude patterns.

        Args:
            commands: List of command dictionaries
            include: Patterns to include (if None, all commands are included)
            exclude: Patterns to exclude (if None, no commands are excluded)
            command_key: Key in the command dictionary containing the command string

        Returns:
            Filtered list of command dictionaries
        """
        result = []

        for cmd in commands:
            if command_key not in cmd:
                continue

            command = cmd[command_key]

            # Apply include patterns
            if include is not None and not self.match_command(
                command, include, default=False
            ):
                continue

            # Apply exclude patterns
            if exclude is not None and self.match_command(
                command, exclude, default=False
            ):
                continue

            result.append(cmd)

        return result
