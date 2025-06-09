"""Command execution functionality for the domd package."""

import logging
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

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

        logger.debug("Executing command: %s", cmd_str)
        logger.debug("Working directory: %s", work_dir)

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

            elapsed = time.monotonic() - start_time

            return CommandResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                execution_time=elapsed,
                stdout=result.stdout,
                stderr=result.stderr,
                command=cmd_str,
            )

        except TimeoutExpired as e:
            elapsed = time.monotonic() - start_time
            logger.error("Command timed out after %.2f seconds: %s", elapsed, cmd_str)
            raise

        except CalledProcessError as e:
            elapsed = time.monotonic() - start_time
            logger.error(
                "Command failed with code %d in %.2f seconds: %s",
                e.returncode,
                elapsed,
                cmd_str,
            )
            if e.stderr:
                logger.error("Error output: %s", e.stderr.strip())
            raise

        except Exception as e:
            elapsed = time.monotonic() - start_time
            logger.exception(
                "Unexpected error executing command (%.2fs): %s",
                elapsed,
                cmd_str,
            )
            raise
