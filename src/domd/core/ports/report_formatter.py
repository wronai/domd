"""
Interfejsy dla formaterów raportów w aplikacji DoMD.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from ..domain.command import Command


class ReportFormatter(ABC):
    """
    Interfejs dla formatera raportów.

    Formater raportów jest odpowiedzialny za formatowanie komend
    do określonego formatu wyjściowego (np. Markdown, JSON).
    """

    @abstractmethod
    def format_commands(self, commands: List[Command], title: str) -> str:
        """
        Formatuje listę komend do określonego formatu.

        Args:
            commands: Lista komend do sformatowania
            title: Tytuł raportu

        Returns:
            Sformatowany raport jako tekst
        """
        pass

    @abstractmethod
    def write_report(self, content: str, output_path: Path) -> Path:
        """
        Zapisuje raport do pliku.

        Args:
            content: Zawartość raportu
            output_path: Ścieżka do pliku wyjściowego

        Returns:
            Ścieżka do zapisanego pliku
        """
        pass
