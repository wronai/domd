"""Command execution functionality for domd."""

import logging
import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    """Whether the command executed successfully (return code 0)."""

    return_code: int
    """The exit code returned by the command."""

    execution_time: float
    """Time taken to execute the command in seconds."""

    stdout: str = ""
    """Standard output of the command."""

    stderr: str = ""
    """Standard error output of the command."""

    command: str = ""
    """The command that was executed."""

    error: Optional[str] = None
    """Error message if an exception occurred."""

    environment: Dict[str, str] = field(default_factory=dict)
    """Environment variables used during command execution."""

    output: str = ""
    """Combined output (stdout + stderr) for backward compatibility."""

    def __post_init__(self):
        """Initialize derived fields after dataclass initialization."""
        if not self.output and (self.stdout or self.stderr):
            self.output = f"{self.stdout}\n{self.stderr}".strip()


class CommandExecutor:
    """Handles execution of shell commands with timeout and output capture."""

    def __init__(
        self,
        timeout: int = 60,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        """Initialize the command executor.

        Args:
            timeout: Default timeout in seconds for command execution
            cwd: Current working directory for commands
            env: Environment variables to use for command execution
        """
        self.timeout = timeout
        self.cwd = Path(cwd).resolve() if cwd else Path.cwd()
        self.env = self._prepare_environment(env or {})

    def _prepare_environment(self, custom_env: Dict[str, str]) -> Dict[str, str]:
        """Prepare the environment for command execution.

        Args:
            custom_env: Custom environment variables to include

        Returns:
            Dictionary containing the complete environment
        """
        env = os.environ.copy()

        # Update with custom environment variables
        for key, value in custom_env.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = str(value)

        # Ensure PATH is properly set
        if "PATH" not in env:
            env["PATH"] = os.defpath

        return env

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
            command: The command to execute (string or list of args)
            timeout: Optional timeout in seconds (overrides default)
            cwd: Optional working directory (overrides default)
            env: Optional environment variables to use (merged with instance env)
            check: If True, raise CalledProcessError on non-zero exit code

        Returns:
            CommandResult with execution details

        Raises:
            subprocess.CalledProcessError: If check=True and command returns non-zero
            subprocess.TimeoutExpired: If command times out
        """
        timeout = timeout or self.timeout
        cwd = Path(cwd).resolve() if cwd else self.cwd

        # Merge instance environment with command-specific environment
        exec_env = self.env.copy()
        if env:
            exec_env.update(env)

        start_time = time.time()
        command_str = command if isinstance(command, str) else " ".join(command)

        logger.debug(f"Executing command: {command_str}")
        logger.debug(f"Working directory: {cwd}")

        try:
            # Split the command into a list of arguments if it's a string
            args = shlex.split(command_str) if isinstance(command_str, str) else command

            # Log environment variables (excluding sensitive ones)
            safe_env = {
                k: "***" if "PASS" in k or "SECRET" in k or "TOKEN" in k else v
                for k, v in exec_env.items()
            }
            logger.debug(f"Environment: {safe_env}")

            # Execute the command with a timeout
            result = subprocess.run(
                args,
                shell=False,
                cwd=str(cwd),
                env=exec_env,
                timeout=timeout,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            execution_time = time.time() - start_time

            # Log command completion
            logger.debug(
                f"Command completed in {execution_time:.2f}s with return code {result.returncode}"
            )
            if result.stdout:
                logger.debug(
                    f"STDOUT: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}"
                )
            if result.stderr:
                logger.debug(
                    f"STDERR: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}"
                )

            # Create result object
            cmd_result = CommandResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                execution_time=execution_time,
                stdout=result.stdout,
                stderr=result.stderr,
                command=command_str,
                environment=exec_env,
            )

            # Raise exception if check=True and command failed
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=result.returncode,
                    cmd=args,
                    output=result.stdout,
                    stderr=result.stderr,
                )

            return cmd_result

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(error_msg)

            if check:
                raise

            return CommandResult(
                success=False,
                return_code=-1,
                execution_time=timeout,
                stdout=e.stdout or "",
                stderr=e.stderr or error_msg,
                command=command_str,
                environment=exec_env,
                error=error_msg,
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with return code {e.returncode}")
            logger.error(f"STDERR: {e.stderr}" if e.stderr else "No error output")

            if check:
                raise

            return CommandResult(
                success=False,
                return_code=e.returncode,
                execution_time=time.time() - start_time,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                command=command_str,
                environment=exec_env,
                error=str(e),
            )

        except Exception as e:
            error_msg = f"Unexpected error executing command: {str(e)}"
            logger.exception(error_msg)

            if check:
                if isinstance(e, subprocess.SubprocessError):
                    raise
                raise subprocess.SubprocessError(error_msg) from e

            return CommandResult(
                success=False,
                return_code=-2,
                execution_time=time.time() - start_time,
                stdout="",
                stderr=error_msg,
                command=command_str,
                environment=exec_env,
                error=error_msg,
            )
