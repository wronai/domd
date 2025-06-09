"""
Command execution module for the domd package.

This module is a backward compatibility layer that imports and re-exports
classes from the core.command_execution module.
"""

from domd.core.command_execution import (
    CommandContext,
    CommandExecutor,
    CommandResult,
    CommandRunner,
)

__all__ = ["CommandExecutor", "CommandResult", "CommandContext", "CommandRunner"]
