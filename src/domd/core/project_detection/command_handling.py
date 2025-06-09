"""Command handling for project command detection."""

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.command_execution import CommandResult, CommandRunner
from domd.parsing import PatternMatcher

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
        self.pattern_matcher = PatternMatcher()

        # Command storage
        self.failed_commands: List[Dict[str, Any]] = []
        self.successful_commands: List[Dict[str, Any]] = []
        self.ignored_commands: List[Dict[str, Any]] = []

    def execute_command(
        self,
        command: Union[str, List[str]],
        timeout: Optional[int] = None,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = False,
    ) -> Dict[str, Any]:
        """Execute a command with proper environment setup.

        Args:
            command: Command to execute (string or list of args)
            timeout: Optional timeout in seconds
            cwd: Working directory for the command
            env: Additional environment variables to include
            check: If True, raises an exception on non-zero exit code

        Returns:
            Dictionary with command execution results
        """
        # Ensure command is a string for logging
        command_str = command if isinstance(command, str) else " ".join(command)
        logger.info(f"Executing command: {command_str}")

        # Execute the command using the CommandRunner
        try:
            result = self.command_runner.run(
                command=command,
                timeout=timeout or self.timeout,
                cwd=cwd or self.project_path,
                env=env,
                check=check,
            )

            # Convert result to dictionary for backward compatibility
            result_dict = {
                "success": result.success,
                "return_code": result.return_code,
                "execution_time": result.execution_time,
                "output": (result.stdout or "") + "\n" + (result.stderr or ""),
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "command": command_str,
            }

            # Log the result
            if result.success:
                logger.info(f"Command succeeded in {result.execution_time:.2f}s")
                self.successful_commands.append(result_dict)
            else:
                logger.error(f"Command failed with code {result.return_code}")
                if result.stderr:
                    logger.error(
                        f"Error output: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}"
                    )
                self.failed_commands.append(result_dict)

            return result_dict

        except Exception as e:
            # Handle any exceptions and return a consistent result dictionary
            error_msg = str(e)
            logger.error(f"Error executing command: {error_msg}")

            result_dict = {
                "success": False,
                "return_code": -1,
                "execution_time": 0.0,
                "output": error_msg,
                "stdout": "",
                "stderr": error_msg,
                "command": command_str,
            }

            self.failed_commands.append(result_dict)
            return result_dict

    def run_in_venv(
        self, command: Union[str, List[str]], venv_env: Dict[str, str], **kwargs
    ) -> Dict[str, Any]:
        """Run a command in the virtual environment.

        Args:
            command: Command to execute (string or list of arguments)
            venv_env: Environment variables with virtualenv paths included
            **kwargs: Additional arguments to pass to execute_command

        Returns:
            Dictionary with command execution results
        """
        # Ensure command is a list for easier manipulation
        cmd_list = command if isinstance(command, list) else shlex.split(str(command))

        # If we have a Python path in the environment, use it for Python commands
        python_path = venv_env.get("VIRTUAL_ENV")
        if python_path:
            if cmd_list and cmd_list[0] in ("python", "python3"):
                # Try to find the Python executable in the virtualenv
                import os
                import sys

                if sys.platform == "win32":
                    bin_dir = "Scripts"
                    python_exe = "python.exe"
                else:
                    bin_dir = "bin"
                    python_exe = "python"

                python_path = os.path.join(python_path, bin_dir, python_exe)
                if os.path.isfile(python_path):
                    cmd_list[0] = python_path

        # Merge environments, with user-provided env taking precedence
        env = kwargs.pop("env", None) or {}
        merged_env = venv_env.copy()

        for key, value in env.items():
            if value is not None:
                merged_env[str(key)] = str(value)
            elif key in merged_env:
                del merged_env[key]

        # Run the command using the command runner
        result = self.command_runner.run(command=cmd_list, env=merged_env, **kwargs)

        # Convert result to dictionary for backward compatibility
        result_dict = {
            "success": result.success,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "command": cmd_list if isinstance(cmd_list, str) else " ".join(cmd_list),
            "output": (result.stdout or "") + "\n" + (result.stderr or ""),
        }

        return result_dict

    def should_ignore_command(self, cmd) -> bool:
        """Check if a command should be ignored based on ignore rules.

        Args:
            cmd: Either a Command object or a dictionary containing command information

        Returns:
            bool: True if command should be ignored
        """
        # Convert Command object to dict if needed
        if hasattr(cmd, "to_dict"):
            cmd_dict = cmd.to_dict()
        else:
            cmd_dict = cmd

        # Check ignore patterns using PatternMatcher
        command_str = cmd_dict.get("command", "")
        return (
            self.pattern_matcher.match_any_pattern(command_str, self.ignore_patterns)
            if self.ignore_patterns
            else False
        )

    def execute_single_command(self, cmd_info) -> bool:
        """Execute a single command and update the command info with results.

        Args:
            cmd_info: Either a Command object or a dictionary containing command information

        Returns:
            bool: True if command executed successfully, False otherwise
        """
        if hasattr(cmd_info, "command"):  # It's a Command object
            command = cmd_info.command
            cwd = getattr(cmd_info, "cwd", self.project_path)
            timeout = getattr(cmd_info, "timeout", self.timeout)
            env = getattr(cmd_info, "env", None)
        else:  # It's a dictionary
            command = cmd_info.get("command", "")
            cwd = str(cmd_info.get("cwd", self.project_path))
            timeout = cmd_info.get("timeout", self.timeout)
            env = cmd_info.get("env", None)

        logger.info("Executing command: %s", command)

        try:
            # Execute the command through the command runner
            result = self.command_runner.run(
                command=command, timeout=timeout, cwd=cwd, env=env
            )

            # Update command info with results
            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "execution_time", result.execution_time)
                setattr(cmd_info, "stdout", result.stdout)
                setattr(cmd_info, "stderr", result.stderr)
                setattr(cmd_info, "return_code", result.return_code)
                setattr(cmd_info, "success", result.success)
                if not result.success:
                    setattr(cmd_info, "error", result.stderr or "Command failed")
            else:  # Dictionary
                cmd_info.update(
                    {
                        "execution_time": result.execution_time,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.return_code,
                        "success": result.success,
                    }
                )
                if not result.success:
                    cmd_info["error"] = result.stderr or "Command failed"

            return result.success

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {e.timeout} seconds"
            logger.error(error_msg)

            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "error", error_msg)
                setattr(cmd_info, "return_code", -1)
                setattr(cmd_info, "success", False)
            else:  # Dictionary
                cmd_info.update(
                    {"error": error_msg, "return_code": -1, "success": False}
                )
            return False

        except Exception as e:
            error_msg = str(e)
            logger.error("Error executing command '%s': %s", command, error_msg)

            if hasattr(cmd_info, "command"):  # Command object
                setattr(cmd_info, "error", str(e))
                setattr(cmd_info, "success", False)
            else:  # Dictionary
                cmd_info["error"] = str(e)
                cmd_info["success"] = False
            return False

    def test_commands(self, commands: List) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        self.failed_commands = []
        self.successful_commands = []
        self.ignored_commands = []

        for cmd in commands:
            try:
                # Check if command should be ignored
                if self.should_ignore_command(cmd):
                    logger.info("Ignoring command: %s", cmd)
                    self.ignored_commands.append(cmd)
                    continue

                # Execute the command
                success = self.execute_single_command(cmd)
                if success:
                    self.successful_commands.append(cmd)
                else:
                    self.failed_commands.append(cmd)
            except Exception as e:
                logger.error("Error testing command: %s", e, exc_info=True)
                if hasattr(cmd, "command"):  # Command object
                    setattr(cmd, "error", str(e))
                    setattr(cmd, "success", False)
                else:  # Dictionary
                    cmd["error"] = str(e)
                    cmd["success"] = False
                self.failed_commands.append(cmd)
