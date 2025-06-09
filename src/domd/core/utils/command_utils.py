"""
Command-related utility functions for the domd package.

This module provides utility functions for working with shell commands,
including parsing, formatting, and splitting command strings.
"""

import shlex
from typing import List, Tuple, Union


def split_command(command: Union[str, List[str]]) -> List[str]:
    """
    Split a command string into a list of arguments.

    Args:
        command: The command string or list of arguments to split.

    Returns:
        List of command arguments.
    """
    if isinstance(command, list):
        return command
    return shlex.split(command)


def parse_command(command: str) -> Tuple[str, List[str]]:
    """
    Parse a command string into a command and its arguments.

    Args:
        command: The command string to parse.

    Returns:
        A tuple of (command, args) where command is the command name
        and args is a list of arguments.
    """
    parts = split_command(command)
    if not parts:
        return "", []
    return parts[0], parts[1:]


def format_command(command: Union[str, List[str]]) -> str:
    """
    Format a command and its arguments into a shell-escaped string.

    Args:
        command: The command as a string or list of arguments.

    Returns:
        A shell-escaped command string.
    """
    if isinstance(command, str):
        return command
    return " ".join(shlex.quote(arg) for arg in command)
