#!/usr/bin/env python3
"""
Enhanced CLI for domd with streaming TODO.md updates
"""

import argparse
import sys
import signal
import time
import threading
from pathlib import Path
from typing import Optional

from . import __version__
from .detector import ProjectCommandDetector


class ProgressMonitor:
    """Monitor and display progress during command execution."""

    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start monitoring the output file for changes."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_file)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_file(self):
        """Monitor file changes and show progress."""
        last_size = 0
        dots = 0

        while self.monitoring:
            try:
                if self.output_file.exists():
                    current_size = self.output_file.stat().st_size
                    if current_size != last_size:
                        # File updated, show progress
                        print(".", end="", flush=True)
                        dots += 1
                        if dots >= 50:  # New line after 50 dots
                            print()
                            dots = 0
                        last_size = current_size

                time.sleep(0.5)  # Check every 500ms
            except Exception:
                pass  # Ignore file access errors


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog='domd',
        description='Project Command Detector with streaming TODO.md updates',
        epilog='''
Examples:
  domd                              # Scan with streaming updates
  domd --no-streaming               # Traditional mode (no live updates)
  domd --path /path/to/project      # Scan specific project
  domd --dry-run                    # Preview without execution
  domd --output ISSUES.md           # Custom output file
  domd --watch                      # Show live progress indicators

Streaming Features:
  - TODO.md updates in real-time during execution
  - Progress tracking and status updates
  - Safe interruption with partial results saved
  - Current command status and recent completions
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
        help='Only detect commands without executing them'
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
        '--output', '-o',
        type=str,
        default='TODO.md',
        help='Output file for failed commands (default: TODO.md)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'text'],
        default='markdown',
        help='Output format (default: markdown)'
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

    # Streaming-specific options
    parser.add_argument(
        '--no-streaming',
        action='store_true',
        help='Disable streaming updates (traditional mode - generate file only at end)'
    )

    parser.add_argument(
        '--watch',
        action='store_true',
        help='Show live progress indicators during execution'
    )

    return parser


def setup_signal_handlers(detector: ProjectCommandDetector, output_file: str):
    """Setup signal handlers for graceful interruption."""

    def signal_handler(signum, frame):
        """Handle interruption signals gracefully."""
        print("\n🛑 Execution interrupted by user")
        print("💾 Saving current progress to TODO.md...")

        # Finalize the current state
        if hasattr(detector, 'todo_writer') and detector.todo_writer:
            detector.todo_writer.finalize_file(detector.failed_commands)

        # Show current status
        total_tested = len(detector.failed_commands)  # Simplified for now
        if total_tested > 0:
            failed = len(detector.failed_commands)
            print(f"\n📊 Progress at interruption:")
            print(f"   Commands tested: {total_tested}")
            print(f"   ❌ Failed: {failed}")
            print(f"   📝 Partial results saved to: {output_file}")

        sys.exit(130)  # Standard exit code for SIGINT

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


def validate_args(args: argparse.Namespace) -> Optional[str]:
    """Validate command line arguments."""
    # Check if project path exists
    project_path = Path(args.path)
    if not project_path.exists():
        return f"Project path does not exist: {project_path}"

    if not project_path.is_dir():
        return f"Project path is not a directory: {project_path}"

    # Check timeout value
    if args.timeout <= 0:
        return "Timeout must be a positive integer"

    # Check if verbose and quiet are both specified
    if args.verbose and args.quiet:
        return "Cannot specify both --verbose and --quiet"

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
    failed = len(detector.failed_commands)
    success = total_commands - failed

    print(f"\n{'=' * 50}")
    print("EXECUTION SUMMARY")
    print(f"{'=' * 50}")
    print(f"✅ Successful: {success}/{total_commands}")
    print(f"❌ Failed: {failed}/{total_commands}")

    if total_commands > 0:
        success_rate = (success / total_commands) * 100
        print(f"📊 Success rate: {success_rate:.1f}%")

    if failed > 0:
        print(f"📝 Check TODO.md for failed command details")
    else:
        print(f"🎉 All commands executed successfully!")


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    error_msg = validate_args(args)
    if error_msg:
        print(f"Error: {error_msg}", file=sys.stderr)
        return 1

    # Setup logging
    setup_logging(args.verbose, args.quiet)

    try:
        # Initialize detector
        detector = ProjectCommandDetector(
            project_path=args.path,
            timeout=args.timeout,
            exclude_patterns=args.exclude or [],
            include_patterns=args.include_only or []
        )

        if not args.quiet:
            print(f"domd v{__version__}")
            print(f"Scanning project: {Path(args.path).resolve()}")

        # Setup signal handlers
        setup_signal_handlers(detector, args.output)

        # Scan project for commands
        commands = detector.scan_project()

        if not commands:
            if not args.quiet:
                print("No commands found to test.")
            return 0

        if not args.quiet:
            print(f"Found {len(commands)} commands to test")

        # Handle dry-run mode
        if args.dry_run:
            if not args.quiet:
                print("\n🔍 DRY RUN MODE - Commands found:")
                for i, cmd in enumerate(commands, 1):
                    print(f"{i:3d}. {cmd['description']}")
                    print(f"     Command: {cmd['command']}")
                    print(f"     Source:  {cmd['source']}")
                    if args.verbose:
                        print(f"     Type:    {cmd.get('type', 'unknown')}")
                    print()
            return 0

        # Test commands
        if not args.quiet:
            print(f"\nTesting commands...")

        detector.test_commands(commands)

        # Generate output file
        detector.generate_output_file(args.output, args.format)

        # Print summary
        if not args.quiet:
            print_summary(detector, len(commands))

        # Return exit code based on results
        return 1 if detector.failed_commands else 0

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())