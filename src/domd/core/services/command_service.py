"""
Usługi biznesowe do zarządzania komendami w aplikacji DoMD.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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
    ):
        """
        Inicjalizuje usługę CommandService.

        Args:
            repository: Repozytorium komend
            executor: Wykonawca komend
            timeout: Domyślny limit czasu wykonania w sekundach
            ignore_patterns: Lista wzorców komend do ignorowania
        """
        self.repository = repository
        self.executor = executor
        self.timeout = timeout
        self.ignore_patterns = ignore_patterns or []

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

        # Check if any ignore pattern matches the command or its components
        for pattern in self.ignore_patterns:
            # Check if pattern matches the full command string
            if fnmatch.fnmatch(command.command, pattern):
                return True

            # Check if pattern matches just the script part (after 'npm run ')
            if command.command.startswith("npm run ") and fnmatch.fnmatch(
                command.command[8:], pattern
            ):
                return True

            # Check if pattern matches the command type or description
            if (
                hasattr(command, "type")
                and command.type
                and fnmatch.fnmatch(command.type, pattern)
            ):
                return True

            if (
                hasattr(command, "description")
                and command.description
                and fnmatch.fnmatch(command.description, pattern)
            ):
                return True

            # Check if pattern matches the source file
            if (
                hasattr(command, "source")
                and command.source
                and fnmatch.fnmatch(str(command.source), pattern)
            ):
                return True

            # Check if pattern matches any metadata values
            if hasattr(command, "metadata") and command.metadata:
                for value in command.metadata.values():
                    if isinstance(value, str) and fnmatch.fnmatch(value, pattern):
                        return True

        return False

    def test_commands(self, commands: List[Command]) -> None:
        """
        Testuje listę komend i aktualizuje repozytorium.

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
            except Exception as e:
                logger.error(f"Error testing command: {e}", exc_info=True)
                result = CommandResult(success=False, return_code=-1, error=str(e))
                command.result = result
                self.repository.mark_as_failed(command)
