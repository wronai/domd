"""
Command execution module for the domd package.

This module provides functionality for executing commands in a controlled environment,
including support for:
- Command execution with timeouts
- Retry logic for failed commands
- Command chaining and dependency management
- Environment variable management
- Output and error stream handling
- Process management

Key Components:
- CommandExecutor: Low-level command execution with timeout and output capture
- CommandRunner: Higher-level command execution with retries and result processing
- CommandContext: Context for command execution with environment and metadata
- CommandResult: Result of command execution with status and output
"""

from .command_executor import CommandExecutor, CommandResult
from .command_runner import CommandContext, CommandRunner

__all__ = [
    "CommandExecutor",
    "CommandResult",
    "CommandRunner",
    "CommandContext",
]
