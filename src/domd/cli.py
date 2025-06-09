#!/usr/bin/env python3
"""
Enhanced CLI with .doignore support
"""

import argparse
import signal
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .core.detector import ProjectCommandDetector


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
        type=str,
        default=".",
        help="Path to project directory (default: current directory)",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Only detect commands without creating files or executing",
    )

    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only create TODO.md, todo.sh, and .doignore template (no testing)",
    )

    parser.add_argument(
        "--generate-ignore",
        action="store_true",
        help="Generate .doignore template file and exit",
    )

    parser.add_argument(
        "--show-ignored",
        action="store_true",
        help="Show which commands would be ignored and exit",
    )

    parser.add_argument(
        "--ignore-file",
        type=str,
        default=".doignore",
        help="Custom ignore file path (default: .doignore)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed logging",
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors"
    )

    parser.add_argument(
        "--todo-file",
        type=str,
        default="TODO.md",
        help="TODO markdown file path (default: TODO.md)",
    )

    parser.add_argument(
        "--script-file",
        type=str,
        default="todo.sh",
        help="Executable script file path (default: todo.sh)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Command timeout in seconds (default: 60)",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude specific file patterns (can be used multiple times)",
    )

    parser.add_argument(
        "--include-only",
        action="append",
        help="Include only specific file patterns (can be used multiple times)",
    )

    return parser


def setup_signal_handlers(detector: ProjectCommandDetector):
    """Setup signal handlers for graceful interruption."""

    def signal_handler(signum, frame):
        """Handle interruption signals gracefully."""
        print("\n🛑 Execution interrupted by user")
        print("💾 Saving current progress...")

        if hasattr(detector, "failed_commands") and hasattr(
            detector, "successful_commands"
        ):
            all_commands = detector.failed_commands + detector.successful_commands
            if all_commands:
                detector._finalize_todo_md(all_commands)
                print(f"📝 Progress saved to {detector.todo_file}")

        sys.exit(130)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)


