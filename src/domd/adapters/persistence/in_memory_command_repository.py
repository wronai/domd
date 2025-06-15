"""
Implementacja repozytorium komend w pamięci.
"""

from typing import List

from ...core.domain.command import Command
from ...core.ports.command_repository import CommandRepository


class InMemoryCommandRepository(CommandRepository):
    """
    Implementacja repozytorium komend przechowująca komendy w pamięci.
    """

    def __init__(self):
        """Inicjalizuje repozytorium komend w pamięci."""
        self._all_commands: List[Command] = []
        self._successful_commands: List[Command] = []
        self._failed_commands: List[Command] = []
        self._ignored_commands: List[Command] = []

    def add_command(self, command: Command) -> None:
        """
        Dodaje komendę do repozytorium.

        Args:
            command: Komenda do dodania
        """
        if command not in self._all_commands:
            self._all_commands.append(command)

    def get_all_commands(self) -> List[Command]:
        """
        Zwraca wszystkie komendy w repozytorium.

        Returns:
            Lista wszystkich komend
        """
        return self._all_commands.copy()

    def get_successful_commands(self) -> List[Command]:
        """
        Zwraca komendy, które zostały wykonane pomyślnie.

        Returns:
            Lista udanych komend
        """
        return self._successful_commands.copy()

    def get_failed_commands(self) -> List[Command]:
        """
        Zwraca komendy, które nie zostały wykonane pomyślnie.

        Returns:
            Lista nieudanych komend
        """
        return self._failed_commands.copy()

    def get_ignored_commands(self) -> List[Command]:
        """
        Zwraca komendy, które zostały zignorowane.

        Returns:
            Lista zignorowanych komend
        """
        return self._ignored_commands.copy()

    def clear(self) -> None:
        """
        Czyści wszystkie kolekcje komend w repozytorium.
        """
        self._successful_commands.clear()
        self._failed_commands.clear()
        self._ignored_commands.clear()

    def mark_as_successful(self, command: Command) -> None:
        """
        Oznacza komendę jako wykonaną pomyślnie.

        Args:
            command: Komenda do oznaczenia
        """
        if command in self._failed_commands:
            self._failed_commands.remove(command)
        if command in self._ignored_commands:
            self._ignored_commands.remove(command)
        if command not in self._successful_commands:
            self._successful_commands.append(command)
        if command not in self._all_commands:
            self._all_commands.append(command)

    def mark_as_failed(self, command: Command) -> None:
        """
        Oznacza komendę jako nieudaną.

        Args:
            command: Komenda do oznaczenia
        """
        if command in self._successful_commands:
            self._successful_commands.remove(command)
        if command in self._ignored_commands:
            self._ignored_commands.remove(command)
        if command not in self._failed_commands:
            self._failed_commands.append(command)
        if command not in self._all_commands:
            self._all_commands.append(command)

    def mark_as_ignored(self, command: Command) -> None:
        """
        Oznacza komendę jako zignorowaną.

        Args:
            command: Komenda do oznaczenia
        """
        if command in self._successful_commands:
            self._successful_commands.remove(command)
        if command in self._failed_commands:
            self._failed_commands.remove(command)
        if command not in self._ignored_commands:
            self._ignored_commands.append(command)
        if command not in self._all_commands:
            self._all_commands.append(command)
