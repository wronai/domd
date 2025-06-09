#!/usr/bin/env python3
"""
Enhanced CLI with clean architecture support
"""

import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import __version__
from .adapters.cli.command_presenter import CommandPresenter
from .application.factory import ApplicationFactory

# Tymczasowy import dla kompatybilności wstecznej
from .core.detector import ProjectCommandDetector
from .core.domain.command import Command
from .core.ports.command_executor import CommandExecutor
from .core.ports.command_repository import CommandRepository
from .core.ports.report_formatter import ReportFormatter
from .core.services.command_service import CommandService
from .core.services.report_service import ReportService

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create enhanced argument parser with .doignore support."""
    parser = argparse.ArgumentParser(
        prog="domd",
        description="Project Command Detector with .doignore support",
        epilog="""
Examples:
  domd                              # Scan, filter via .doignore, create files, test
  domd --init-only                  # Only create TODO.md, todo.sh, and .doignore template
  domd --generate-ignore            # Generate .doignore template file
  domd --ignore-file custom.ignore  # Use custom ignore file
  domd --show-ignored               # Show what commands would be ignored

.doignore Syntax:
  npm run dev                       # Exact command match
  *serve*                          # Pattern match (any command containing "serve")
  poetry run *                     # Pattern match (commands starting with "poetry run")
  # Comment line                   # Comments (ignored)

Workflow:
  1. domd --generate-ignore         # Create .doignore template
  2. Edit .doignore                 # Add your project-specific ignores
  3. domd --show-ignored           # Preview what will be ignored
  4. domd --init-only              # Create files without testing
  5. domd                          # Full run with filtering
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--path",
        "-p",
        default=".",
        help="Path to project directory (default: current directory)",
    )

    parser.add_argument(
        "--todo-file",
        default="TODO.md",
        help="Output file for failed commands (default: TODO.md)",
    )

    parser.add_argument(
        "--script-file",
        default="todo.sh",
        help="Output script file (default: todo.sh)",
    )

    parser.add_argument(
        "--ignore-file",
        default=".doignore",
        help="Ignore file (default: .doignore)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Command execution timeout in seconds (default: 60)",
    )

    parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        help="Exclude files/dirs (can be used multiple times)",
    )

    parser.add_argument(
        "--include-only",
        "-i",
        action="append",
        help="Include only specific files/dirs (can be used multiple times)",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show commands without executing them",
    )

    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only create TODO.md and todo.sh without testing commands",
    )

    parser.add_argument(
        "--generate-ignore",
        action="store_true",
        help="Generate .doignore template file",
    )

    parser.add_argument(
        "--show-ignored",
        action="store_true",
        help="Show what commands would be ignored via .doignore",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors"
    )

    return parser


def setup_signal_handlers(command_service: CommandService) -> None:
    """Setup signal handlers for graceful interruption."""

    def signal_handler(sig, frame):
        print("\n⚠️  Interrupted by user. Cleaning up...")
        # Tutaj można dodać kod do czyszczenia
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def validate_args(args: argparse.Namespace) -> Optional[str]:
    """Validate command line arguments."""
    if args.quiet and args.verbose:
        return "Cannot use --quiet and --verbose together"

    project_path = Path(args.path)
    if not project_path.exists():
        return f"Project path does not exist: {project_path}"

    if not project_path.is_dir():
        return f"Project path is not a directory: {project_path}"

    return None


def setup_logging(verbose: bool, quiet: bool) -> None:
    """
    Setup logging based on verbosity level.

    Args:
        verbose: Enable verbose logging (DEBUG level)
        quiet: Enable quiet mode (ERROR level only)
    """
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.ERROR

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def handle_generate_ignore(project_path: Path, ignore_file: str) -> int:
    """Handle --generate-ignore option."""
    try:
        # Tymczasowo używamy starego kodu
        detector = ProjectCommandDetector(
            project_path=project_path,
            ignore_file=ignore_file,
        )
        detector.generate_domdignore_template()
        print(f"✅ Generated {ignore_file} template file")
        print(f"💡 Edit {ignore_file} to customize ignored commands")
        return 0
    except Exception as e:
        print(f"❌ Error generating ignore file: {e}", file=sys.stderr)
        return 1


