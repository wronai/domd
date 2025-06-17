"""
REST API implementation for DoMD application using Flask.
"""

import logging
import os
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Tuple, Union

from flask import Flask, Response, abort, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from ...application.factory import ApplicationFactory
from ...core.domain.command import Command
from ...core.parsing.pattern_matcher import PatternMatcher
from .command_testing import register_command_testing_routes

# Configure logging
logger = logging.getLogger(__name__)

# Enable CORS for all routes
cors = CORS()

# Simple in-memory token storage (replace with database in production)
api_tokens = {}
users = {
    "admin": {
        "username": "admin",
        "password_hash": generate_password_hash("admin"),  # Change in production!
        "roles": ["admin"],
    }
}


class DomdFlaskApi:
    """
    REST API dla aplikacji DoMD przy użyciu Flask.
    """

    def __init__(self, project_path: Union[str, Path] = None, secret_key: str = None):
        """
        Initialize the DoMD REST API.

        Args:
            project_path: Path to the project directory
            secret_key: Secret key for session management (default: random hex)
        """
        self.app = Flask(__name__)
        self.app.secret_key = secret_key or secrets.token_hex(32)
        self.project_path = Path(project_path) if project_path else Path.cwd()

        # Initialize application services
        self.factory = ApplicationFactory(project_path)
        
        # Register all routes
        self._register_routes()
        
        # Register command testing routes
        try:
            from ...core.command_detection.handlers.command_handler import CommandHandler
            command_handler = CommandHandler(
                project_path=Path(project_path) if project_path else Path.cwd(),
                command_runner=self.factory.create_command_runner(),
                enable_docker_testing=True
            )
            register_command_testing_routes(self, command_handler)
        except Exception as e:
            logger.warning(f"Failed to register command testing routes: {e}")

        # Initialize application components
        self.repository = self.factory.create_command_repository()
        self.executor = self.factory.create_command_executor()
        self.formatter = self.factory.create_report_formatter()

        # Load ignore patterns
        self.ignore_patterns = []
        self._load_ignore_patterns()

        # Initialize services
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
            formatter=self.formatter,
        )

        # Register routes
        self._register_routes()

    def _load_ignore_patterns(self) -> None:
        """Load ignore patterns from .doignore file if it exists."""
        ignore_file_path = self.project_path / ".doignore"
        if ignore_file_path.exists():
            try:
                with open(ignore_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            self.ignore_patterns.append(line)
            except Exception as e:
                logger.warning(f"Failed to load .doignore: {e}")

    def _verify_token(self, token: str) -> Union[Dict[str, Any], None]:
        """Verify API token and return user data if valid."""
        if not token:
            return None

        # In a real app, validate against a database
        if token in api_tokens:
            return users.get(api_tokens[token])
        return None

    def require_auth(self, roles: list = None):
        """Decorator to require authentication for an endpoint."""

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    abort(401, "Missing or invalid authorization header")

                token = auth_header.split(" ")[1]
                user = self._verify_token(token)
                if not user:
                    abort(401, "Invalid or expired token")

                if roles and not any(role in user.get("roles", []) for role in roles):
                    abort(403, "Insufficient permissions")

                request.user = user
                return f(*args, **kwargs)

            return wrapper

        return decorator

    def _create_response(
        self, data: Any = None, message: str = None, status: int = 200, **kwargs
    ) -> Tuple[Dict[str, Any], int]:
        """Create a standardized API response."""
        response = {
            "status": "success" if 200 <= status < 400 else "error",
            "message": message,
            "data": data,
        }
        response.update(kwargs)
        return jsonify(response), status

    def _register_routes(self) -> None:
        """Register all API routes."""
        # Health check (public)
        self.app.route("/health", methods=["GET"])(self.health)
        self.app.route("/api/health", methods=["GET"])(
            self.health
        )  # Added for frontend compatibility

        # Authentication
        self.app.route("/api/auth/login", methods=["POST"])(self.login)
        self.app.route("/api/auth/refresh", methods=["POST"])(self.refresh_token)

        # Commands API (protected)
        self.app.route("/api/commands", methods=["GET"])(
            self.require_auth()(self.get_commands)
        )
        self.app.route("/api/commands/scan", methods=["POST"])(
            self.require_auth(["admin"])(self.scan_commands)
        )
        self.app.route("/api/commands/test", methods=["POST"])(
            self.require_auth(["admin"])(self.test_commands)
        )
        self.app.route("/api/commands/<string:command_id>", methods=["GET"])(
            self.require_auth()(self.get_command)
        )
        self.app.route("/api/commands/<string:command_id>/run", methods=["POST"])(
            self.require_auth(["admin"])(self.run_command)
        )

        # Reports API (protected)
        self.app.route("/api/reports", methods=["GET"])(
            self.require_auth()(self.get_reports)
        )
        self.app.route("/api/reports/generate", methods=["POST"])(
            self.require_auth(["admin"])(self.generate_reports)
        )

        # Stats API (protected)
        self.app.route("/api/stats", methods=["GET"])(
            self.require_auth()(self.get_stats)
        )

        # Project API (protected)
        self.app.route("/api/project", methods=["GET"])(
            self.require_auth()(self.get_project_info)
        )

        # Error handlers
        self.app.errorhandler(400)(self.bad_request)
        self.app.errorhandler(401)(self.unauthorized)
        self.app.errorhandler(403)(self.forbidden)
        self.app.errorhandler(404)(self.not_found)
        self.app.errorhandler(500)(self.server_error)

    # Authentication endpoints
    def login(self) -> Tuple[Dict[str, Any], int]:
        """Authenticate user and return a token."""
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return self._create_response(
                message="Username and password are required", status=400
            )

        user = users.get(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return self._create_response(
                message="Invalid username or password", status=401
            )

        # Generate token
        token = secrets.token_hex(32)
        api_tokens[token] = username

        return self._create_response(
            data={
                "token": token,
                "user": {"username": user["username"], "roles": user["roles"]},
            },
            message="Login successful",
        )

    def refresh_token(self) -> Tuple[Dict[str, Any], int]:
        """Refresh an authentication token."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._create_response(
                message="Missing or invalid authorization header", status=401
            )

        old_token = auth_header.split(" ")[1]
        username = api_tokens.pop(old_token, None)

        if not username or username not in users:
            return self._create_response(message="Invalid or expired token", status=401)

        # Generate new token
        new_token = secrets.token_hex(32)
        api_tokens[new_token] = username
        user = users[username]

        return self._create_response(
            data={
                "token": new_token,
                "user": {"username": user["username"], "roles": user["roles"]},
            },
            message="Token refreshed successfully",
        )

    # Health check endpoint
    def health(self) -> Tuple[Dict[str, Any], int]:
        """Health check endpoint."""
        return self._create_response(
            data={
                "version": "1.0.0",
                "project_path": str(self.project_path),
                "status": "operational",
            },
            message="Service is healthy",
        )

    # Command endpoints
    def get_commands(self) -> Tuple[Dict[str, Any], int]:
        """
        Get all commands with filtering and pagination.

        Query Parameters:
            status: Filter by status (success, failed, ignored, all)
            search: Search term in command or description
            page: Page number (default: 1)
            per_page: Items per page (default: 20, max: 100)
        """
        try:
            # Get query parameters
            status_filter = request.args.get("status", "all").lower()
            search_term = request.args.get("search", "").lower()
            page = max(1, int(request.args.get("page", 1)))
            per_page = min(100, max(1, int(request.args.get("per_page", 20))))

            # Get commands based on status filter
            if status_filter == "success":
                commands = self.repository.get_successful_commands()
            elif status_filter == "failed":
                commands = self.repository.get_failed_commands()
            elif status_filter == "ignored":
                commands = self.repository.get_ignored_commands()
            else:
                commands = self.repository.get_all_commands()

            # Apply search filter
            if search_term:
                commands = [
                    cmd
                    for cmd in commands
                    if (
                        search_term in cmd.command.lower()
                        or (cmd.description and search_term in cmd.description.lower())
                    )
                ]

            # Pagination
            total_commands = len(commands)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_commands = commands[start_idx:end_idx]

            return self._create_response(
                data={
                    "commands": [
                        self._command_to_dict(cmd) for cmd in paginated_commands
                    ],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_items": total_commands,
                        "total_pages": (total_commands + per_page - 1) // per_page,
                    },
                }
            )

        except Exception:  # noqa: F841
            logger.exception("Failed to get commands")
            return self._create_response(
                message="Failed to retrieve commands", status=500
            )

    def get_command(self, command_id: str) -> Tuple[Dict[str, Any], int]:
        """Get details of a specific command by ID."""
        try:
            command = self.repository.get_command_by_id(command_id)
            if not command:
                return self._create_response(
                    message=f"Command with ID {command_id} not found", status=404
                )

            return self._create_response(
                data={"command": self._command_to_dict(command)}
            )

        except Exception:  # noqa: F841
            logger.exception(f"Failed to get command {command_id}")
            return self._create_response(
                message="Failed to retrieve command", status=500
            )

    def run_command(self, command_id: str) -> Tuple[Dict[str, Any], int]:
        """Run a specific command by ID."""
        try:
            command = self.repository.get_command_by_id(command_id)
            if not command:
                return self._create_response(
                    message=f"Command with ID {command_id} not found", status=404
                )

            # Execute the command
            result = self.executor.execute(
                command=command.command,
                cwd=command.working_dir or str(self.project_path),
                env=command.environment or {},
            )

            # Update command status based on result
            command.success = result.returncode == 0
            command.last_run = datetime.utcnow()
            command.output = result.output
            command.error = result.error

            # Save the updated command
            self.repository.save_command(command)

            return self._create_response(
                data={
                    "command": self._command_to_dict(command),
                    "execution_result": {
                        "returncode": result.returncode,
                        "output": result.output,
                        "error": result.error,
                        "execution_time": result.execution_time,
                    },
                },
                message="Command executed successfully",
            )

        except Exception as e:
            logger.exception(f"Failed to execute command {command_id}")
            return self._create_response(
                message=f"Failed to execute command: {str(e)}", status=500
            )

    def scan_commands(self) -> Tuple[Dict[str, Any], int]:
        """
        Scan the project for commands.

        Request Body (JSON):
            project_path: Optional path to scan (default: current project)
            exclude_patterns: List of patterns to exclude
            include_patterns: List of patterns to include
            force_rescan: Whether to force rescan even if files haven't changed

        Returns:
            Tuple containing response data and status code
        """
        try:
            data = request.get_json() or {}
            project_path = Path(data.get("project_path", str(self.project_path)))
            exclude_patterns = data.get("exclude_patterns", [])
            include_patterns = data.get("include_patterns", [])
            _ = data.get("force_rescan", False)  # Unused variable

            # Validate project path
            if not project_path.exists() or not project_path.is_dir():
                return self._create_response(
                    message=f"Project path does not exist or is not a directory: {project_path}",
                    status=400,
                )

            # Use the command service to scan for commands
            try:
                from ...core.project_detection.detector import ProjectCommandDetector

                detector = ProjectCommandDetector(
                    project_path=project_path,
                    exclude_patterns=exclude_patterns,
                    include_patterns=include_patterns,
                )

                # Scan the project
                commands_dict = detector.scan_project()

                # Convert dictionaries to Command objects and add to repository
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

                # Check which commands should be ignored
                for command in commands:
                    if self.command_service.should_ignore_command(command):
                        self.repository.mark_as_ignored(command)

                return jsonify(
                    {
                        "status": "success",
                        "message": f"Successfully scanned {len(commands)} commands",
                        "data": {
                            "commands": [
                                self._command_to_dict(cmd) for cmd in commands
                            ],
                            "total_commands": len(commands),
                            "ignored_commands": sum(
                                1 for cmd in commands if cmd.ignored
                            ),
                        },
                    }
                )

            except Exception as e:
                logger.error(f"Error scanning project: {str(e)}", exc_info=True)
                return self._create_response(
                    message=f"Error scanning project: {str(e)}", status=500
                )
        except Exception as e:
            logger.error(f"Unexpected error in scan_commands: {str(e)}", exc_info=True)
            return self._create_response(
                message="An unexpected error occurred while processing the request",
                status=500,
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

            # Update report service with new file names
            self.report_service.todo_file = todo_file
            self.report_service.done_file = done_file

            # Generate reports
            todo_path, done_path = self.report_service.generate_reports()

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

    def get_project_info(self) -> Tuple[Dict[str, Any], int]:
        """Get information about the current project."""
        try:
            # Get project stats
            all_commands = self.repository.get_all_commands()
            successful_commands = self.repository.get_successful_commands()
            failed_commands = self.repository.get_failed_commands()
            ignored_commands = self.repository.get_ignored_commands()

            # Get disk usage
            total_size = 0
            file_count = 0
            for dirpath, _, filenames in os.walk(self.project_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                        file_count += 1
                    except (OSError, TypeError):
                        continue

            return self._create_response(
                data={
                    "project_path": str(self.project_path),
                    "stats": {
                        "total_commands": len(all_commands),
                        "successful_commands": len(successful_commands),
                        "failed_commands": len(failed_commands),
                        "ignored_commands": len(ignored_commands),
                        "success_rate": len(successful_commands) / len(all_commands)
                        if all_commands
                        else 0,
                    },
                    "disk_usage": {
                        "total_size": total_size,
                        "total_size_human": self._format_size(total_size),
                        "file_count": file_count,
                        "directory_count": sum(1 for _ in os.walk(self.project_path)),
                    },
                }
            )

        except Exception:  # noqa: F841
            logger.exception("Failed to get project info")
            return self._create_response(
                message="Failed to retrieve project information", status=500
            )

    def _format_date(self, date_obj):
        """Helper method to format date objects for JSON serialization."""
        return date_obj.isoformat() if date_obj else None

    def _command_to_dict(self, command: Command) -> Dict[str, Any]:
        """Convert a Command object to a dictionary for JSON serialization."""
        return {
            "id": str(command.id) if command.id else None,
            "name": command.name,
            "command": command.command,
            "description": command.description,
            "working_dir": str(command.working_dir) if command.working_dir else None,
            "environment": command.environment or {},
            "success": command.success,
            "output": command.output,
            "error": command.error,
            "execution_time": command.execution_time,
            # Format dates using the helper method
            "created_at": self._format_date(command.created_at),  # noqa: E231
            "updated_at": self._format_date(command.updated_at),  # noqa: E231
            "last_run": self._format_date(command.last_run),
            "tags": getattr(command, "tags", []),
            "metadata": getattr(command, "metadata", {}),
        }

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def bad_request(self, error) -> Tuple[Dict[str, Any], int]:
        return self._create_response(message=str(error) or "Bad request", status=400)

    def unauthorized(self, error) -> Tuple[Dict[str, Any], int]:
        return self._create_response(message=str(error) or "Unauthorized", status=401)

    def forbidden(self, error) -> Tuple[Dict[str, Any], int]:
        return self._create_response(message=str(error) or "Forbidden", status=403)

    def not_found(self, error) -> Tuple[Dict[str, Any], int]:
        return self._create_response(
            message=str(error) or "Resource not found", status=404
        )

    def server_error(self, error) -> Tuple[Dict[str, Any], int]:
        logger.exception("Internal server error")
        return self._create_response(
            message="An internal server error occurred", status=500
        )

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        """
        Uruchamia serwer REST API.

        Args:
            host: Host, na którym ma być uruchomiony serwer
            port: Port, na którym ma być uruchomiony serwer
            debug: Czy uruchomić serwer w trybie debug
        """
        self.app.run(host=host, port=port, debug=debug)
