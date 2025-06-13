"""Command execution functionality for the domd package."""

import logging
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from domd.utils.path_utils import safe_path_display, to_relative_path

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    return_code: int
    execution_time: float
    stdout: str
    stderr: str
    command: str

    @property
    def output(self) -> str:
        """Get combined stdout and stderr output."""
        return f"{self.stdout}\n{self.stderr}"


class CommandExecutor:
    """Handles execution of shell commands with timeout and environment support."""

    def __init__(
        self,
        timeout: int = 60,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        """Initialize the CommandExecutor.

        Args:
            timeout: Default timeout in seconds for command execution
            cwd: Current working directory for commands
            env: Environment variables to use for command execution
        """
        self.timeout = timeout
        self.cwd = Path(cwd).resolve() if cwd else Path.cwd()
        self.env = env or {}

    def _log_command_start(self, command_str: str, work_dir: Union[str, Path]) -> None:
        """Log command execution start with proper path handling."""
        logger.debug(
            "Executing command: %s in %s", command_str, safe_path_display(work_dir)
        )

    def _create_command_result(
        self,
        success: bool,
        return_code: int,
        start_time: float,
        stdout: str = "",
        stderr: str = "",
        command_str: str = "",
        error: Optional[Exception] = None,
    ) -> CommandResult:
        """Create a CommandResult with proper timing and error handling."""
        execution_time = time.monotonic() - start_time

        if error is not None:
            if not stderr:
                stderr = str(error)
            logger.debug(
                "Command error after %.2fs: %s",
                execution_time,
                stderr,
                exc_info=isinstance(error, Exception)
                and not isinstance(
                    error, (subprocess.CalledProcessError, subprocess.TimeoutExpired)
                ),
            )

        return CommandResult(
            success=success,
            return_code=return_code,
            execution_time=execution_time,
            stdout=stdout,
            stderr=stderr,
            command=command_str,
        )

    def execute(
        self,
        command: Union[str, List[str]],
        timeout: Optional[int] = None,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = False,
    ) -> CommandResult:
        """Execute a shell command.

        Args:
            command: Command to execute (string or list of args)
            timeout: Timeout in seconds (overrides default)
            cwd: Working directory (overrides default)
            env: Additional environment variables
            check: If True, raises CalledProcessError on non-zero exit code

        Returns:
            CommandResult with execution details

        Raises:
            subprocess.CalledProcessError: If check=True and command fails
            subprocess.TimeoutExpired: If command times out
        """
        import time
        from subprocess import CalledProcessError, TimeoutExpired

        # Prepare command and environment
        cmd_str = command if isinstance(command, str) else " ".join(map(str, command))
        cmd_args = (
            command if isinstance(command, (list, tuple)) else shlex.split(cmd_str)
        )

        # Prepare environment
        exec_env = dict(os.environ)
        exec_env.update(self.env)
        if env:
            exec_env.update(env)

        # Set working directory
        work_dir = Path(cwd).resolve() if cwd else self.cwd
        self._log_command_start(cmd_str, work_dir)
        start_time = time.monotonic()

        try:
            # Run the command
            result = subprocess.run(
                cmd_args,
                cwd=work_dir,
                env=exec_env,
                timeout=timeout or self.timeout,
                capture_output=True,
                text=True,
                check=check,
            )

            return self._create_command_result(
                success=result.returncode == 0,
                return_code=result.returncode,
                start_time=start_time,
                stdout=result.stdout,
                stderr=result.stderr,
                command_str=cmd_str,
            )

        except TimeoutExpired as e:
            result = self._create_command_result(
                success=False,
                return_code=-1,
                start_time=start_time,
                stderr=f"Command timed out after {self.timeout} seconds",
                command_str=cmd_str,
                error=e,
            )
            logger.error(
                "Command timed out after %.2f seconds: %s",
                result.execution_time,
                safe_path_display(cmd_str),
            )
            if check:
                raise
            return result

        except CalledProcessError as e:
            result = self._create_command_result(
                success=False,
                return_code=e.returncode,
                start_time=start_time,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                command_str=cmd_str,
                error=e,
            )

            logger.error(
                "Command failed with code %d in %.2f seconds: %s",
                e.returncode,
                result.execution_time,
                safe_path_display(cmd_str),
            )

            if e.stderr:
                logger.error("Error output: %s", e.stderr.strip())

            if check:
                raise
            return result

        except Exception as e:
            result = self._create_command_result(
                success=False,
                return_code=-1,
                start_time=start_time,
                stderr=str(e),
                command_str=cmd_str,
                error=e,
            )

            logger.error(
                "Unexpected error executing command (%.2fs): %s",
                result.execution_time,
                safe_path_display(cmd_str),
                exc_info=True,
            )

            if check:
                raise
            return result