def handle_show_ignored(
    command_service: CommandService,
    repository: CommandRepository,
    presenter: CommandPresenter,
    project_path: Path,
    ignore_file: str,
) -> int:
    """Handle --show-ignored option."""
    try:
        # Tymczasowo używamy starego kodu
        detector = ProjectCommandDetector(
            project_path=project_path,
            ignore_file=ignore_file,
        )

        # Skanuj projekt i załaduj wzorce ignorowania
        commands = detector.scan_project()
        detector._load_ignore_patterns()

        # Testuj komendy (tylko sprawdzanie ignorowania)
        for cmd in commands:
            # Konwertuj słownik na obiekt Command
            command = Command(
                command=cmd.get("command", ""),
                type=cmd.get("type", ""),
                description=cmd.get("description", ""),
                source=cmd.get("source", ""),
                metadata=cmd.get("metadata", {}),
            )

            # Sprawdź, czy komenda powinna być ignorowana
            if command_service.should_ignore_command(command):
                repository.mark_as_ignored(command)
            else:
                repository.add_command(command)

        # Wyświetl ignorowane komendy
        presenter.print_dry_run(show_ignored=True)
        return 0
    except Exception as e:
        print(f"❌ Error showing ignored commands: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Enhanced main entry point with clean architecture support."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    error_msg = validate_args(args)
    if error_msg:
        print(f"❌ Error: {error_msg}", file=sys.stderr)
        return 1

    # Setup logging
    setup_logging(args.verbose, args.quiet)

    try:
        # Inicjalizacja ścieżek
        project_path = Path(args.path).resolve()

        # Inicjalizacja komponentów aplikacji
        repository = ApplicationFactory.create_command_repository()
        executor = ApplicationFactory.create_command_executor(max_retries=1)
        formatter = ApplicationFactory.create_report_formatter()

        # Załaduj wzorce ignorowania
        ignore_patterns = []
        ignore_file_path = project_path / args.ignore_file
        if ignore_file_path.exists():
            with open(ignore_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_patterns.append(line)

        # Inicjalizacja usług
        command_service = ApplicationFactory.create_command_service(
            repository=repository,
            executor=executor,
            timeout=args.timeout,
            ignore_patterns=ignore_patterns,
        )

        report_service = ApplicationFactory.create_report_service(
            repository=repository,
            project_path=project_path,
            todo_file=args.todo_file,
            done_file="DONE.md",
        )

        # Inicjalizacja prezentera
        presenter = ApplicationFactory.create_command_presenter(repository)

        if not args.quiet:
            print(f"TodoMD v{__version__} - Project Command Detector with .doignore")
            print(f"🔍 Project: {project_path}")
            print(f"📝 TODO file: {args.todo_file}")
            print(f"🔧 Script file: {args.script_file}")
            print(f"🚫 Ignore file: {args.ignore_file}")

        # Handle special modes
        if args.generate_ignore:
            return handle_generate_ignore(project_path, args.ignore_file)

        if args.show_ignored:
            return handle_show_ignored(
                command_service, repository, presenter, project_path, args.ignore_file
            )

        # Setup signal handlers
        setup_signal_handlers(command_service)

        # Tymczasowo używamy starego kodu do skanowania projektu
        detector = ProjectCommandDetector(
            project_path=project_path,
            timeout=args.timeout,
            exclude_patterns=args.exclude or [],
            include_patterns=args.include_only or [],
            todo_file=args.todo_file,
            script_file=args.script_file,
            ignore_file=args.ignore_file,
        )

        # Skanuj projekt
        commands = detector.scan_project()

        # Dodaj komendy do repozytorium
        for command in commands:
            repository.add_command(command)

        if not commands:
            return 0

        # Handle dry-run mode
        if args.dry_run:
            if not args.quiet:
                presenter.print_dry_run(show_ignored=False)
            return 0

        # Handle init-only mode
        if args.init_only:
            # Also generate .doignore template if it doesn't exist
            if not ignore_file_path.exists():
                detector.generate_domdignore_template()

            if not args.quiet:
                presenter.print_init_only(
                    todo_file=args.todo_file,
                    script_file=args.script_file,
                    ignore_file=args.ignore_file,
                )
            return 0

        # Test commands with real-time updates
        if not args.quiet:
            print(f"\n🧪 Testing {len(commands)} commands...")
            print(f"📊 Progress will be updated in {args.todo_file}")

        # Testuj komendy
        command_service.test_commands(commands)

        # Generuj raporty
        todo_path, done_path = report_service.generate_reports(formatter)

        # Print summary
        if not args.quiet:
            presenter.print_summary(
                todo_file=str(todo_path),
                done_file=str(done_path),
                script_file=args.script_file,
                ignore_file=args.ignore_file,
            )

        # Return exit code based on results
        return 1 if repository.get_failed_commands() else 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
