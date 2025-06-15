"""
Interfejsy dla wykonawców komend w aplikacji DoMD.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..domain.command import CommandResult


class CommandExecutor(ABC):
    """
    Interfejs dla wykonawcy komend.

    Wykonawca komend jest odpowiedzialny za wykonywanie komend
    i zwracanie wyników ich wykonania.
    """

    @abstractmethod
    def execute(self, command: Command, timeout: Optional[int] = None) -> CommandResult:
        """
        Wykonuje komendę i zwraca wynik jej wykonania.

        Args:
            command: Komenda do wykonania
            timeout: Limit czasu wykonania w sekundach

        Returns:
            Wynik wykonania komendy
        """
        pass

    @abstractmethod
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
        pass
