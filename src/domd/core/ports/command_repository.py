"""
Interfejsy dla repozytoriów komend w aplikacji DoMD.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..domain.command import Command


class CommandRepository(ABC):
    """
    Interfejs dla repozytorium komend.

    Repozytorium zarządza kolekcjami komend, w tym komendami udanymi,
    nieudanymi i ignorowanymi.
    """

    @abstractmethod
    def add_command(self, command: Command) -> None:
        """
        Dodaje komendę do repozytorium.

        Args:
            command: Komenda do dodania
        """
        pass

    @abstractmethod
    def get_all_commands(self) -> List[Command]:
        """
        Zwraca wszystkie komendy w repozytorium.

        Returns:
            Lista wszystkich komend
        """
        pass

    @abstractmethod
    def get_successful_commands(self) -> List[Command]:
        """
        Zwraca komendy, które zostały wykonane pomyślnie.

        Returns:
            Lista udanych komend
        """
        pass

    @abstractmethod
    def get_failed_commands(self) -> List[Command]:
        """
        Zwraca komendy, które nie zostały wykonane pomyślnie.

        Returns:
            Lista nieudanych komend
        """
        pass

    @abstractmethod
    def get_ignored_commands(self) -> List[Command]:
        """
        Zwraca komendy, które zostały zignorowane.

        Returns:
            Lista zignorowanych komend
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Czyści wszystkie kolekcje komend w repozytorium.
        """
        pass

    @abstractmethod
    def mark_as_successful(self, command: Command) -> None:
        """
        Oznacza komendę jako wykonaną pomyślnie.

        Args:
            command: Komenda do oznaczenia
        """
        pass

    @abstractmethod
    def mark_as_failed(self, command: Command) -> None:
        """
        Oznacza komendę jako nieudaną.

        Args:
            command: Komenda do oznaczenia
        """
        pass

    @abstractmethod
    def mark_as_ignored(self, command: Command) -> None:
        """
        Oznacza komendę jako zignorowaną.

        Args:
            command: Komenda do oznaczenia
        """
        pass
