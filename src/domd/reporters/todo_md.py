"""
Module for generating and updating TODO.md files based on command results.
"""

from pathlib import Path
from typing import List, Optional, Union

from domd.core.commands import Command, CommandResult


class TodoMdReporter:
    """Reporter that generates and updates TODO.md files based on command results."""

    def __init__(self, todo_file: Union[str, Path] = "TODO.md"):
        """Initialize the reporter with the path to the TODO.md file.

        Args:
            todo_file: Path to the TODO.md file (default: "TODO.md")
        """
        self.todo_file = Path(todo_file).resolve()

    def generate_report(
        self,
        commands: List[Command],
        results: List[CommandResult],
        failed_commands: Optional[List[Command]] = None,
    ) -> str:
        """Generate a markdown report of commands and their results.

        Args:
            commands: List of Command objects that were executed
            results: List of CommandResult objects from the execution
            failed_commands: Optional list of commands that failed to execute

        Returns:
            str: Generated markdown content
        """
        if failed_commands is None:
            failed_commands = []

        # Group commands by their source file
        commands_by_source = {}
        for cmd in commands:
            source = cmd.source or "Unknown"
            if source not in commands_by_source:
                commands_by_source[source] = []
            commands_by_source[source].append(cmd)

        # Generate markdown sections
        sections = ["# Project Commands\n"]

        # Add sections for each source file
        for source, cmds in commands_by_source.items():
            sections.append(f"## {source}\n")

            for cmd in sorted(cmds, key=lambda c: c.command):
                # Find the corresponding result by matching command strings
                result = next((r for r in results if r.command == cmd.command), None)

                # Determine status
                if cmd in failed_commands:
                    status = "❌ Failed to execute"
                elif result and not result.success:
                    status = f"❌ Failed (exit code: {result.return_code})"
                else:
                    status = "✅ Success"

                # Add command info
                sections.append(f"### {cmd.command}\n")
                sections.append(f"- **Type:** {cmd.type}")
                sections.append(
                    f"- **Description:** {cmd.description or 'No description'}"
                )
                sections.append(f"- **Command:** `{cmd.command}`")

                if result:
                    sections.append(f"- **Status:** {status}")
                    if result.stdout:
                        sections.append(f"- **Output:**\n```\n{result.stdout}\n```")
                    if result.stderr:
                        sections.append(f"- **Errors:**\n```\n{result.stderr}\n```")
                    if (
                        hasattr(result, "execution_time")
                        and result.execution_time is not None
                    ):
                        sections.append(f"- **Duration:** {result.execution_time:.2f}s")
                else:
                    sections.append("- **Status:** Not executed")

                sections.append("")

            sections.append("")

        return "\n".join(sections).strip()

    def write_report(self, content: str) -> None:
        """Write the generated report to the TODO.md file.

        Args:
            content: The markdown content to write
        """
        self.todo_file.parent.mkdir(parents=True, exist_ok=True)
        self.todo_file.write_text(content, encoding="utf-8")

    def update_report(
        self,
        commands: List[Command],
        results: List[CommandResult],
        failed_commands: Optional[List[Command]] = None,
    ) -> None:
        """Generate and write the report in one step.

        Args:
            commands: List of Command objects that were executed
            results: List of CommandResult objects from the execution
            failed_commands: Optional list of commands that failed to execute
        """
        content = self.generate_report(commands, results, failed_commands)
        self.write_report(content)
