"""Handler for executing and managing project commands."""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...services.command_runner import CommandRunner
from ..models import Command

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handler for executing and managing project commands."""

    # Common non-command patterns that should be filtered out
    NON_COMMAND_PATTERNS = [
        r"^#",  # Comments
        r"^\s*$",  # Empty lines
        r"^source\s+",  # Shell source commands
        r"^\.\s+",  # Shell source alternative
        r"^exec\s+",  # Shell exec commands
        r"^export\s+",  # Environment exports
        r"^unset\s+",  # Environment unset
        r"^cd\s+",  # Directory changes
        r"^echo\s+",  # Echo statements
        r"^\s*(true|false|:)\s*$",  # No-op commands
    ]

    def __init__(
        self,
        project_path: Path,
        command_runner: CommandRunner,
        timeout: int = 60,
        ignore_patterns: Optional[List[str]] = None,
    ):
        """Initialize the CommandHandler.

        Args:
            project_path: Path to the project root
            command_runner: CommandRunner instance for executing commands
            timeout: Default command execution timeout in seconds
            ignore_patterns: List of command patterns to ignore
        """
        self.project_path = project_path
        self.command_runner = command_runner
        self.timeout = timeout
        self.ignore_patterns = ignore_patterns or []
        self._compiled_non_command_patterns = [
            re.compile(pattern) for pattern in self.NON_COMMAND_PATTERNS
        ]

        # Command storage - can contain both Command objects and dictionaries
        self.failed_commands: List[Union[Command, Dict[str, Any]]] = []
        self.successful_commands: List[Union[Command, Dict[str, Any]]] = []
        self.ignored_commands: List[Union[Command, Dict[str, Any]]] = []
        self.skipped_commands: List[Dict[str, Any]] = []

    def test_commands(self, commands: List[Union[Command, Dict]]) -> None:
        """Test a list of commands and update internal state.

        Args:
            commands: List of Command objects or command dictionaries to test
        """
        self.failed_commands = []
        self.successful_commands = []
        self.ignored_commands = []
        self.skipped_commands = []

        for cmd in commands:
            try:
                # Skip None or empty commands
                if not cmd:
                    continue

                # Extract command string for logging
                cmd_str = self._extract_command_string(cmd)
                if not cmd_str or not cmd_str.strip():
                    continue

                # Check if command should be ignored
                if self.should_ignore_command(cmd):
                    self._handle_ignored_command(cmd)
                    continue

                # Validate command format and content
                is_valid, reason = self.is_valid_command(cmd)
                if not is_valid:
                    logger.debug(
                        f"Skipping invalid command: {cmd_str[:100]}... Reason: {reason}"
                    )
                    self._handle_skipped_command(cmd, reason)
                    continue

                # Execute the command
                result = self.execute_single_command(cmd)

                # Update command state based on result
                if result.get("success"):
                    self._handle_successful_command(cmd, result)
                else:
                    self._handle_failed_command(cmd, result)

            except Exception as e:
                # Log the full error but don't expose internal details to the user
                logger.debug(f"Internal error processing command: {e}", exc_info=True)
                error_msg = "An internal error occurred while processing this command"
                if isinstance(e, (PermissionError, FileNotFoundError)):
                    error_msg = str(e)  # These are usually safe to show
                self._handle_error(cmd, error_msg)

    def execute_single_command(self, cmd_info: Union[Command, Dict]) -> Dict[str, Any]:
        """Execute a single command and return the result.

        Args:
            cmd_info: Either a Command object or a dictionary containing command info

        Returns:
            Dictionary with command execution results
        """
        if isinstance(cmd_info, Command):
            command = cmd_info.command
            cwd = cmd_info.metadata.get("cwd", self.project_path)
            env = cmd_info.metadata.get("env", {})
            timeout = cmd_info.metadata.get("timeout", self.timeout)
        else:
            command = cmd_info.get("command", "")
            cwd = cmd_info.get("cwd", self.project_path)
            env = cmd_info.get("env", {})
            timeout = cmd_info.get("timeout", self.timeout)

        try:
            start_time = time.time()
            result = self.command_runner.run(
                command=command,
                cwd=cwd,
                env=env,
                timeout=timeout,
            )
            execution_time = time.time() - start_time

            return {
                "success": result.return_code == 0,
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return {
                "success": False,
                "return_code": -1,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
            }

    def is_valid_command(self, command: Union[str, Dict, Command]) -> tuple[bool, str]:
        """Check if a command is valid and should be executed.

        Args:
            command: Command to validate (string, dict, or Command object)

        Returns:
            Tuple of (is_valid, reason) where is_valid is a boolean and reason is a string
        """
        cmd_str = self._extract_command_string(command)
        if not cmd_str or not cmd_str.strip():
            return False, "Empty command"

        cmd_str = cmd_str.strip()

        # Check for empty or whitespace-only commands
        if not cmd_str:
            return False, "Empty command"

        # Check for commands that are too long (likely not actual commands)
        if len(cmd_str) > 1000:
            return False, "Command is too long to be a valid shell command"

        # Check for commands that are just numbers or special characters
        if re.match(r"^[\d\s\W]+$", cmd_str):
            return False, "Command contains only numbers or special characters"

        # Enhanced markdown detection with more patterns
        markdown_patterns = [
            (r"^#+\s+", "Markdown header"),  # Headers (#, ##, ###)
            (r"^[-*+]\s+", "Markdown list item"),  # List items (-, *, +)
            (r"^\d+\.\s+", "Numbered list item"),  # Numbered lists (1., 2., etc.)
            (r"^\|.*\|$", "Markdown table"),  # Tables (| col1 | col2 |)
            (r"^```", "Markdown code block"),  # Code blocks
            (r"`[^`]+`", "Inline code"),  # Inline code
            (r"\*\*[^*]+\*\*", "Bold text"),  # **bold**
            (r"__[^_]+__", "Underlined text"),  # __underline__
            (r"~~[^~]+~~", "Strikethrough"),  # ~~strikethrough~~
            (r"\[.*\]\(.*\)", "Markdown link"),  # [text](url)
            (r"!\[.*\]\(.*\)", "Markdown image"),  # ![alt](src)
            (r"^>\s+", "Blockquote"),  # > quote
            (r"^\s*\*\*\*+\s*$", "Horizontal rule"),  # ***
            (r"^\s*---\s*$", "Horizontal rule"),  # ---
            (r"^\s*___\s*$", "Horizontal rule"),  # ___
        ]

        for pattern, description in markdown_patterns:
            if re.search(pattern, cmd_str, re.MULTILINE):
                return False, f"Appears to be {description}"

        # Check for directory listing patterns (tree output)
        dir_listing_indicators = [
            r"^[│└├─]",  # Tree-like directory structure
            r"\s+\d+\s+\w+\s+\d+\s+[\d:]+\s+",  # File size and date
            r"\d+\s+[BKMGTPEZY]B\s*$",  # File sizes
            r"^total \d+$",  # 'total X' line
        ]

        for pattern in dir_listing_indicators:
            if re.search(pattern, cmd_str, re.MULTILINE):
                return False, "Appears to be directory listing output"

        # Check for documentation patterns
        doc_patterns = [
            (r"^\s*[A-Z][A-Za-z0-9_\s-]+:", "Documentation line"),  # Key: value
            (r"^\s*<!--.*-->\s*$", "HTML comment"),  # HTML comments
            (r"^\s*//", "Single-line comment"),  # // comments
            (r"^\s*#", "Comment"),  # # comments
            (r"^\s*/\*.*\*/\s*$", "Multi-line comment"),  # /* comments */
        ]

        for pattern, description in doc_patterns:
            if re.search(pattern, cmd_str):
                return False, f"Appears to be {description}"

        # Check against non-command patterns
        for pattern in self._compiled_non_command_patterns:
            if pattern.search(cmd_str):
                return False, f"Matches non-command pattern: {pattern.pattern}"

        # Check for suspicious command patterns
        suspicious_patterns = [
            (r"^\s*\w+\s*=\s*\S+\s*$", "Variable assignment without command"),
            (r"^\s*\{\s*\}\s*$", "Empty code block"),
            (r"^\s*\[\s*\]\s*$", "Empty array"),
            (r"^\s*\{\s*$", "Opening brace without content"),
            (r"^\s*\}\s*$", "Closing brace without content"),
        ]

        for pattern, reason in suspicious_patterns:
            if re.search(pattern, cmd_str):
                return False, f"Suspicious command: {reason}"

        # Check for common error patterns
        if any(
            s in cmd_str.lower()
            for s in ["error:", "warning:", "exception:", "traceback"]
        ):
            return False, "Appears to be an error or warning message"

        # Check for documentation-style lines (e.g., "parameter: value")
        if re.match(r"^\s*[A-Za-z][A-Za-z0-9_\s-]*:", cmd_str):
            return False, "Appears to be documentation or configuration"

        # Check for suspicious patterns that might indicate internal errors
        if any(s in cmd_str.lower() for s in ["traceback", "exception", "stacktrace"]):
            return False, "Appears to contain error output"

        # Check for internal tool paths that shouldn't be executed
        if any(
            s in cmd_str
            for s in ["/tmp/", "/var/", "/usr/local/", "~/.cache/", "/dev/"]
        ):
            return False, "References internal tool paths"

        # Check for commands that are just numbers or special characters
        if re.match(r"^[\d\s\W]+$", cmd_str):
            return False, "Contains only numbers or special characters"

        # Check for very long commands that are likely not actual commands
        if len(cmd_str) > 500:  # Arbitrary length threshold
            return False, "Command is too long to be a valid shell command"

        return True, ""

    def should_ignore_command(self, command: Union[str, Dict, Command]) -> bool:
        """Check if a command should be ignored based on ignore patterns.

        Args:
            command: Command to check (string, dict, or Command object)

        Returns:
            True if the command should be ignored, False otherwise
        """
        if not self.ignore_patterns:
            return False

        cmd_str = self._extract_command_string(command)
        if not cmd_str:
            return True

        return any(pattern in cmd_str for pattern in self.ignore_patterns)

    def _extract_command_string(self, command: Union[str, Dict, Command]) -> str:
        """Extract the command string from various input types."""
        if isinstance(command, str):
            return command
        if isinstance(command, dict):
            return command.get("command", "")
        if hasattr(command, "command"):
            return command.command
        return str(command)

    def _handle_ignored_command(self, command: Union[Command, Dict]) -> None:
        """Handle a command that should be ignored."""
        if isinstance(command, dict):
            command["ignored"] = True
        else:
            setattr(command, "ignored", True)
        self.ignored_commands.append(command)
        logger.debug(f"Ignored command: {self._extract_command_string(command)}")

    def _handle_successful_command(
        self, command: Union[Command, Dict], result: Dict[str, Any]
    ) -> None:
        """Handle a successfully executed command."""
        self._update_command_result(command, result, success=True)
        self.successful_commands.append(command)
        logger.debug(f"Command succeeded: {self._extract_command_string(command)}")

    def _handle_failed_command(
        self, command: Union[Command, Dict], result: Dict[str, Any]
    ) -> None:
        """Handle a failed command execution."""
        self._update_command_result(command, result, success=False)
        self.failed_commands.append(command)
        logger.warning(f"Command failed: {self._extract_command_string(command)}")

    def _handle_skipped_command(
        self, command: Union[Command, Dict], reason: str
    ) -> None:
        """Handle a command that was skipped during validation."""
        if isinstance(command, dict):
            command.update(
                {
                    "skipped": True,
                    "skip_reason": reason,
                    "success": False,
                    "return_code": -2,  # Special code for skipped commands
                }
            )
            self.skipped_commands.append(command)
        else:
            # For Command objects, we'll create a dict representation
            cmd_dict = {
                "command": command.command,
                "skipped": True,
                "skip_reason": reason,
                "success": False,
                "return_code": -2,
                "source": getattr(command, "source", ""),
                "metadata": getattr(command, "metadata", {}),
            }
            self.skipped_commands.append(cmd_dict)

        logger.debug(
            f"Skipped command: {self._extract_command_string(command)}. Reason: {reason}"
        )

    def _handle_error(self, command: Union[Command, Dict], error: str) -> None:
        """Handle an error during command execution.

        Args:
            command: The command that failed
            error: User-friendly error message (not the raw exception)
        """
        result = {
            "success": False,
            "error": error,
            "return_code": -1,
            "stdout": "",
            "stderr": error,
        }
        self._update_command_result(command, result, success=False)
        self.failed_commands.append(command)
        # Log at debug level to avoid cluttering user output with internal errors
        logger.debug(f"Command execution failed: {error}")

    def _update_command_result(
        self, command: Union[Command, Dict], result: Dict[str, Any], success: bool
    ) -> None:
        """Update a command object with execution results."""
        if isinstance(command, dict):
            command.update(
                {
                    "success": success,
                    "return_code": result.get("return_code", -1),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "error": result.get("error"),
                    "execution_time": result.get("execution_time", 0),
                }
            )
        else:
            command.success = success
            command.return_code = result.get("return_code", -1)
            command.stdout = result.get("stdout", "")
            command.stderr = result.get("stderr", "")
            command.error = result.get("error")
            command.execution_time = result.get("execution_time", 0)
