"""Command runner with support for retries, chaining, and environment management."""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from .command_executor import CommandExecutor, CommandResult

logger = logging.getLogger(__name__)

# Type variable for command result handlers
T = TypeVar("T")


@dataclass
class CommandContext:
    """Context for command execution."""

    command: str
    cwd: Path
    env: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[CommandResult] = None

    def update_env(self, env: Dict[str, str]) -> None:
        """Update environment variables."""
        self.env.update(env)

    def update_metadata(self, data: Dict[str, Any]) -> None:
        """Update metadata."""
        self.metadata.update(data)


class CommandRunner(Generic[T]):
    """Manages execution of commands with retries, chaining, and result processing."""

    def __init__(
        self,
        executor: Optional[CommandExecutor] = None,
        max_retries: int = 0,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
    ):
        """Initialize the CommandRunner.

        Args:
            executor: CommandExecutor instance (creates default if None)
            max_retries: Maximum number of retry attempts for failed commands
            retry_delay: Initial delay between retries in seconds
            retry_backoff: Multiplier for delay between retries
        """
        self.executor = executor or CommandExecutor()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self._result_handlers: List[Callable[[CommandContext], T]] = []

    def add_result_handler(self, handler: Callable[[CommandContext], T]) -> None:
        """Add a result handler function.

        Args:
            handler: Function that processes command results
        """
        self._result_handlers.append(handler)

    def run(
        self,
        command: Union[str, List[str]],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        check: bool = False,
    ) -> T:
        """Run a command with retries and process the result.

        Args:
            command: Command to execute
            cwd: Working directory
            env: Additional environment variables
            timeout: Timeout in seconds
            check: If True, raises exception on non-zero exit code

        Returns:
            Result from the first handler that returns a non-None value

        Raises:
            subprocess.CalledProcessError: If check=True and command fails
            subprocess.TimeoutExpired: If command times out
            RuntimeError: If max retries exceeded
        """
        context = CommandContext(
            command=command if isinstance(command, str) else " ".join(command),
            cwd=Path(cwd).resolve() if cwd else Path.cwd(),
            env=env or {},
        )

        attempt = 0
        delay = self.retry_delay
        last_exception = None

        while attempt <= self.max_retries:
            try:
                if attempt > 0:
                    logger.debug("Retry attempt %d/%d", attempt, self.max_retries)
                    time.sleep(delay)
                    delay *= self.retry_backoff

                # Execute the command
                context.result = self.executor.execute(
                    command=command,
                    cwd=context.cwd,
                    env=context.env,
                    timeout=timeout,
                    check=check
                    and attempt == self.max_retries,  # Only check on final attempt
                )

                # Process result with handlers
                for handler in self._result_handlers:
                    try:
                        result = handler(context)
                        if result is not None:
                            return result
                    except Exception as e:
                        logger.warning("Result handler failed: %s", e, exc_info=True)

                # If no handler returned a result, return the command result
                if context.result is not None:
                    return context.result  # type: ignore

                return None  # type: ignore

            except Exception as e:
                last_exception = e
                attempt += 1
                if attempt > self.max_retries:
                    break

                logger.warning(
                    "Command failed (attempt %d/%d): %s",
                    attempt,
                    self.max_retries + 1,
                    e,
                )

        # If we get here, all retries failed
        if last_exception:
            if check:
                raise last_exception
            logger.error("Command failed after %d attempts", self.max_retries + 1)
            raise RuntimeError(
                f"Command failed after {self.max_retries + 1} attempts"
            ) from last_exception

        raise RuntimeError("Command execution failed with unknown error")

    def chain(
        self,
        commands: List[Union[str, List[str]]],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        stop_on_failure: bool = True,
    ) -> List[CommandResult]:
        """Run multiple commands in sequence.

        Args:
            commands: List of commands to execute
            cwd: Working directory
            env: Environment variables for all commands
            timeout: Timeout per command
            stop_on_failure: If True, stop on first failure

        Returns:
            List of CommandResult objects
        """
        results = []
        current_cwd = Path(cwd).resolve() if cwd else Path.cwd()

        for cmd in commands:
            try:
                result = self.run(
                    command=cmd,
                    cwd=current_cwd,
                    env=env,
                    timeout=timeout,
                    check=False,
                )
                results.append(result)
                if not result.success and stop_on_failure:
                    break
            except Exception as e:
                logger.error("Command chain failed: %s", e)
                if stop_on_failure:
                    raise

        return results
