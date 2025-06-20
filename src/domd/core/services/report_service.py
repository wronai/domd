"""
Usługi biznesowe do generowania raportów w aplikacji DoMD.
"""

import logging
from pathlib import Path
from typing import List, Tuple

from ..ports.command_repository import CommandRepository
from ..ports.report_formatter import ReportFormatter

logger = logging.getLogger(__name__)


class ReportService:
    """
    Usługa biznesowa do generowania raportów.

    Usługa ta jest odpowiedzialna za generowanie raportów
    na podstawie komend w repozytorium.
    """

    def __init__(
        self,
        repository: CommandRepository,
        project_path: Path,
        todo_file: str = "TODO.md",
        done_file: str = "DONE.md",
        formatter: ReportFormatter = None,
    ):
        """
        Inicjalizuje usługę ReportService.

        Args:
            repository: Repozytorium komend
            project_path: Ścieżka do katalogu projektu
            todo_file: Nazwa pliku z nieudanymi komendami
            done_file: Nazwa pliku z udanymi komendami
            formatter: Formater raportów
        """
        self.repository = repository
        self.project_path = project_path
        self.todo_file = todo_file
        self.done_file = done_file
        self.formatter = formatter

    def generate_reports(self, formatter: ReportFormatter = None) -> Tuple[Path, Path]:
        """
        Generuje raporty dla nieudanych i udanych komend.

        Args:
            formatter: Formater raportów (opcjonalny, jeśli podano w konstruktorze)

        Returns:
            Krotka (ścieżka_do_todo, ścieżka_do_done)
        """
        # Użyj formatera z argumentu lub z instancji
        formatter = formatter or self.formatter
        if formatter is None:
            raise ValueError(
                "No formatter provided. Either pass formatter to the constructor or to this method."
            )

        logger.info("Generating reports")

        # Pobierz komendy z repozytorium
        failed_commands = self.repository.get_failed_commands()
        successful_commands = self.repository.get_successful_commands()

        # Generuj raport dla nieudanych komend
        todo_content = formatter.format_commands(failed_commands, "Commands to Fix")
        todo_path = self.project_path / self.todo_file
        formatter.write_report(todo_content, todo_path)

        # Generuj raport dla udanych komend
        done_content = formatter.format_commands(
            successful_commands, "Successfully Executed Commands"
        )
        done_path = self.project_path / self.done_file
        formatter.write_report(done_content, done_path)

        logger.info(f"Reports generated: {todo_path}, {done_path}")
        return todo_path, done_path
