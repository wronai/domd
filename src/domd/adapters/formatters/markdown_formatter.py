"""
Implementacja formatera raportów w formacie Markdown.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from ...core.domain.command import Command
from ...core.ports.report_formatter import ReportFormatter

logger = logging.getLogger(__name__)


class MarkdownFormatter(ReportFormatter):
    """
    Implementacja formatera raportów w formacie Markdown.
    """

    def format_commands(self, commands: List[Command], title: str) -> str:
        """
        Formatuje listę komend do formatu Markdown.

        Args:
            commands: Lista komend do sformatowania
            title: Tytuł raportu

        Returns:
            Sformatowany raport Markdown jako tekst
        """
        if not commands:
            return f"# {title}\n\nNo commands found.\n"

        lines = [f"# {title}", ""]

        for i, cmd in enumerate(commands, 1):
            # Dodaj nagłówek komendy
            lines.append(f"## {i}. {cmd.description}")
            lines.append("")

            # Dodaj informacje o komendzie
            lines.append(f"**Command:** `{cmd.command}`")
            lines.append(f"**Source:** {cmd.source}")
            lines.append(f"**Type:** {cmd.type}")

            # Dodaj informacje o wyniku wykonania, jeśli dostępne
            if cmd.result:
                lines.append(
                    f"**Status:** {'✅ Success' if cmd.result.success else '❌ Failed'}"
                )
                lines.append(f"**Return Code:** {cmd.result.return_code}")
                lines.append(f"**Execution Time:** {cmd.result.execution_time:.2f}s")

                if cmd.result.error:
                    lines.append(f"**Error:** {cmd.result.error}")

                if cmd.result.stdout:
                    lines.append("\n**Output:**")
                    lines.append("```")
                    lines.append(
                        cmd.result.stdout[:500]
                        + ("..." if len(cmd.result.stdout) > 500 else "")
                    )
                    lines.append("```")

                if cmd.result.stderr:
                    lines.append("\n**Error Output:**")
                    lines.append("```")
                    lines.append(
                        cmd.result.stderr[:500]
                        + ("..." if len(cmd.result.stderr) > 500 else "")
                    )
                    lines.append("```")

            # Dodaj metadane, jeśli dostępne
            if cmd.metadata:
                lines.append("\n**Metadata:**")
                for key, value in cmd.metadata.items():
                    lines.append(f"- **{key}:** {value}")

            # Dodaj pustą linię między komendami
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def write_report(self, content: str, output_path: Path) -> Path:
        """
        Zapisuje raport do pliku Markdown.

        Args:
            content: Zawartość raportu
            output_path: Ścieżka do pliku wyjściowego

        Returns:
            Ścieżka do zapisanego pliku
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Report written to {output_path}")
            return output_path
        except Exception as e:
            logger.error(
                f"Error writing report to {output_path}: {str(e)}", exc_info=True
            )
            raise
