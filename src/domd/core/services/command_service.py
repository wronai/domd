"""
Usługi biznesowe do zarządzania komendami w aplikacji DoMD.
"""

import logging
import subprocess
from typing import List, Optional

from ..command_execution.command_recorder import CommandRecorder
from ..domain.command import Command, CommandResult
from ..ports.command_executor import CommandExecutor
from ..ports.command_repository import CommandRepository

logger = logging.getLogger(__name__)


class CommandService:
    """
    Usługa biznesowa do zarządzania komendami.

    Usługa ta jest odpowiedzialna za wykonywanie komend, zarządzanie
    ich statusem i aktualizację repozytorium komend.
    """

    def __init__(
        self,
        repository: CommandRepository,
        executor: CommandExecutor,
        timeout: int = 60,
        ignore_patterns: Optional[List[str]] = None,
        dodocker_path: str = ".dodocker",
    ):
        """
        Inicjalizuje usługę CommandService.

        Args:
            repository: Repozytorium komend
            executor: Wykonawca komend
            timeout: Domyślny limit czasu wykonania w sekundach
            ignore_patterns: Lista wzorców komend do ignorowania
            dodocker_path: Ścieżka do pliku .dodocker
        """
        self.repository = repository
        self.executor = executor
        self.timeout = timeout
        self.ignore_patterns = ignore_patterns or []
        self.command_recorder = CommandRecorder(config_path=dodocker_path)

    def execute_command(self, command: Command) -> CommandResult:
        """
        Wykonuje komendę i aktualizuje jej status.

        Args:
            command: Komenda do wykonania

        Returns:
            Wynik wykonania komendy
        """
        try:
            logger.info(f"Executing command: {command.command}")
            result = self.executor.execute(command, timeout=self.timeout)
            command.result = result

            if result.success:
                self.repository.mark_as_successful(command)
            else:
                self.repository.mark_as_failed(command)
                logger.error(
                    f"Error executing command '{command.command}': {result.error}"
                )

            return result
        except Exception as e:
            logger.error(
                f"Exception executing command '{command.command}': {str(e)}",
                exc_info=True,
            )
            result = CommandResult(success=False, return_code=-1, error=str(e))
            command.result = result
            self.repository.mark_as_failed(command)
            return result

    def should_ignore_command(self, command: Command) -> bool:
        """
        Sprawdza, czy komenda powinna być ignorowana.

        Args:
            command: Komenda do sprawdzenia

        Returns:
            True, jeśli komenda powinna być ignorowana
        """
        import fnmatch

        logger.debug(f"Checking if command should be ignored: {command.command}")
        logger.debug(f"Ignore patterns: {self.ignore_patterns}")

        # Check if any ignore pattern matches the command or its components
        for pattern in self.ignore_patterns:
            logger.debug(f"  Checking pattern: {pattern}")

            # Check if pattern matches the full command string
            if fnmatch.fnmatch(command.command, pattern):
                logger.debug(f"    Pattern '{pattern}' matches full command")
                return True

            # Check if pattern matches just the script part (after 'npm run ')
            if command.command.startswith("npm run "):
                script_part = command.command[8:]
                if fnmatch.fnmatch(script_part, pattern):
                    logger.debug(
                        f"    Pattern '{pattern}' matches script part: {script_part}"
                    )
                    return True

            # Check if pattern matches the command type
            if hasattr(command, "type") and command.type:
                if fnmatch.fnmatch(command.type, pattern):
                    logger.debug(
                        f"    Pattern '{pattern}' matches type: {command.type}"
                    )
                    return True

            # Check if pattern matches the command description
            if hasattr(command, "description") and command.description:
                if fnmatch.fnmatch(command.description, pattern):
                    logger.debug(
                        f"    Pattern '{pattern}' matches description: {command.description}"
                    )
                    return True

            # Check if pattern matches the source file
            if hasattr(command, "source") and command.source:
                source_str = str(command.source)
                if fnmatch.fnmatch(source_str, pattern):
                    logger.debug(
                        f"    Pattern '{pattern}' matches source: {source_str}"
                    )
                    return True

            # Check if pattern matches any metadata values
            if hasattr(command, "metadata") and command.metadata:
                for key, value in command.metadata.items():
                    if isinstance(value, str) and fnmatch.fnmatch(value, pattern):
                        logger.debug(
                            f"    Pattern '{pattern}' matches metadata {key}: {value}"
                        )
                        return True

        logger.debug("  No patterns matched, command will not be ignored")
        return False

    def test_commands(self, commands: List[Command]) -> None:
        """
        Testuje listę komend i aktualizuje repozytorium.
        Automatycznie dodaje komendy przekraczające limit czasu do pliku .dodocker.

        Args:
            commands: Lista komend do przetestowania
        """
        # Wyczyść repozytorium przed rozpoczęciem testowania
        self.repository.clear()

        for command in commands:
            try:
                # Sprawdź, czy komenda powinna być ignorowana
                if self.should_ignore_command(command):
                    logger.info(f"Ignoring command: {command.command}")
                    self.repository.mark_as_ignored(command)
                    continue

                # Wykonaj komendę
                self.execute_command(command)

            except subprocess.TimeoutExpired:
                # Handle command timeout
                error_msg = f"Command timed out after {self.timeout} seconds"
                logger.warning(f"{error_msg}: {command.command}")

                # Record the command to .dodocker for future Docker execution
                self.command_recorder.record_command(
                    command=command.command,
                    reason=f"Command timed out after {self.timeout} seconds",
                    timeout=self.timeout,
                    metadata={
                        "source": command.source,
                        "description": command.description,
                        "type": command.type,
                    },
                )

                # Update command result
                result = CommandResult(
                    success=False,
                    return_code=-1,
                    error=error_msg,
                    execution_time=self.timeout,
                )
                command.result = result
                self.repository.mark_as_failed(command)

            except Exception as e:
                # Handle other exceptions
                error_msg = str(e)
                logger.error(
                    f"Error testing command '{command.command}': {error_msg}",
                    exc_info=True,
                )
                result = CommandResult(success=False, return_code=-1, error=error_msg)
                command.result = result
                self.repository.mark_as_failed(command)
