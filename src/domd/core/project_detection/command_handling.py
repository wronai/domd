"""Command handling for project command detection."""

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.command_execution import CommandRunner
from domd.core.commands import Command
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

        # Load commands that should be executed in Docker container
        self.docker_commands = {}
        docker_file_path = self.project_path / ".dodocker"
        if docker_file_path.exists():
            try:
                with open(docker_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Check if line starts with 'docker:'
                            if line.startswith("docker:"):
                                # Extract the actual command after 'docker:'
                                command = line[7:].strip()
                                self.docker_commands[command] = True
                            else:
                                # Regular command, store with False to indicate it shouldn't run in Docker
                                self.docker_commands[line] = False

                docker_count = sum(1 for v in self.docker_commands.values() if v)
                logger.info(
                    f"Loaded {len(self.docker_commands)} commands from {docker_file_path} "
                    f"({docker_count} to run in Docker)"
                )
            except Exception as e:
                logger.error(f"Error loading .dodocker commands: {e}")

        # Command storage - może zawierać zarówno obiekty Command jak i słowniki
        self.failed_commands: List[Union[Command, Dict[str, Any]]] = []
        self.successful_commands: List[Union[Command, Dict[str, Any]]] = []
        self.ignored_commands: List[Union[Command, Dict[str, Any]]] = []

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
                logger.info(f"Command succeeded in {result.execution_time:.2f} s")
                self.successful_commands.append(result_dict)
            else:
                logger.error(f"Command failed with code {result.return_code}")
                if result.stderr:
                    logger.error(
                        f"Error output: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}"  # noqa: E231
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
        venv_path = venv_env.get("VIRTUAL_ENV")
        if venv_path and cmd_list and cmd_list[0] in ("python", "python3"):
            # Try to find the Python executable in the virtualenv
            import os
            import sys

            if sys.platform == "win32":
                bin_dir = "Scripts"
                python_exe = "python.exe"
            else:
                bin_dir = "bin"
                python_exe = "python"

            python_path = os.path.join(venv_path, bin_dir, python_exe)
            if os.path.isfile(python_path):
                cmd_list[0] = python_path
            else:
                # Fallback to the Python executable in the virtualenv's bin directory
                python_path = os.path.join(
                    venv_path,
                    bin_dir,
                    f"python{sys.version_info.major}.{sys.version_info.minor}",
                )
                if os.path.isfile(python_path):
                    cmd_list[0] = python_path

        # Merge environments, with user-provided env taking precedence
        env = kwargs.pop("env", {})
        merged_env = venv_env.copy()
        merged_env.update({k: str(v) for k, v in env.items() if v is not None})

        # Run the command using the command runner
        result = self.command_runner.run(command=cmd_list, env=merged_env, **kwargs)

        # Convert result to dictionary for backward compatibility
        result_dict = {
            "success": result.success,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "command": " ".join(cmd_list) if isinstance(cmd_list, list) else cmd_list,
            "output": (result.stdout or "")
            + ("\n" + result.stderr if result.stderr else ""),
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
            self.pattern_matcher.match_command(command_str, self.ignore_patterns)
            if self.ignore_patterns
            else False
        )

    def should_run_in_docker(self, command: str) -> bool:
        """Check if a command should be run in Docker based on .dodocker file.

        Args:
            command: Command string to check

        Returns:
            bool: True if the command should be run in Docker, False otherwise
        """
        if not self.docker_commands:
            return False

        # Check for exact match first
        if command in self.docker_commands:
            return self.docker_commands[command]

        # Check for pattern match only for commands explicitly marked with docker:
        docker_patterns = [
            cmd for cmd, use_docker in self.docker_commands.items() if use_docker
        ]
        return self.pattern_matcher.match_command(command, docker_patterns)

    def execute_single_command(self, cmd_info) -> bool:
        """Execute a single command and update the command info with results.

        Args:
            cmd_info: Either a Command object or a dictionary containing command information

        Returns:
            bool: True if command executed successfully, False otherwise
        """
        if hasattr(cmd_info, "command"):  # It's a Command object
            command = cmd_info.command
            # Get cwd from metadata if available, otherwise fall back to project_path
            cwd = (
                Path(cmd_info.metadata.get("cwd"))
                if hasattr(cmd_info, "metadata")
                and hasattr(cmd_info.metadata, "get")
                and callable(cmd_info.metadata.get)
                and cmd_info.metadata.get("cwd")
                else getattr(cmd_info, "cwd", self.project_path)
            )
            timeout = getattr(cmd_info, "timeout", self.timeout)
            env = getattr(cmd_info, "env", None)
        else:  # It's a dictionary
            command = cmd_info.get("command", "")
            # Get cwd from metadata if available, otherwise fall back to project_path
            cwd = (
                Path(cmd_info.get("metadata", {}).get("cwd", self.project_path))
                if isinstance(cmd_info.get("metadata"), dict)
                else Path(self.project_path)
            )
            timeout = cmd_info.get("timeout", self.timeout)
            env = cmd_info.get("env", None)

        # Ensure cwd is a Path object and resolve it relative to project_path if it's relative
        cwd = Path(cwd)
        if not cwd.is_absolute():
            cwd = self.project_path / cwd
        cwd = cwd.resolve()

        # Sprawdź, czy komenda powinna być wykonana w kontenerze Docker
        use_docker = self.should_run_in_docker(command)
        if use_docker:
            logger.info(f"Executing command in Docker: {command}")
            # Przygotuj komendę do wykonania w kontenerze Docker
            docker_command = f'docker run --rm -v {self.project_path}:/app -w /app python:3.9 sh -c "{command}"'  # noqa: E231
            command = docker_command

        logger.info("Executing command: %s", command)

        try:
            # Execute the command through the command runner
            result = self.command_runner.run(
                command=command,  # noqa: E221
                timeout=timeout,  # noqa: E221
                cwd=cwd,  # noqa: E221
                env=env,
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
                    cmd_source = (
                        cmd.source
                        if hasattr(cmd, "source")
                        else cmd.get("source", "unknown")
                    )
                    logger.info("Ignoring command from %s: %s", cmd_source, cmd)
                    self.ignored_commands.append(cmd)
                    continue

                # Make a copy of the command to avoid modifying the original
                if isinstance(cmd, dict):
                    cmd_copy = cmd.copy()
                    # Ensure metadata exists
                    if "metadata" not in cmd_copy:
                        cmd_copy["metadata"] = {}
                else:
                    # For Command objects, create a shallow copy
                    cmd_copy = type(cmd)(**cmd.__dict__)
                    # Ensure metadata exists
                    if not hasattr(cmd_copy, "metadata") or cmd_copy.metadata is None:
                        setattr(cmd_copy, "metadata", {})

                # Execute the command and get the full result
                success = self.execute_single_command(cmd_copy)

                # Set success flag and error information
                if isinstance(cmd_copy, dict):
                    # Ensure we have all required fields for the test
                    if "source" not in cmd_copy:
                        cmd_copy["source"] = cmd_copy.get("file", "unknown")

                    # Preserve the cwd in the output for reference
                    cwd = cmd_copy.get("metadata", {}).get("cwd", self.project_path)
                    if cwd != self.project_path:
                        cmd_copy["source"] = f"{cwd}/{cmd_copy['source']}"

                    # If command failed but no error was set, set a default error message
                    if not success and not cmd_copy.get("error"):
                        cmd_copy["error"] = cmd_copy.get("stderr") or "Command failed"

                    # Ensure success flag is set
                    cmd_copy["success"] = success
                else:
                    # For Command objects
                    if not hasattr(cmd_copy, "source"):
                        setattr(
                            cmd_copy, "source", getattr(cmd_copy, "file", "unknown")
                        )

                    # Preserve the cwd in the output for reference
                    cwd = (
                        cmd_copy.metadata.get("cwd")
                        if hasattr(cmd_copy, "metadata")
                        and hasattr(cmd_copy.metadata, "get")
                        and callable(cmd_copy.metadata.get)
                        else self.project_path
                    )
                    if cwd != self.project_path:
                        setattr(cmd_copy, "source", f"{cwd}/{cmd_copy.source}")

                    # If command failed but no error was set, set a default error message
                    if not success and not hasattr(cmd_copy, "error"):
                        error_msg = (
                            getattr(cmd_copy, "stderr", None) or "Command failed"
                        )
                        setattr(cmd_copy, "error", error_msg)

                    # Ensure success flag is set
                    setattr(cmd_copy, "success", success)

                # Add to appropriate list
                if success:
                    self.successful_commands.append(cmd_copy)
                else:
                    self.failed_commands.append(cmd_copy)
                    # Get command and error, handling both dict and Command object
                    cmd_str = (
                        cmd_copy.get("command", "")
                        if isinstance(cmd_copy, dict)
                        else getattr(cmd_copy, "command", "")
                    )
                    error_msg = (
                        cmd_copy.get("error", "Unknown error")
                        if isinstance(cmd_copy, dict)
                        else getattr(cmd_copy, "error", "Unknown error")
                    )
                    logger.warning(f"Command failed: {cmd_str} - {error_msg}")

                # Update original command with results
                if isinstance(cmd, dict) and isinstance(cmd_copy, dict):
                    cmd.update(cmd_copy)
                elif hasattr(cmd, "__dict__") and hasattr(cmd_copy, "__dict__"):
                    # Update the original command's attributes
                    for k, v in cmd_copy.__dict__.items():
                        setattr(cmd, k, v)

            except Exception as e:
                logger.error("Error testing command: %s", e, exc_info=True)
                error_msg = str(e)
                if hasattr(cmd, "command"):  # Command object
                    setattr(cmd, "error", error_msg)
                    setattr(cmd, "success", False)
                    if not hasattr(cmd, "source"):
                        setattr(cmd, "source", "unknown")
                else:  # Dictionary
                    cmd["error"] = error_msg
                    cmd["success"] = False
                    if "source" not in cmd:
                        cmd["source"] = "unknown"
                self.failed_commands.append(cmd)
