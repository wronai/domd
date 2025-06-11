"""Handler for executing and managing project commands."""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...services.command_runner import CommandRunner
from ..models import Command, CommandResult

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handler for executing and managing project commands."""

    def __init__(
        self,
        project_path: Path,
        command_runner: CommandRunner,
        timeout: int = 60,
        ignore_patterns: Optional[List[str]] = None,
    ):
        """Initialize the CommandHandler.

        Args:
            project_path: Path to the project root
            command_runner: CommandRunner instance for executing commands
            timeout: Default command execution timeout in seconds
            ignore_patterns: List of command patterns to ignore
        """
        self.project_path = project_path
        self.command_runner = command_runner
        self.timeout = timeout
        self.ignore_patterns = ignore_patterns or []

        # Command storage - can contain both Command objects and dictionaries
        self.failed_commands: List[Union[Command, Dict[str, Any]]] = []
        self.successful_commands: List[Union[Command, Dict[str, Any]]] = []
        self.ignored_commands: List[Union[Command, Dict[str, Any]]] = []

    def test_commands(self, commands: List[Union[Command, Dict]]) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        self.failed_commands = []
        self.successful_commands = []
        self.ignored_commands = []

        for cmd in commands:
            try:
                # Handle both Command objects and dictionaries
                if self.should_ignore_command(cmd):
                    self._handle_ignored_command(cmd)
                    continue

                # Execute the command
                result = self.execute_single_command(cmd)

                # Update command state based on result
                if result.get("success"):
                    self._handle_successful_command(cmd, result)
                else:
                    self._handle_failed_command(cmd, result)

            except Exception as e:
                logger.error(f"Error testing command: {e}", exc_info=True)
                self._handle_error(cmd, str(e))

    def execute_single_command(self, cmd_info: Union[Command, Dict]) -> Dict[str, Any]:
        """Execute a single command and return the result.

        Args:
            cmd_info: Either a Command object or a dictionary containing command info

        Returns:
            Dictionary with command execution results
        """
        if isinstance(cmd_info, Command):
            command = cmd_info.command
            cwd = cmd_info.metadata.get("cwd", self.project_path)
            env = cmd_info.metadata.get("env", {})
            timeout = cmd_info.metadata.get("timeout", self.timeout)
        else:
            command = cmd_info.get("command", "")
            cwd = cmd_info.get("cwd", self.project_path)
            env = cmd_info.get("env", {})
            timeout = cmd_info.get("timeout", self.timeout)

        try:
            start_time = time.time()
            result = self.command_runner.run(
                command=command,
                cwd=cwd,
                env=env,
                timeout=timeout,
            )
            execution_time = time.time() - start_time

            return {
                "success": result.return_code == 0,
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return {
                "success": False,
                "return_code": -1,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
            }

    def should_ignore_command(self, command: Union[str, Dict, Command]) -> bool:
        """Check if a command should be ignored based on ignore patterns.

        Args:
            command: Command to check (string, dict, or Command object)

        Returns:
            True if the command should be ignored, False otherwise
        """
        if not self.ignore_patterns:
            return False

        cmd_str = self._extract_command_string(command)
        if not cmd_str:
            return False

        return any(pattern in cmd_str for pattern in self.ignore_patterns)

    def _extract_command_string(self, command: Union[str, Dict, Command]) -> str:
        """Extract the command string from various input types."""
        if isinstance(command, str):
            return command
        if isinstance(command, dict):
            return command.get("command", "")
        if hasattr(command, "command"):
            return command.command
        return str(command)

    def _handle_ignored_command(self, command: Union[Command, Dict]) -> None:
        """Handle a command that should be ignored."""
        if isinstance(command, dict):
            command["ignored"] = True
        else:
            setattr(command, "ignored", True)
        self.ignored_commands.append(command)
        logger.debug(f"Ignored command: {self._extract_command_string(command)}")

    def _handle_successful_command(
        self, command: Union[Command, Dict], result: Dict[str, Any]
    ) -> None:
        """Handle a successfully executed command."""
        self._update_command_result(command, result, success=True)
        self.successful_commands.append(command)
        logger.debug(f"Command succeeded: {self._extract_command_string(command)}")

    def _handle_failed_command(
        self, command: Union[Command, Dict], result: Dict[str, Any]
    ) -> None:
        """Handle a failed command execution."""
        self._update_command_result(command, result, success=False)
        self.failed_commands.append(command)
        logger.warning(f"Command failed: {self._extract_command_string(command)}")

    def _handle_error(self, command: Union[Command, Dict], error: str) -> None:
        """Handle an error during command execution."""
        result = {
            "success": False,
            "error": error,
            "return_code": -1,
            "stdout": "",
            "stderr": error,
        }
        self._update_command_result(command, result, success=False)
        self.failed_commands.append(command)
        logger.error(f"Error executing command: {error}")

    def _update_command_result(
        self, command: Union[Command, Dict], result: Dict[str, Any], success: bool
    ) -> None:
        """Update a command object with execution results."""
        if isinstance(command, dict):
            command.update(
                {
                    "success": success,
                    "return_code": result.get("return_code", -1),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "error": result.get("error"),
                    "execution_time": result.get("execution_time", 0),
                }
            )
        else:
            command.success = success
            command.return_code = result.get("return_code", -1)
            command.stdout = result.get("stdout", "")
            command.stderr = result.get("stderr", "")
            command.error = result.get("error")
            command.execution_time = result.get("execution_time", 0)
