"""Markdown reporter for TODO.md generation."""

import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base import BaseReporter


class TodoMDReporter(BaseReporter):
    """Generates a TODO.md file with failed commands and fix suggestions."""

    def __init__(self, output_file: Optional[Union[str, Path]] = None):
        """Initialize the TODO.md reporter.

        Args:
            output_file: Path to the TODO.md file
        """
        super().__init__(output_file or "TODO.md")

    def generate_report(self, data: Dict) -> str:
        """Generate the TODO.md content.

        Args:
            data: Dictionary containing 'failed_commands' and other metadata

        Returns:
            Formatted markdown content
        """
        failed_commands = data.get("failed_commands", [])
        successful_commands = data.get("successful_commands", [])

        content = [
            "# 🤖 TODO - LLM Task List for Command Fixes",
            "",
            "**📋 INSTRUCTIONS FOR LLM:**",
            "This file contains a list of broken commands that need to be fixed.",
            "Each task is a separate command that failed during testing.",
            "",
            "**🎯 YOUR MISSION:**",
            "1. **Analyze each failed command** and its error output",
            "2. **Identify the root cause** of the failure",
            "3. **Implement the fix** by modifying source code, config files, or dependencies",
            "4. **Test the fix** by running the command manually",
            "5. **Update progress** - when a command starts working, it will be moved to DONE.md automatically",
            "",
            "**📝 TASK FORMAT:**",
            "Each task has:",
            "- ❌ **Command** that failed",
            "- 📁 **Source file** where the command is defined",
            "- 🔴 **Error output** with full details",
            "- 💡 **Suggested actions** for fixing",
            "",
            "**🔄 WORKFLOW:**",
            "1. Pick a task from the list below",
            "2. Read the error details carefully",
            "3. Implement the fix",
            "4. Run `domd` to retest all commands",
            "5. Fixed commands will automatically move to DONE.md",
            "",
            "---",
            "",
            "**📊 Current Status:**",
            f"- **Project Path:** `{data.get('project_path', 'Unknown')}`",
            f"- **Failed Commands:** {len(failed_commands)}",
            f"- **Working Commands:** {len(successful_commands)} (see DONE.md)",
            f"- **Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        if not failed_commands:
            content.extend(
                [
                    "## 🎉 All Commands Working!",
                    "",
                    "✅ **No failed commands found!**",
                    "",
                    "All project commands are working correctly.",
                    "Check DONE.md for the list of working commands.",
                    "",
                ]
            )
        else:
            content.extend(
                [
                    f"## 🔧 Tasks to Fix ({len(failed_commands)} commands)",
                    "",
                    "Each section below is a separate task. Fix them one by one:",
                    "",
                ]
            )

            for i, cmd in enumerate(failed_commands, 1):
                content.extend(
                    [
                        f"### [ ] Task {i}: {cmd.get('description', 'Unnamed command')}",
                        "",
                        f"**📋 Command:** `{cmd.get('command', '')}`",
                        f"**📁 Source:** `{cmd.get('source', 'unknown')}`",
                        f"**⏱️ Timeout:** {cmd.get('timeout', 'N/A')}s",
                        f"**🔴 Return Code:** {cmd.get('return_code', 'N/A')}",
                        f"**⚡ Execution Time:** {cmd.get('execution_time', 0):.2f}s",
                        "",
                        "#### 🔴 Error Output:",
                        "",
                        "```bash",
                        "# Command that failed:",
                        cmd.get("command", ""),
                        "",
                        "# Error output:",
                        cmd.get("error", "No error output captured"),
                        "```",
                        "",
                        "#### 💡 Suggested Fix Actions:",
                        "",
                    ]
                )

                # Add any specific fix suggestions
                suggestions = self._generate_fix_suggestions(cmd)
                for suggestion in suggestions:
                    content.append(f"- [ ] {suggestion}")

                content.extend(["", "---", ""])

        return "\n".join(content)

    def _generate_fix_suggestions(self, cmd: Dict) -> List[str]:
        """Generate specific fix suggestions based on command and error.

        Args:
            cmd: Command dictionary with error details

        Returns:
            List of fix suggestions
        """
        suggestions = []
        error = (cmd.get("error") or "").lower()
        command = (cmd.get("command") or "").lower()

        # Common error patterns
        if "command not found" in error:
            cmd_name = command.split()[0] if command else "the command"
            suggestions.append(f"Check if `{cmd_name}` is installed and in your PATH")
            suggestions.append(
                f"Install the required package that provides `{cmd_name}`"
            )

        if "no such file or directory" in error:
            suggestions.append("Verify the file or directory exists")
            suggestions.append("Check for typos in the path")

        if "permission denied" in error:
            suggestions.append("Check file permissions")
            suggestions.append("Make the file executable if needed: `chmod +x <file>`")

        if not suggestions:
            suggestions = [
                "Check the command syntax and arguments",
                "Verify all required dependencies are installed",
                "Check for any environment variables that might be needed",
                "Look for typos or missing files",
            ]

        return suggestions
