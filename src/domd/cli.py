#!/usr/bin/env python3
"""
Enhanced CLI with immediate TODO.md creation and script generation
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Optional

from . import __version__
from .detector import ProjectCommandDetector


def create_parser() -> argparse.ArgumentParser:
    """Create enhanced argument parser."""
    parser = argparse.ArgumentParser(
        prog='domd',
        description='Project Command Detector with immediate TODO.md and script generation',
        epilog='''
Examples:
  domd                              # Scan, create TODO.md + todo.sh, then test
  domd --init-only                  # Only create TODO.md and todo.sh (no testing)
  domd --from-script                # Load commands from existing todo.sh
  domd --script-file my_tasks.sh    # Custom script filename
  domd --todo-file ISSUES.md        # Custom TODO filename

Workflow:
  1. domd --init-only               # Create files without testing
  2. Edit todo.sh if needed         # Remove unwanted commands
  3. ./todo.sh                      # Execute manually
  4. OR: domd --from-script         # Resume testing from script

Features:
  - TODO.md created immediately on start with all commands listed
  - todo.sh executable script with all commands for manual execution
  - Real-time TODO.md updates during testing
  - Resume from existing todo.sh script
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        '--path', '-p',
        type=str,
        default='.',
        help='Path to project directory (default: current directory)'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Only detect commands without creating files or executing'
    )

    parser.add_argument(
        '--init-only',
        action='store_true',
        help='Only create TODO.md and todo.sh files, do not test commands'
    )

    parser.add_argument(
        '--from-script',
        action='store_true',
        help='Load commands from existing todo.sh and test them'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed logging'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress all output except errors'
    )

    parser.add_argument(
        '--todo-file',
        type=str,
        default='TODO.md',
        help='TODO markdown file path (default: TODO.md)'
    )

    parser.add_argument(
        '--script-file',
        type=str,
        default='todo.sh',
        help='Executable script file path (default: todo.sh)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Command timeout in seconds (default: 60)'
    )

    parser.add_argument(
        '--exclude',
        action='append',
        help='Exclude specific file patterns (can be used multiple times)'
    )

    parser.add_argument(
        '--include-only',
        action='append',
        help='Include only specific file patterns (can be used multiple times)'
    )

    return parser


def setup_signal_handlers(detector: ProjectCommandDetector):
    """Setup signal handlers for graceful interruption."""

    def signal_handler(signum, frame):
        """Handle interruption signals gracefully."""
        print("\n🛑 Execution interrupted by user")
        print("💾 Saving current progress...")

        # Finalize TODO.md with current state
        if hasattr(detector, 'failed_commands') and hasattr(detector, 'successful_commands'):
            all_commands = detector.failed_commands + detector.successful_commands
            if all_commands:
                detector._finalize_todo_md(all_commands)
                print(f"📝 Progress saved to {detector.todo_file}")

        sys.exit(130)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
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

    if args.from_script and args.init_only:
        return "Cannot specify both --from-script and --init-only"

    return None


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Setup logging based on verbosity level."""
    import logging

    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_summary(detector: ProjectCommandDetector, total_commands: int) -> None:
    """Print execution summary."""
    successful = len(detector.successful_commands)
    failed = len(detector.failed_commands)

    print(f"\n{'=' * 60}")
    print("EXECUTION SUMMARY")
    print(f"{'=' * 60}")
    print(f"📊 Results:")
    print(f"   Total commands: {total_commands}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")

    if total_commands > 0:
        success_rate = (successful / total_commands) * 100
        print(f"   📈 Success rate: {success_rate:.1f}%")

    print(f"📝 Files created:")
    print(f"   📋 TODO file: {detector.todo_file}")
    print(f"   🔧 Script file: {detector.script_file}")

    if failed > 0:
        print(f"\n🔧 Next steps:")
        print(f"   1. Review failed commands in {detector.todo_file}")
        print(f"   2. Edit {detector.script_file} to remove problematic commands")
        print(f"   3. Run: ./{detector.script_file} to execute manually")
        print(f"   4. Or run: domd --from-script to resume testing")
    else:
        print(f"\n🎉 All commands executed successfully!")


def main() -> int:
    """Enhanced main entry point."""
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
        # Initialize enhanced detector
        detector = ProjectCommandDetector(
            project_path=args.path,
            timeout=args.timeout,
            exclude_patterns=args.exclude or [],
            include_patterns=args.include_only or [],
            todo_file=args.todo_file,
            script_file=args.script_file
        )

        if not args.quiet:
            print(f"TodoMD v{__version__} - Enhanced Project Command Detector")
            print(f"🔍 Project: {Path(args.path).resolve()}")
            print(f"📝 TODO file: {args.todo_file}")
            print(f"🔧 Script file: {args.script_file}")

        # Setup signal handlers
        setup_signal_handlers(detector)

        # Handle different modes
        if args.from_script:
            # Load commands from existing script
            if not Path(args.script_file).exists():
                print(f"❌ Script file {args.script_file} not found")
                print(f"💡 Run 'domd --init-only' first to create the script")
                return 1

            commands = detector.load_commands_from_script()
            if not commands:
                print("❌ No commands found in script file")
                return 1

            if not args.quiet:
                print(f"📥 Loaded {len(commands)} commands from {args.script_file}")

        else:
            # Scan project and create initial files
            commands = detector.scan_and_initialize()
            if not commands:
                return 0

        # Handle dry-run mode
        if args.dry_run:
            if not args.quiet:
                print("\n🔍 DRY RUN MODE - Commands found:")
                for i, cmd in enumerate(commands, 1):
                    print(f"{i:3d}. {cmd['description']}")
                    print(f"     Command: {cmd['command']}")
                    print(f"     Source:  {cmd['source']}")
                    print()
            return 0

        # Handle init-only mode
        if args.init_only:
            if not args.quiet:
                print(f"\n✅ Initialization complete!")
                print(f"📋 Created {args.todo_file} with {len(commands)} commands")
                print(f"🔧 Created executable {args.script_file}")
                print(f"\n💡 Next steps:")
                print(f"   • Review and edit {args.script_file} if needed")
                print(f"   • Run: ./{args.script_file} to execute commands manually")
                print(f"   • Or run: domd --from-script to test with TodoMD")
            return 0

        # Test commands with real-time updates
        if not args.quiet:
            print(f"\n🧪 Testing {len(commands)} commands...")
            print(f"📊 Progress will be updated in {args.todo_file}")

        detector.test_commands(commands)

        # Print summary
        if not args.quiet:
            print_summary(detector, len(commands))

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