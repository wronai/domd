"""
Fabryka aplikacji DoMD.
"""

from pathlib import Path
from typing import List, Optional

from ..adapters.cli.command_presenter import CommandPresenter
from ..adapters.formatters.markdown_formatter import MarkdownFormatter
from ..adapters.persistence.in_memory_command_repository import (
    InMemoryCommandRepository,
)
from ..adapters.persistence.shell_command_executor import ShellCommandExecutor
from ..core.ports.command_executor import CommandExecutor
from ..core.ports.command_repository import CommandRepository
from ..core.ports.report_formatter import ReportFormatter
from ..core.services.command_service import CommandService
from ..core.services.report_service import ReportService


class ApplicationFactory:
    """
    Fabryka komponentów aplikacji DoMD.

    Odpowiada za tworzenie i łączenie komponentów aplikacji.
    """

    @staticmethod
    def create_command_repository() -> CommandRepository:
        """
        Tworzy repozytorium komend.

        Returns:
            Repozytorium komend
        """
        return InMemoryCommandRepository()

    @staticmethod
    def create_command_executor(max_retries: int = 1) -> CommandExecutor:
        """
        Tworzy wykonawcę komend.

        Args:
            max_retries: Maksymalna liczba prób wykonania komendy

        Returns:
            Wykonawca komend
        """
        return ShellCommandExecutor(max_retries=max_retries)

    @staticmethod
    def create_report_formatter() -> ReportFormatter:
        """
        Tworzy formater raportów.

        Returns:
            Formater raportów
        """
        return MarkdownFormatter()

    @staticmethod
    def create_command_service(
        repository: CommandRepository,
        executor: CommandExecutor,
        timeout: int = 60,
        ignore_patterns: Optional[List[str]] = None,
    ) -> CommandService:
        """
        Tworzy usługę komend.

        Args:
            repository: Repozytorium komend
            executor: Wykonawca komend
            timeout: Limit czasu wykonania komendy
            ignore_patterns: Lista wzorców komend do ignorowania

        Returns:
            Usługa komend
        """
        return CommandService(
            repository=repository,
            executor=executor,
            timeout=timeout,
            ignore_patterns=ignore_patterns,
        )

    @staticmethod
    def create_report_service(
        repository: CommandRepository,
        project_path: Path,
        todo_file: str = "TODO.md",
        done_file: str = "DONE.md",
        formatter: Optional[ReportFormatter] = None,
    ) -> ReportService:
        """
        Tworzy usługę raportów.

        Args:
            repository: Repozytorium komend
            project_path: Ścieżka do katalogu projektu
            todo_file: Nazwa pliku z nieudanymi komendami
            done_file: Nazwa pliku z udanymi komendami
            formatter: Opcjonalny formater raportów

        Returns:
            Usługa raportów
        """
        return ReportService(
            repository=repository,
            project_path=project_path,
            todo_file=todo_file,
            done_file=done_file,
        )

    @staticmethod
    def create_command_presenter(repository: CommandRepository) -> CommandPresenter:
        """
        Tworzy prezenter komend.

        Args:
            repository: Repozytorium komend

        Returns:
            Prezenter komend
        """
        return CommandPresenter(repository=repository)

    @staticmethod
    def create_command_runner(max_retries: int = 3) -> "CommandRunner":
        """
        Tworzy CommandRunner do wykonywania komend.

        Args:
            max_retries: Maksymalna liczba prób wykonania komendy

        Returns:
            CommandRunner do wykonywania komend
        """
        from ..adapters.persistence.shell_command_executor import ShellCommandExecutor
        from ..core.command_execution.command_runner import CommandRunner

        executor = ShellCommandExecutor(
            max_retries=1
        )  # CommandRunner will handle retries
        return CommandRunner(executor=executor, max_retries=max_retries)
