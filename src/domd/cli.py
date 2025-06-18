#!/usr/bin/env python3
"""
Enhanced CLI with clean architecture support
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

from . import __version__
from .adapters.cli.command_presenter import CommandPresenter
from .application.factory import ApplicationFactory
from .core.detector import ProjectCommandDetector  # For backward compatibility
from .core.domain.command import Command
from .core.ports.command_repository import CommandRepository
from .core.services.command_service import CommandService

logger = logging.getLogger(__name__)


def _check_node_installed() -> bool:
    """Check if Node.js and npm are installed.

    Returns:
        bool: True if both Node.js and npm are installed, False otherwise
    """
    try:
        # Check Node.js
        node_version = subprocess.check_output(
            ["node", "--version"], stderr=subprocess.PIPE, universal_newlines=True
        ).strip()

        # Check npm
        npm_version = subprocess.check_output(
            ["npm", "--version"], stderr=subprocess.PIPE, universal_newlines=True
        ).strip()

        print(f"✓ Found {node_version} and npm {npm_version}")
        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _install_dependencies(frontend_dir: Path) -> bool:
    """Install frontend dependencies using npm.

    Args:
        frontend_dir: Path to the frontend directory

    Returns:
        bool: True if installation was successful, False otherwise
    """
    print("Installing frontend dependencies...")
    try:
        subprocess.check_call(
            ["npm", "install"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def start_web_interface(args: argparse.Namespace) -> int:
    """Start the web interface.

    Args:
        args: Command line arguments

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    port = args.port
    open_browser = not args.no_browser

    # Check if Node.js and npm are installed
    print("🔍 Checking for Node.js and npm...")
    if not _check_node_installed():
        print(
            """
❌ Node.js and npm are required to run the web interface.
   Please install them from https://nodejs.org/ and try again.

   On Ubuntu/Debian: sudo apt-get install nodejs npm
   On macOS:          brew install node
   On Windows:        Download from https://nodejs.org/
        """
        )
        return 1

    # Get the directory of this file
    current_dir = Path(__file__).parent
    frontend_dir = current_dir.parent.parent / "frontend"

    if not frontend_dir.exists():
        print(f"❌ Error: Frontend directory not found at {frontend_dir}")
        return 1

    # Check if node_modules exists, if not, install dependencies
    if not (frontend_dir / "node_modules").exists():
        if not _install_dependencies(frontend_dir):
            return 1

    # Change to the frontend directory
    os.chdir(frontend_dir)

    # Set the port environment variable
    os.environ["PORT"] = str(port)

    print(f"🚀 Starting DoMD web interface on port {port}...")
    print("   Press Ctrl+C to stop the server")

    # Start the React development server
    try:
        cmd = ["npm", "start"]
        if sys.platform == "win32":
            cmd = ["npm.cmd", "start"]

        # Start the process
        process = subprocess.Popen(
            cmd,
            shell=sys.platform == "win32",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
        )

        # Open browser after a short delay
        if open_browser:
            time.sleep(2)  # Give the server a moment to start
            print(f"🌐 Opening browser to http://localhost:{port}...")
            webbrowser.open(f"http://localhost:{port}")

        # Stream the output
        for line in process.stdout:
            print(line, end="")

        # Wait for the process to complete
        process.wait()
        return process.returncode

    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
        return 0

    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        print("\n💡 Try these troubleshooting steps:")
        print("1. Make sure no other process is using the port")
        print("2. Try running 'npm install' in the frontend directory")
        print("3. Check the logs above for more details")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create enhanced argument parser with .doignore support and web interface."""
    # Create the main parser with add_help=False to handle help and version manually
    parser = argparse.ArgumentParser(
        prog="domd",
        description="Project Command Detector with .doignore support and web interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # We'll add help manually to control its position
    )

    # Add help and version arguments at the top level
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message and exit"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version information and exit"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Main command (default)
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan project for commands (default)",
        description="Scan project for commands and generate reports",
    )
    scan_parser.set_defaults(func=None)  # Will be handled in main()

    # Web interface command
    web_parser = subparsers.add_parser(
        "web",
        help="Start the web interface",
        description="Start the DoMD web interface",
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=3003,
        help="Port to run the web interface on (default: 3003)",
    )
    web_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the browser automatically",
    )
    web_parser.set_defaults(func=start_web_interface)

    # Test commands in Docker
    test_parser = subparsers.add_parser(
        "test-commands",
        help="Test commands in Docker containers",
        description="Test commands in Docker and update .doignore with failing commands",
    )
    test_parser.add_argument(
        "commands",
        nargs="*",
        help="Commands to test (or use --file to read from file)",
    )
    test_parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="File containing commands to test (one per line)",
    )
    test_parser.add_argument(
        "--update-doignore",
        action="store_true",
        help="Update .doignore with commands that fail in Docker",
    )
    test_parser.add_argument(
        "--dodocker",
        type=Path,
        default=".dodocker",
        help="Path to .dodocker configuration file (default: .dodocker)",
    )
    test_parser.add_argument(
        "--doignore",
        type=Path,
        default=".doignore",
        help="Path to .doignore file (default: .doignore)",
    )
    test_parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Skip Docker testing and only validate commands",
    )
    test_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    # This will be handled by the command service
    test_parser.set_defaults(func=lambda args: 0)  # Return success by default

    # Common arguments for scan command
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory)",
    )
    scan_parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help="Exclude files/directories matching pattern (can be used multiple times)",
    )
    scan_parser.add_argument(
        "--include-only",
        "-i",
        action="append",
        default=[],
        help="Only include files/directories matching pattern (can be used multiple times)",
    )
    scan_parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=30,
        help="Command execution timeout in seconds (default: 30)",
    )
    scan_parser.add_argument(
        "--todo-file",
        default="TODO.md",
        help="Name of the TODO file to create (default: TODO.md)",
    )
    scan_parser.add_argument(
        "--script-file",
        default="todo.sh",
        help="Name of the script file to create (default: todo.sh)",
    )
    scan_parser.add_argument(
        "--ignore-file",
        default=".doignore",
        help="Name of the ignore file to use (default: .doignore)",
    )
    scan_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    scan_parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only create TODO.md and todo.sh without testing commands",
    )
    scan_parser.add_argument(
        "--generate-ignore",
        action="store_true",
        help="Generate .doignore template file",
    )
    scan_parser.add_argument(
        "--show-ignored",
        action="store_true",
        help="Show what commands would be ignored via .doignore",
    )
    scan_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    scan_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors"
    )

    # Set default command to scan for backward compatibility
    parser.set_defaults(command="scan")

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
    # Skip validation for web command
    if hasattr(args, "command") and args.command == "web":
        return None

    # Only check these for non-web commands
    if (
        hasattr(args, "quiet")
        and hasattr(args, "verbose")
        and getattr(args, "quiet", False)
        and args.verbose
    ):
        return "Cannot use --quiet and --verbose together"

    # Only validate path if it exists in args (i.e., for scan command)
    if hasattr(args, "path"):
        project_path = Path(args.path)
        if not project_path.exists():
            return f"Project path does not exist: {project_path}"

        if not project_path.is_dir():
            return f"Project path is not a directory: {project_path}"

    return None


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Setup logging based on verbosity level.

    Args:
        verbose: Enable verbose logging (DEBUG level)
        quiet: Enable quiet mode (ERROR level only)
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
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
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Check if the command is a valid shell command
        if not hasattr(args, "command") or args.command is None:
            parser.print_help()
            print("\nPlease specify a command (scan or web).")
            return 1

        if args.command == "web":
            return start_web_interface(args)

        # If we get here, it's the scan command
        elif args.command == "scan":
            # For scan command, do validation and setup logging
            error_msg = validate_args(args)
            if error_msg:
                print(f"❌ Error: {error_msg}", file=sys.stderr)
                return 1

        # Setup logging with default values if not provided
        verbose = getattr(args, "verbose", False)
        quiet = getattr(args, "quiet", False)
        setup_logging(verbose=verbose, quiet=quiet)

        # Get the project path with a default of current directory if not provided
        project_path = Path(getattr(args, "path", ".")).resolve()

        # Initialize application components
        repository = ApplicationFactory.create_command_repository()
        executor = ApplicationFactory.create_command_executor(max_retries=1)

        # Load ignore patterns
        ignore_patterns = []
        ignore_file_path = project_path / getattr(args, "ignore_file", ".doignore")
        if ignore_file_path.exists():
            with open(ignore_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_patterns.append(line)

            # Initialize services with default values if not provided
            timeout = getattr(args, "timeout", 30)  # Default to 30 seconds
            _ = getattr(args, "todo_file", "TODO.md")  # Used in other parts
            _ = getattr(args, "script_file", "todo.sh")  # Used in other parts
            _ = getattr(args, "ignore_file", ".doignore")  # Used in other parts

            # Initialize command service
            command_service = ApplicationFactory.create_command_service(
                repository=repository,
                executor=executor,
                timeout=timeout,
                ignore_patterns=ignore_patterns,
            )

            # Initialize report service with the correct parameters
            report_service = ApplicationFactory.create_report_service(
                repository=repository,
                project_path=project_path,
                todo_file=getattr(args, "todo_file", "TODO.md"),
                done_file="DONE.md",  # Using default done file name
            )

        # Inicjalizacja prezentera
        presenter = ApplicationFactory.create_command_presenter(repository)

        # Get quiet attribute with default False if not present
        quiet = getattr(args, "quiet", False)

        if not quiet:
            print(f"TodoMD v{__version__} - Project Command Detector with .doignore")
            print(f"🔍 Project: {project_path}")
            print(f"📝 TODO file: {getattr(args, 'todo_file', 'TODO.md')}")
            print(f"🔧 Script file: {getattr(args, 'script_file', 'todo.sh')}")
            print(f"🚫 Ignore file: {getattr(args, 'ignore_file', '.doignore')}")

        # Handle special modes
        if getattr(args, "generate_ignore", False):
            return handle_generate_ignore(
                project_path, getattr(args, "ignore_file", ".doignore")
            )

        if getattr(args, "show_ignored", False):
            return handle_show_ignored(
                command_service,
                repository,
                presenter,
                project_path,
                getattr(args, "ignore_file", ".doignore"),
            )

        # Setup signal handlers
        setup_signal_handlers(command_service)

        # Tymczasowo używamy starego kodu do skanowania projektu
        detector = ProjectCommandDetector(
            project_path=project_path,
            timeout=getattr(
                args, "timeout", 30
            ),  # Default to 30 seconds if not specified
            exclude_patterns=getattr(args, "exclude", []) or [],
            include_patterns=getattr(args, "include_only", []) or [],
            todo_file=getattr(args, "todo_file", "TODO.md"),
            script_file=getattr(args, "script_file", "todo.sh"),
            ignore_file=getattr(args, "ignore_file", ".doignore"),
        )

        # Skanuj projekt
        commands = detector.scan_project()

        # Dodaj komendy do repozytorium
        for command in commands:
            repository.add_command(command)

        if not commands:
            return 0

        # Handle dry-run mode
        if hasattr(args, "dry_run") and args.dry_run:
            if not getattr(
                args, "quiet", False
            ):  # Default to False if quiet not in args
                presenter.print_dry_run(show_ignored=False)
            return 0

        # Handle init-only mode
        if hasattr(args, "init_only") and args.init_only:
            # Also generate .doignore template if it doesn't exist
            if not ignore_file_path.exists():
                detector.generate_domdignore_template()

            if not getattr(args, "quiet", False):
                presenter.print_init_only(
                    todo_file=args.todo_file,
                    script_file=args.script_file,
                    ignore_file=args.ignore_file,
                )
            return 0

        # Test commands with real-time updates
        if not getattr(args, "quiet", False):
            print(f"\n🧪 Testing {len(commands)} commands...")
            print(
                f"📊 Progress will be updated in {getattr(args, 'todo_file', 'TODO.md')}"
            )

        # Create formatter for reports
        formatter = ApplicationFactory.create_report_formatter()

        # Testuj komendy
        command_service.test_commands(commands)

        # Generuj raporty
        todo_path, done_path = report_service.generate_reports(formatter)

        # Print summary
        if not getattr(args, "quiet", False):
            presenter.print_summary(
                todo_file=str(todo_path),
                done_file=str(done_path),
                script_file=getattr(args, "script_file", "todo.sh"),
                ignore_file=getattr(args, "ignore_file", ".doignore"),
            )

        # Return exit code based on results
        return 1 if repository.get_failed_commands() else 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