def validate_args(args: argparse.Namespace) -> Optional[str]:
    """Validate command line arguments."""
    project_path = Path(args.path)
    if not project_path.exists():
        return f"Project path does not exist: {project_path}"

    if not project_path.is_dir():
        return f"Project path is not a directory: {project_path}"

    if args.timeout <= 0:
        return "Timeout must be a positive integer"

    if args.verbose and args.quiet:
        return "Cannot specify both --verbose and --quiet"

    return None


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Setup logging based on verbosity level.

    Args:
        verbose: Enable verbose logging (DEBUG level)
        quiet: Enable quiet mode (ERROR level only)
    """
    import logging

    from domd.core.utils.logging_utils import setup_logging as setup_logging_util

    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Use the utility function from logging_utils
    setup_logging_util(level=level)


def handle_generate_ignore(detector: ProjectCommandDetector) -> int:
    """Handle --generate-ignore option."""
    print("📝 Generating .doignore template...")
    detector.generate_doignore_template()

    ignore_file_path = (
        detector.project_path / detector.ignore_parser.ignore_file_path.name
    )
    if ignore_file_path.exists():
        print(f"✅ Created .doignore template at {ignore_file_path}")
        print("💡 Edit this file to customize which commands to skip")
        print("📖 See examples and patterns in the template")
        return 0
    else:
        print("❌ Failed to create .doignore template")
        return 1


def handle_show_ignored(detector: ProjectCommandDetector) -> int:
    """Handle --show-ignored option."""
    print("🔍 Scanning commands and showing ignore status...")

    # Scan all commands
    all_commands = detector.scan_project()

    if not all_commands:
        print("❌ No commands found to analyze")
        return 0

    # Separate ignored and testable commands
    ignored_commands = []
    testable_commands = []

    for cmd in all_commands:
        if detector.ignore_parser.should_ignore_command(cmd["command"]):
            reason = detector.ignore_parser.get_ignore_reason(cmd["command"])
            cmd["ignore_reason"] = reason
            ignored_commands.append(cmd)
        else:
            testable_commands.append(cmd)

    # Report results
    total = len(all_commands)
    ignored_count = len(ignored_commands)
    testable_count = len(testable_commands)

    print("\n📊 Command Analysis Results:")
    print(f"   Total commands found: {total}")
    print(f"   🧪 Commands to test: {testable_count}")
    print(f"   🚫 Commands to ignore: {ignored_count}")

    if ignored_commands:
        print("\n🚫 Commands that will be IGNORED:")
        print("   (based on .domdignore rules)")
        print()

        # Group by ignore reason
        by_reason = {}
        for cmd in ignored_commands:
            reason = cmd.get("ignore_reason", "unknown")
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(cmd)

        for reason, commands in by_reason.items():
            print(f"   📋 {reason}:")  # noqa: E231
            for cmd in commands:
                print(f"      🚫 {cmd['command']} ({cmd['source']})")  # noqa: E231
            print()

    if testable_commands:
        print("🧪 Commands that will be TESTED:")
        print()
        for i, cmd in enumerate(testable_commands, 1):
            print(f"   {i:3d}. {cmd['command']}")
            print(f"        Source: {cmd['source']}")
            print(f"        Description: {cmd['description']}")
            print()

    if ignored_count > 0:
        print(
            f"💡 To modify ignore rules, edit: {detector.ignore_parser.ignore_file_path}"
        )

    return 0


def print_summary(detector: ProjectCommandDetector, total_commands: int) -> None:
    """Print execution summary with ignore statistics."""
    # Poprawne zliczanie komend niezależnie od ich typu (obiekt Command lub słownik)
    successful = len(detector.successful_commands)
    failed = len(detector.failed_commands)
    ignored = len(detector.ignored_commands)
    
    # Upewnij się, że statystyki są aktualne
    total_tested = successful + failed
    
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    print("📊 Results:")
    print(f"   Total commands found: {total_tested + ignored}")
    print(f"   Commands tested:  {total_tested}")
    print(f"   Commands ignored:  {ignored} (via .domdignore)")
    print(f"   ✅ Successful:  {successful}")
    print(f"   ❌ Failed:  {failed}")

    if total_commands > 0:
        success_rate = (successful / total_commands) * 100
        print(f"   📈 Success rate: {success_rate:.1f}%")

    print("📝 Files:")
    print(f"   📋 TODO file: {detector.todo_file}")
    print(f"   🔧 Script file: {detector.script_file}")
    print(f"   🚫 Ignore file: {detector.ignore_parser.ignore_file_path}")  # noqa: E231

    if failed > 0:
        print("\n🔧 Next steps:")
        print(f"   1. Review failed commands in {detector.todo_file}")
        print("   2. Add problematic commands to .doignore")
        print(f"   3. Edit {detector.script_file} if needed")
        print("   4. Re-run: domd")
    else:
        print("\n🎉 All testable commands executed successfully!")

    if ignored > 0:
        print("\n🚫 Ignored commands:")
        print(f"   {ignored} commands were skipped via .doignore")
        print("   Use --show-ignored to see which commands are ignored")


def main() -> int:
    """Enhanced main entry point with .doignore support."""
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
        # Initialize enhanced detector with ignore support
        detector = ProjectCommandDetector(
            project_path=args.path,
            timeout=args.timeout,
            exclude_patterns=args.exclude or [],
            include_patterns=args.include_only or [],
            todo_file=args.todo_file,
            script_file=args.script_file,
            ignore_file=args.ignore_file,
        )

        if not args.quiet:
            print(f"TodoMD v{__version__} - Project Command Detector with .domdignore")
            print(f"🔍 Project: {Path(args.path).resolve()}")
            print(f"📝 TODO file: {args.todo_file}")
            print(f"🔧 Script file: {args.script_file}")
            print(f"🚫 Ignore file: {args.ignore_file}")

        # Handle special modes
        if args.generate_ignore:
            return handle_generate_ignore(detector)

        if args.show_ignored:
            return handle_show_ignored(detector)

        # Setup signal handlers
        setup_signal_handlers(detector)

        # Scan and filter commands
        commands = detector.scan_and_initialize()
        if not commands:
            return 0

        # Handle dry-run mode
        if args.dry_run:
            if not args.quiet:
                print("\n🔍 DRY RUN MODE - Filtered commands:")
                for i, cmd in enumerate(commands, 1):
                    # Obsługa zarówno obiektów Command jak i słowników
                    if hasattr(cmd, 'description') and hasattr(cmd, 'command') and hasattr(cmd, 'source'):
                        # To jest obiekt Command
                        description = cmd.description
                        command = cmd.command
                        source = cmd.source
                    elif isinstance(cmd, dict):
                        # To jest słownik
                        description = cmd.get('description', 'No description')
                        command = cmd.get('command', 'No command')
                        source = cmd.get('source', 'Unknown source')
                    else:
                        # Nieznany typ, pokaż co mamy
                        description = str(cmd)
                        command = str(cmd)
                        source = type(cmd).__name__
                        
                    print(f"{i:3d}. {description}")
                    print(f"     Command:  {command}")
                    print(f"     Source:   {source}")
                    print()

                if detector.ignored_commands:
                    print(
                        f"🚫 Would ignore {len(detector.ignored_commands)} commands via .domdignore"
                    )
            return 0

        # Handle init-only mode
        if args.init_only:
            # Also generate .domdignore template if it doesn't exist
            if not (detector.project_path / args.ignore_file).exists():
                detector.generate_domdignore_template()

            if not args.quiet:
                print("\n✅ Initialization complete!")
                print(
                    f"📋 Created {args.todo_file} with {len(commands)} testable commands"
                )
                print(f"🔧 Created executable {args.script_file}")
                if detector.ignored_commands:
                    print(
                        f"🚫 Ignored {len(detector.ignored_commands)} commands via .domdignore"
                    )
                print("\n💡 Next steps:")
                print(
                    f"   • Review and edit {args.ignore_file} to adjust ignored commands"
                )
                print(f"   • Run: ./{args.script_file} to execute commands manually")
                print("   • Or run: domd to test with TodoMD")
                print("   • Use: domd --show-ignored to see ignored commands")
            return 0

        # Test commands with real-time updates
        if not args.quiet:
            print(f"\n🧪 Testing {len(commands)} commands...")
            if detector.ignored_commands:
                print(
                    f"🚫 Ignoring {len(detector.ignored_commands)} commands via .domdignore"
                )
            print(f"📊 Progress will be updated in {args.todo_file}")

        detector.test_commands(commands)

        # Print summary
        if not args.quiet:
            # Używamy rzeczywistej liczby przetestowanych komend, a nie początkowej listy
            total_tested = len(detector.successful_commands) + len(detector.failed_commands)
            print_summary(detector, total_tested)

        # Return exit code based on results
        return 1 if detector.failed_commands else 0

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
