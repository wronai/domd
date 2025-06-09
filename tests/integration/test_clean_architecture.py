"""
Test integracyjny dla nowej architektury czystej.

Ten test sprawdza, czy cały przepływ pracy z aplikacją działa poprawnie,
od skanowania projektu, przez wykonanie komend, po generowanie raportów.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from domd.application.factory import ApplicationFactory
from domd.core.domain.command import Command, CommandResult
from domd.core.ports.command_executor import CommandExecutor
from domd.core.ports.command_repository import CommandRepository
from domd.core.services.command_service import CommandService
from domd.core.services.report_service import ReportService


class MockCommandExecutor(CommandExecutor):
    """
    Mock wykonawcy komend do testów.
    """

    def __init__(self, success_commands=None, fail_commands=None):
        """
        Inicjalizuje mock wykonawcy komend.

        Args:
            success_commands: Lista komend, które powinny zakończyć się sukcesem
            fail_commands: Lista komend, które powinny zakończyć się niepowodzeniem
        """
        self.success_commands = success_commands or []
        self.fail_commands = fail_commands or []
        self.executed_commands = []

    def execute(self, command: Command, timeout=None) -> CommandResult:
        """
        Symuluje wykonanie komendy.

        Args:
            command: Komenda do wykonania
            timeout: Limit czasu wykonania

        Returns:
            Wynik wykonania komendy
        """
        self.executed_commands.append(command)

        if command.command in self.success_commands:
            return CommandResult(
                success=True,
                return_code=0,
                execution_time=0.1,
                stdout="Success output",
                stderr="",
            )
        elif command.command in self.fail_commands:
            return CommandResult(
                success=False,
                return_code=1,
                execution_time=0.1,
                stdout="",
                stderr="Error output",
            )
        else:
            # Domyślnie zwróć sukces
            return CommandResult(
                success=True,
                return_code=0,
                execution_time=0.1,
                stdout="Default success output",
                stderr="",
            )

    def execute_in_directory(
        self, command, directory, timeout=None, env=None
    ) -> CommandResult:
        """
        Symuluje wykonanie komendy w określonym katalogu.

        Args:
            command: Komenda do wykonania
            directory: Katalog, w którym ma być wykonana komenda
            timeout: Limit czasu wykonania
            env: Dodatkowe zmienne środowiskowe

        Returns:
            Wynik wykonania komendy
        """
        return self.execute(command, timeout)


class CleanArchitectureIntegrationTest(unittest.TestCase):
    """
    Test integracyjny dla nowej architektury czystej.
    """

    def setUp(self):
        """
        Przygotowuje środowisko testowe.
        """
        # Utwórz tymczasowy katalog projektu
        self.test_dir = tempfile.mkdtemp()
        self.project_path = Path(self.test_dir)

        # Utwórz przykładowe pliki projektu
        self.create_test_project_files()

        # Utwórz plik .doignore
        self.create_domdignore_file()

        # Inicjalizuj komponenty
        self.repository = ApplicationFactory.create_command_repository()

        # Utwórz mock wykonawcy komend
        self.executor = MockCommandExecutor(
            success_commands=["npm run build", "npm run test"],
            fail_commands=["npm run broken"],
        )

        # Inicjalizuj usługi
        self.command_service = CommandService(
            repository=self.repository,
            executor=self.executor,
            timeout=10,
            ignore_patterns=["*ignore*"],
        )

        self.report_service = ReportService(
            repository=self.repository,
            project_path=self.project_path,
            todo_file="TODO.md",
            done_file="DONE.md",
        )

    def tearDown(self):
        """
        Czyści środowisko testowe.
        """
        # Usuń tymczasowy katalog projektu
        shutil.rmtree(self.test_dir)

    def create_test_project_files(self):
        """
        Tworzy przykładowe pliki projektu do testów.
        """
        # Utwórz package.json
        package_json = self.project_path / "package.json"
        with open(package_json, "w") as f:
            f.write(
                """
            {
                "name": "test-project",
                "version": "1.0.0",
                "scripts": {
                    "start": "node index.js",
                    "build": "webpack",
                    "test": "jest",
                    "broken": "invalid-command",
                    "ignore-me": "should-be-ignored"
                }
            }
            """
            )

        # Utwórz README.md
        readme = self.project_path / "README.md"
        with open(readme, "w") as f:
            f.write(
                """
            # Test Project

            Run the following commands:

            ```bash
            npm run build
            npm run test
            npm run broken
            ```
            """
            )

    def create_domdignore_file(self):
        """
        Tworzy plik .doignore do testów.
        """
        domdignore = self.project_path / ".doignore"
        with open(domdignore, "w") as f:
            f.write(
                """
            # Ignore patterns
            *ignore*
            """
            )

    def test_full_workflow(self):
        """
        Testuje pełny przepływ pracy z aplikacją.
        """
        # 1. Przygotuj komendy testowe
        commands = [
            Command(
                command="npm run build",
                type="npm",
                description="Build the project",
                source="package.json",
                metadata={"file": "package.json"},
            ),
            Command(
                command="npm run test",
                type="npm",
                description="Run tests",
                source="package.json",
                metadata={"file": "package.json"},
            ),
            Command(
                command="npm run broken",
                type="npm",
                description="Run broken command",
                source="package.json",
                metadata={"file": "package.json"},
            ),
            Command(
                command="npm run ignore-me",
                type="npm",
                description="Should be ignored",
                source="package.json",
                metadata={"file": "package.json"},
            ),
        ]

        # 2. Dodaj komendy do repozytorium
        for cmd in commands:
            self.repository.add_command(cmd)

        # 3. Testuj komendy
        self.command_service.test_commands(commands)

        # 4. Sprawdź, czy komendy zostały poprawnie przetestowane
        successful_commands = self.repository.get_successful_commands()
        failed_commands = self.repository.get_failed_commands()
        ignored_commands = self.repository.get_ignored_commands()

        # Powinny być 2 udane komendy
        self.assertEqual(len(successful_commands), 2)
        self.assertEqual(successful_commands[0].command, "npm run build")
        self.assertEqual(successful_commands[1].command, "npm run test")

        # Powinna być 1 nieudana komenda
        self.assertEqual(len(failed_commands), 1)
        self.assertEqual(failed_commands[0].command, "npm run broken")

        # Powinna być 1 zignorowana komenda
        self.assertEqual(len(ignored_commands), 1)
        self.assertEqual(ignored_commands[0].command, "npm run ignore-me")

        # 5. Generuj raporty
        formatter = ApplicationFactory.create_report_formatter()
        todo_path, done_path = self.report_service.generate_reports(formatter)

        # 6. Sprawdź, czy raporty zostały wygenerowane
        self.assertTrue(todo_path.exists())
        self.assertTrue(done_path.exists())

        # 7. Sprawdź zawartość raportów
        with open(todo_path, "r") as f:
            todo_content = f.read()
            self.assertIn("npm run broken", todo_content)
            self.assertIn("Failed", todo_content)

        with open(done_path, "r") as f:
            done_content = f.read()
            self.assertIn("npm run build", done_content)
            self.assertIn("npm run test", done_content)
            self.assertIn("Success", done_content)


if __name__ == "__main__":
    unittest.main()
