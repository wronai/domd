"""
Implementacja REST API dla aplikacji DoMD przy użyciu Flask.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from flask import Flask, Response, jsonify, request

from ...application.factory import ApplicationFactory
from ...core.domain.command import Command
from ...core.ports.command_executor import CommandExecutor
from ...core.ports.command_repository import CommandRepository
from ...core.services.command_service import CommandService
from ...core.services.report_service import ReportService

logger = logging.getLogger(__name__)


class DomdFlaskApi:
    """
    REST API dla aplikacji DoMD przy użyciu Flask.
    """

    def __init__(self, project_path: Union[str, Path] = None):
        """
        Inicjalizuje REST API dla aplikacji DoMD.

        Args:
            project_path: Ścieżka do katalogu projektu
        """
        self.app = Flask(__name__)
        self.project_path = Path(project_path) if project_path else Path.cwd()

        # Inicjalizacja komponentów aplikacji
        self.repository = ApplicationFactory.create_command_repository()
        self.executor = ApplicationFactory.create_command_executor()
        self.formatter = ApplicationFactory.create_report_formatter()

        # Załaduj wzorce ignorowania
        self.ignore_patterns = []
        ignore_file_path = self.project_path / ".domdignore"
        if ignore_file_path.exists():
            with open(ignore_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ignore_patterns.append(line)

        # Inicjalizacja usług
        self.command_service = ApplicationFactory.create_command_service(
            repository=self.repository,
            executor=self.executor,
            timeout=60,
            ignore_patterns=self.ignore_patterns,
        )

        self.report_service = ApplicationFactory.create_report_service(
            repository=self.repository,
            project_path=self.project_path,
            todo_file="TODO.md",
            done_file="DONE.md",
        )

        # Rejestracja endpointów
        self._register_routes()

    def _register_routes(self) -> None:
        """
        Rejestruje endpointy REST API.
        """
        # Endpoint zdrowia
        self.app.route("/health")(self.health)

        # Endpointy komend
        self.app.route("/api/commands", methods=["GET"])(self.get_commands)
        self.app.route("/api/commands/scan", methods=["POST"])(self.scan_commands)
        self.app.route("/api/commands/test", methods=["POST"])(self.test_commands)

        # Endpointy raportów
        self.app.route("/api/reports", methods=["GET"])(self.get_reports)
        self.app.route("/api/reports/generate", methods=["POST"])(self.generate_reports)

        # Endpointy statystyk
        self.app.route("/api/stats", methods=["GET"])(self.get_stats)

    def health(self) -> Response:
        """
        Endpoint zdrowia API.

        Returns:
            Odpowiedź HTTP
        """
        return jsonify(
            {"status": "ok", "version": "1.0.0", "project_path": str(self.project_path)}
        )

    def get_commands(self) -> Response:
        """
        Zwraca listę wszystkich komend.

        Returns:
            Odpowiedź HTTP
        """
        all_commands = self.repository.get_all_commands()
        successful_commands = self.repository.get_successful_commands()
        failed_commands = self.repository.get_failed_commands()
        ignored_commands = self.repository.get_ignored_commands()

        return jsonify(
            {
                "all_commands": [self._command_to_dict(cmd) for cmd in all_commands],
                "successful_commands": [
                    self._command_to_dict(cmd) for cmd in successful_commands
                ],
                "failed_commands": [
                    self._command_to_dict(cmd) for cmd in failed_commands
                ],
                "ignored_commands": [
                    self._command_to_dict(cmd) for cmd in ignored_commands
                ],
            }
        )

    def scan_commands(self) -> Response:
        """
        Skanuje projekt w poszukiwaniu komend.

        Returns:
            Odpowiedź HTTP
        """
        try:
            # Tymczasowo używamy starego kodu do skanowania projektu
            from ...core.detector import ProjectCommandDetector

            data = request.get_json() or {}
            project_path = Path(data.get("project_path", str(self.project_path)))
            exclude_patterns = data.get("exclude_patterns", [])
            include_patterns = data.get("include_patterns", [])

            detector = ProjectCommandDetector(
                project_path=project_path,
                exclude_patterns=exclude_patterns,
                include_patterns=include_patterns,
            )

            # Skanuj projekt
            commands_dict = detector.scan_project()

            # Konwertuj słowniki na obiekty Command i dodaj do repozytorium
            commands = []
            self.repository.clear()

            for cmd_dict in commands_dict:
                command = Command(
                    command=cmd_dict.get("command", ""),
                    type=cmd_dict.get("type", ""),
                    description=cmd_dict.get("description", ""),
                    source=cmd_dict.get("source", ""),
                    metadata=cmd_dict.get("metadata", {}),
                )
                commands.append(command)
                self.repository.add_command(command)

            # Sprawdź, które komendy powinny być ignorowane
            for command in commands:
                if self.command_service.should_ignore_command(command):
                    self.repository.mark_as_ignored(command)

            return jsonify(
                {
                    "status": "success",
                    "message": f"Znaleziono {len(commands)} komend",
                    "commands": [self._command_to_dict(cmd) for cmd in commands],
                }
            )

        except Exception as e:
            logger.error(f"Error scanning commands: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Błąd podczas skanowania komend: {str(e)}",
                    }
                ),
                500,
            )

    def test_commands(self) -> Response:
        """
        Testuje komendy.

        Returns:
            Odpowiedź HTTP
        """
        try:
            data = request.get_json() or {}
            command_ids = data.get("command_ids", [])
            timeout = data.get("timeout", 60)

            # Pobierz komendy do testowania
            all_commands = self.repository.get_all_commands()

            # Filtruj komendy według ID, jeśli podano
            if command_ids:
                commands_to_test = [
                    cmd for cmd in all_commands if cmd.command in command_ids
                ]
            else:
                commands_to_test = all_commands

            # Testuj komendy
            self.command_service.test_commands(commands_to_test, timeout=timeout)

            return jsonify(
                {
                    "status": "success",
                    "message": f"Przetestowano {len(commands_to_test)} komend",
                    "successful": len(self.repository.get_successful_commands()),
                    "failed": len(self.repository.get_failed_commands()),
                    "ignored": len(self.repository.get_ignored_commands()),
                }
            )

        except Exception as e:
            logger.error(f"Error testing commands: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Błąd podczas testowania komend: {str(e)}",
                    }
                ),
                500,
            )

    def get_reports(self) -> Response:
        """
        Zwraca informacje o raportach.

        Returns:
            Odpowiedź HTTP
        """
        todo_path = self.project_path / "TODO.md"
        done_path = self.project_path / "DONE.md"

        return jsonify(
            {
                "todo_report": {
                    "path": str(todo_path),
                    "exists": todo_path.exists(),
                    "size": todo_path.stat().st_size if todo_path.exists() else 0,
                    "modified": todo_path.stat().st_mtime if todo_path.exists() else 0,
                },
                "done_report": {
                    "path": str(done_path),
                    "exists": done_path.exists(),
                    "size": done_path.stat().st_size if done_path.exists() else 0,
                    "modified": done_path.stat().st_mtime if done_path.exists() else 0,
                },
            }
        )

    def generate_reports(self) -> Response:
        """
        Generuje raporty.

        Returns:
            Odpowiedź HTTP
        """
        try:
            data = request.get_json() or {}
            todo_file = data.get("todo_file", "TODO.md")
            done_file = data.get("done_file", "DONE.md")

            # Aktualizuj usługę raportów
            self.report_service = ApplicationFactory.create_report_service(
                repository=self.repository,
                project_path=self.project_path,
                todo_file=todo_file,
                done_file=done_file,
            )

            # Generuj raporty
            todo_path, done_path = self.report_service.generate_reports(self.formatter)

            return jsonify(
                {
                    "status": "success",
                    "message": "Wygenerowano raporty",
                    "todo_report": str(todo_path),
                    "done_report": str(done_path),
                }
            )

        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Błąd podczas generowania raportów: {str(e)}",
                    }
                ),
                500,
            )

    def get_stats(self) -> Response:
        """
        Zwraca statystyki.

        Returns:
            Odpowiedź HTTP
        """
        all_commands = self.repository.get_all_commands()
        successful_commands = self.repository.get_successful_commands()
        failed_commands = self.repository.get_failed_commands()
        ignored_commands = self.repository.get_ignored_commands()

        return jsonify(
            {
                "total_commands": len(all_commands),
                "successful_commands": len(successful_commands),
                "failed_commands": len(failed_commands),
                "ignored_commands": len(ignored_commands),
                "success_rate": len(successful_commands) / len(all_commands)
                if all_commands
                else 0,
            }
        )

    def _command_to_dict(self, command: Command) -> Dict[str, Any]:
        """
        Konwertuje obiekt Command na słownik.

        Args:
            command: Obiekt Command do konwersji

        Returns:
            Słownik reprezentujący komendę
        """
        result = command.to_dict()

        # Dodaj informacje o wyniku wykonania, jeśli dostępne
        if command.result:
            result["result"] = {
                "success": command.result.success,
                "return_code": command.result.return_code,
                "execution_time": command.result.execution_time,
                "error": command.result.error,
            }

        return result

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        """
        Uruchamia serwer REST API.

        Args:
            host: Host, na którym ma być uruchomiony serwer
            port: Port, na którym ma być uruchomiony serwer
            debug: Czy uruchomić serwer w trybie debug
        """
        self.app.run(host=host, port=port, debug=debug)
