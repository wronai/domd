"""Formatters for different output formats (Markdown, JSON, etc.)."""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """Base class for all formatters."""

    def __init__(self, **kwargs: Any):
        """Initialize the formatter.

        Args:
            **kwargs: Format-specific options
        """
        self.options = kwargs

    @abstractmethod
    def format_report(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """Format the report data.

        Args:
            data: Report data to format
            **kwargs: Additional formatting options

        Returns:
            Formatted report as a string
        """
        raise NotImplementedError("Subclasses must implement format_report()")

    def write_report(
        self, data: Dict[str, Any], output_path: Union[str, Path], **kwargs: Any
    ) -> None:
        """Write the formatted report to a file.

        Args:
            data: Report data to format
            output_path: Path to write the report to
            **kwargs: Additional formatting options
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        formatted = self.format_report(data, **kwargs)

        try:
            output_path.write_text(formatted, encoding="utf-8")
            logger.info("Report written to %s", output_path)
        except IOError as e:
            logger.error("Failed to write report to %s: %s", output_path, e)
            raise


class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown output."""

    def format_report(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """Format the report as Markdown.

        Args:
            data: Report data to format
            **kwargs: Additional formatting options
                - title: Report title
                - timestamp: Include timestamp (default: True)
                - include_successful: Include successful commands (default: True)
                - include_failed: Include failed commands (default: True)
                - include_ignored: Include ignored commands (default: False)

        Returns:
            Formatted Markdown report
        """
        title = kwargs.get("title", "Command Execution Report")
        include_timestamp = kwargs.get("timestamp", True)
        include_successful = kwargs.get("include_successful", True)
        include_failed = kwargs.get("include_failed", True)
        include_ignored = kwargs.get("include_ignored", False)

        lines = [f"# {title}", ""]

        if include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.extend([f"*Generated on {timestamp}*", ""])

        # Summary section
        total = len(data.get("commands", []))
        successful = len(data.get("successful_commands", []))
        failed = len(data.get("failed_commands", []))
        ignored = len(data.get("ignored_commands", []))

        lines.extend(
            [
                "## Summary",
                "",
                f"- **Total commands:** {total}",
                f"- **✅ Successful:** {successful}",
                f"- **❌ Failed:** {failed}",
                f"- **⏭️ Ignored:** {ignored}",
                "",
            ]
        )

        # Failed commands section
        if include_failed and data.get("failed_commands"):
            lines.extend(["## ❌ Failed Commands", ""])

            for i, cmd in enumerate(data["failed_commands"], 1):
                lines.extend(
                    [
                        f"### {i}. `{cmd.get('command', '')}`",
                        "",
                        f"**Source:** {cmd.get('source', 'Unknown')}",
                        f"**Exit Code:** {cmd.get('return_code', '?')}",
                        "",
                        "#### Error Output",
                        "```",
                        cmd.get("error", "No error output").strip(),
                        "```",
                        "",
                    ]
                )

        # Successful commands section
        if include_successful and data.get("successful_commands"):
            lines.extend(["## ✅ Successful Commands", ""])

            for i, cmd in enumerate(data["successful_commands"], 1):
                lines.extend(
                    [
                        f"### {i}. `{cmd.get('command', '')}`",
                        "",
                        f"**Source:** {cmd.get('source', 'Unknown')}",
                        f"**Duration:** {cmd.get('execution_time', 0):.2f}s",
                        "",
                    ]
                )

        # Ignored commands section
        if include_ignored and data.get("ignored_commands"):
            lines.extend(["## ⏭️ Ignored Commands", ""])

            for i, cmd in enumerate(data["ignored_commands"], 1):
                lines.extend(
                    [
                        f"### {i}. `{cmd.get('command', '')}`",
                        "",
                        f"**Source:** {cmd.get('source', 'Unknown')}",
                        f"**Reason:** {cmd.get('ignore_reason', 'Not specified')}",
                        "",
                    ]
                )

        return "\n".join(lines)


class JsonFormatter(BaseFormatter):
    """Formatter for JSON output."""

    def format_report(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """Format the report as JSON.

        Args:
            data: Report data to format
            **kwargs: Additional formatting options
                - pretty: Whether to pretty-print the JSON (default: True)

        Returns:
            Formatted JSON report
        """
        pretty = kwargs.get("pretty", True)

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


class ConsoleFormatter(BaseFormatter):
    """Formatter for console output."""

    def format_report(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """Format the report for console output.

        Args:
            data: Report data to format
            **kwargs: Additional formatting options
                - verbose: Include detailed output (default: False)
                - color: Use ANSI color codes (default: True)

        Returns:
            Formatted console output
        """
        verbose = kwargs.get("verbose", False)
        use_color = kwargs.get("color", True)

        def color_text(text: str, color: str) -> str:
            """Wrap text in ANSI color codes."""
            if not use_color:
                return text

            colors = {
                "red": "\033[91m",
                "green": "\033[92m",
                "yellow": "\033[93m",
                "blue": "\033[94m",
                "magenta": "\033[95m",
                "cyan": "\033[96m",
                "white": "\033[97m",
                "reset": "\033[0m",
                "bold": "\033[1m",
                "underline": "\033[4m",
            }
            return f"{colors.get(color, '')}{text}{colors['reset']}"

        lines = []

        # Header
        lines.append(color_text("=" * 40, "blue"))
        lines.append(color_text("COMMAND EXECUTION REPORT", "blue"))
        lines.append(color_text("=" * 40, "blue"))

        # Summary
        total = len(data.get("commands", []))
        successful = len(data.get("successful_commands", []))
        failed = len(data.get("failed_commands", []))
        ignored = len(data.get("ignored_commands", []))

        lines.append(color_text("\nSUMMARY", "bold"))
        lines.append(f"Total commands:  {total}")
        lines.append(f"{color_text('✅ Successful:', 'green')}  {successful}")
        lines.append(f"{color_text('❌ Failed:', 'red')}  {failed}")
        lines.append(f"{color_text('⏭️ Ignored:', 'yellow')}  {ignored}")

        # Failed commands
        if data.get("failed_commands"):
            lines.append(color_text("\nFAILED COMMANDS", "bold"))

            for i, cmd in enumerate(data["failed_commands"], 1):
                lines.extend(
                    [
                        f"\n{color_text(f'{i}.', 'red')} {cmd.get('command', '')}",
                        f"  {color_text('Source:', 'cyan')} {cmd.get('source', 'Unknown')}",
                        f"  {color_text('Exit Code:', 'cyan')} {cmd.get('return_code', '?')}",
                        f"  {color_text('Error:', 'red')}",
                        f"  {cmd.get('error', 'No error output').strip()}",
                    ]
                )

        # Verbose output for successful commands
        if verbose and data.get("successful_commands"):
            lines.append(color_text("\nSUCCESSFUL COMMANDS", "bold"))

            for i, cmd in enumerate(data["successful_commands"], 1):
                lines.extend(
                    [
                        f"\n{i}. {cmd.get('command', '')}",
                        f"  {color_text('Source:', 'cyan')} {cmd.get('source', 'Unknown')}",
                        f"  {color_text('Duration:', 'cyan')} {cmd.get('execution_time', 0):.2f}s",
                    ]
                )

        # Ignored commands
        if data.get("ignored_commands"):
            lines.append(color_text("\nIGNORED COMMANDS", "yellow"))

            for i, cmd in enumerate(data["ignored_commands"], 1):
                lines.extend(
                    [
                        f"\n{i}. {cmd.get('command', '')}",
                        f"  {color_text('Source:', 'cyan')} {cmd.get('source', 'Unknown')}",
                        f"  {color_text('Reason:', 'yellow')} {cmd.get('ignore_reason', 'Not specified')}",
                    ]
                )

        return "\n".join(lines)
