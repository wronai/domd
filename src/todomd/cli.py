#!/usr/bin/env python3
"""
Command Line Interface for TodoMD
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .detector import ProjectCommandDetector


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog='todomd',
        description='Project Command Detector - Automatically detects and tests project commands',
        epilog='Examples:\n'
               '  todomd                          # Scan current directory\n'
               '  todomd --path /path/to/project  # Scan specific project\n'
               '  todomd --dry-run                # Preview commands without executing\n'
               '  todomd --output custom.md       # Custom output file',
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
        help='Enable verbose output'
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

    return parser


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

    if failed > 0:
        success_rate = (success / total_commands) * 100
        print(f"📊 Success rate: {success_rate:.1f}%")
        print(f"📝 Check output file for failed command details")
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
            print(f"TodoMD v{__version__}")
            print(f"Scanning project: {Path(args.path).resolve()}")

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

        # Execute commands
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