"""Command execution functionality for domd."""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    return_code: int
    execution_time: float
    output: str
    error: Optional[str] = None


class CommandExecutor:
    """Handles execution of shell commands with timeout and output capture."""

    def __init__(self, timeout: int = 60, cwd: Optional[Union[str, Path]] = None):
        """Initialize the command executor.

        Args:
            timeout: Default timeout in seconds for command execution
            cwd: Current working directory for commands
        """
        self.timeout = timeout
        self.cwd = Path(cwd).resolve() if cwd else Path.cwd()

    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        cwd: Optional[Union[str, Path]] = None,
    ) -> CommandResult:
        """Execute a shell command.

        Args:
            command: The command to execute
            timeout: Optional timeout in seconds (overrides default)
            cwd: Optional working directory (overrides default)

        Returns:
            CommandResult with execution details
        """
        timeout = timeout or self.timeout
        cwd = Path(cwd).resolve() if cwd else self.cwd

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                timeout=timeout,
                capture_output=True,
                text=True,
            )

            execution_time = time.time() - start_time

            return CommandResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr,
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                return_code=-1,
                execution_time=timeout,
                output="",
                error=f"Command timed out after {timeout} seconds",
            )

        except Exception as e:
            return CommandResult(
                success=False,
                return_code=-2,
                execution_time=time.time() - start_time,
                output="",
                error=str(e),
            )
