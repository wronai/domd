"""
Implementacja wykonawcy komend powłoki systemowej.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...core.domain.command import Command, CommandResult
from ...core.ports.command_executor import CommandExecutor

logger = logging.getLogger(__name__)


class ShellCommandExecutor(CommandExecutor):
    """
    Implementacja wykonawcy komend powłoki systemowej.
    """

    def __init__(self, max_retries: int = 1):
        """
        Inicjalizuje wykonawcę komend powłoki systemowej.

        Args:
            max_retries: Maksymalna liczba prób wykonania komendy
        """
        self.max_retries = max_retries

    def execute(self, command: Command, timeout: Optional[int] = None) -> CommandResult:
        """
        Wykonuje komendę i zwraca wynik jej wykonania.

        Args:
            command: Komenda do wykonania
            timeout: Limit czasu wykonania w sekundach

        Returns:
            Wynik wykonania komendy
        """
        # Domyślnie wykonaj komendę w bieżącym katalogu
        return self.execute_in_directory(command, Path.cwd(), timeout)

    def execute_in_directory(
        self,
        command: Command,
        directory: Path,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Wykonuje komendę w określonym katalogu i zwraca wynik jej wykonania.

        Args:
            command: Komenda do wykonania
            directory: Katalog, w którym ma być wykonana komenda
            timeout: Limit czasu wykonania w sekundach
            env: Dodatkowe zmienne środowiskowe

        Returns:
            Wynik wykonania komendy
        """
        cmd_str = command.command
        cmd_args = self._parse_command(cmd_str)

        # Przygotuj środowisko wykonania
        execution_env = None
        if env:
            execution_env = dict(os.environ)
            execution_env.update(env)

        # Wykonaj komendę z możliwością ponownych prób
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()

                # Wykonaj komendę
                process = subprocess.run(
                    cmd_args,
                    cwd=str(directory),
                    capture_output=True,
                    text=True,
                    env=execution_env,
                    timeout=timeout,
                )

                execution_time = time.time() - start_time

                # Przygotuj wynik
                result = CommandResult(
                    success=(process.returncode == 0),
                    return_code=process.returncode,
                    execution_time=execution_time,
                    stdout=process.stdout,
                    stderr=process.stderr,
                )

                if result.success:
                    return result

                # Jeśli nie udało się wykonać komendy, spróbuj ponownie
                if attempt < self.max_retries:
                    logger.warning(
                        f"Command failed (attempt {attempt}/{self.max_retries}): {cmd_str}"
                    )
                    continue

                # Jeśli wszystkie próby się nie powiodły, zwróć ostatni wynik
                logger.error(f"Command failed after {attempt} attempts")
                return result

            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out after {timeout} seconds: {cmd_str}")
                return CommandResult(
                    success=False,
                    return_code=-1,
                    execution_time=timeout or 0,
                    error=f"Command timed out after {timeout} seconds",
                )

            except Exception as e:
                logger.error(f"Error executing command: {str(e)}", exc_info=True)
                return CommandResult(success=False, return_code=-1, error=str(e))

        # Ten kod nie powinien być nigdy osiągnięty
        return CommandResult(
            success=False, return_code=-1, error="Unexpected error in command execution"
        )

    def _parse_command(self, command: str) -> List[str]:
        """
        Parsuje komendę do listy argumentów.

        Args:
            command: Komenda do sparsowania

        Returns:
            Lista argumentów komendy
        """
        import shlex

        return shlex.split(command)
