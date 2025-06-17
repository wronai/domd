"""Handler for executing and managing project commands."""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from domd.core.command_execution.command_runner import CommandRunner

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

        This method performs multiple validations to ensure the command is a valid shell command
        and not markdown, documentation, or other non-command content.

        Args:
            command: Command to validate (string, dict, or Command object)

        Returns:
            Tuple of (is_valid, reason) where is_valid is a boolean and reason is a string
        """
        logger.debug(f"Validating command: {command}")

        cmd_str = self._extract_command_string(command)
        if not cmd_str or not cmd_str.strip():
            logger.debug("Empty command string")
            return False, "Empty command"

        cmd_str = cmd_str.strip()
        logger.debug(
            f"Processing command: {cmd_str[:100]}"
            + ("..." if len(cmd_str) > 100 else "")
        )

        # Check for empty or whitespace-only commands
        if not cmd_str:
            logger.debug("Command is empty after stripping")
            return False, "Empty command"

        # Check for very long commands (likely not actual commands)
        if len(cmd_str) > 500:
            logger.debug(f"Command too long ({len(cmd_str)} > 500 characters)")
            return False, "Command is too long to be a valid shell command"

        # Check for commands that are just numbers or special characters
        if re.match(r"^[\d\s\W]+$", cmd_str):
            logger.debug("Command contains only numbers or special characters")
            return False, "Command contains only numbers or special characters"

        # Check for common non-command patterns first (fast checks)
        for pattern in self._compiled_non_command_patterns:
            if pattern.search(cmd_str):
                logger.debug(f"Matches non-command pattern: {pattern.pattern}")
                return False, f"Matches non-command pattern: {pattern.pattern}"

        # Enhanced markdown and documentation detection with detailed logging
        markdown_patterns = [
            # Markdown patterns
            (r"^#+\s+", "Markdown header"),
            (r"^[-*+]\s+", "Markdown list item"),
            (r"^\d+\.\s+", "Numbered list item"),
            (r"^\|.*\|$", "Markdown table"),
            (r"^```", "Markdown code block"),
            (r"`[^`]+`", "Inline code"),
            (r"\*\*[^*]+\*\*", "Bold text"),
            (r"__[^_]+__", "Underlined text"),
            (r"~~[^~]+~~", "Strikethrough"),
            (r"\[.*\]\(.*\)", "Markdown link"),
            (r"^>\s+", "Blockquote"),
            (r"^\s*<!--.*-->\s*$", "HTML comment"),
            # Documentation patterns
            (r"^For\s+\w+\s+information", "Documentation line"),
            (r"^To\s+\w+", "Documentation line"),
            (r"^This\s+\w+", "Documentation line"),
            (r"^The\s+\w+", "Documentation line"),
            (r"^[A-Z][a-z]+\s+the\s+\w+", "Documentation line"),
            (r"^[A-Z][a-z]+\s+[A-Z][a-z]+", "Documentation line"),
            (r"^[A-Z][a-z]+\s+[a-z]+\s+[a-z]+", "Documentation line"),
            # Directory tree patterns
            (r"^\s*[│├└─]+\s+", "Directory tree"),
            (r"^\s*[│├└─]+$", "Directory tree connector"),
            (r"^\s*\d+\s+[a-z]+\s+\d+\s+\d{2}:\d{2}\s+", "Directory listing"),
        ]

        logger.debug(f"Checking against {len(markdown_patterns)} markdown patterns")

        # Additional patterns to check with detailed logging
        additional_patterns = [
            # Common documentation phrases
            (r"(?i)for more information", "Documentation phrase"),
            (r"(?i)see also", "Documentation phrase"),
            (r"(?i)example:", "Documentation phrase"),
            (r"(?i)note:", "Documentation note"),
            (r"(?i)warning:", "Warning message"),
            (r"(?i)important:", "Important note"),
            (r"(?i)tip:", "Tip note"),
            (r"(?i)caution:", "Caution note"),
            (r"(?i)see the", "Documentation reference"),
            (r"(?i)refer to", "Documentation reference"),
            # Common command-like patterns that should be ignored
            (r"^\s*\w+\s*=\s*\S+\s*$", "Variable assignment"),
            (r"^\s*\{\s*\}\s*$", "Empty code block"),
            (r"^\s*\[\s*\]\s*$", "Empty array"),
            (r"^\s*\{\s*$", "Opening brace"),
            (r"^\s*\}\s*$", "Closing brace"),
            # Common error patterns
            (r"(?i)error:", "Error message"),
            (r"(?i)exception:", "Exception message"),
            (r"(?i)traceback", "Traceback message"),
            (r"(?i)stacktrace", "Stack trace"),
            # Path patterns
            (r"^\s*/[\w/.-]+$", "File path"),
            (r"^\s*~?/[\w/.-]+$", "Home-relative path"),
            (r"^\s*\./[\w/.-]+$", "Relative path"),
            # URL patterns
            (r"https?://\S+", "URL"),
            (r"www\.\S+\.\w+", "Web address"),
            # Email patterns
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "Email address"),
        ]

        logger.debug(f"Checking against {len(additional_patterns)} additional patterns")

        # Combine all patterns
        all_patterns = markdown_patterns + additional_patterns
        logger.debug(f"Total patterns to check: {len(all_patterns)}")

        # Check all patterns with detailed logging
        for pattern, description in all_patterns:
            try:
                if re.search(pattern, cmd_str, re.IGNORECASE):
                    logger.debug(
                        f"Pattern matched - Type: {description}, Pattern: {pattern}"
                    )
                    return False, f"{description} detected"
            except Exception as e:
                logger.error(f"Error checking pattern '{pattern}': {str(e)}")
                continue

        logger.debug("No markdown or documentation patterns matched")

        # Check for command-like patterns that might be valid
        valid_command_indicators = [
            (r"^\s*[a-z][a-z0-9_-]+(\s+[a-z][a-z0-9_-]+)*\s*$", "Simple command"),
            (r"^\s*[a-z][a-z0-9_-]+\s+[a-z][a-z0-9_-]+", "Command with argument"),
            (r"^\s*[a-z][a-z0-9_-]+\s+--?[a-z0-9-]+", "Command with option"),
            (
                r"^\s*[a-z][a-z0-9_-]+\s+[a-z][a-z0-9_-]+\s+[a-z][a-z0-9_-]+",
                "Command with multiple args",
            ),
        ]

        logger.debug("Checking command against valid command patterns")

        # Track if any command pattern matches
        command_matched = False
        for pattern, pattern_type in valid_command_indicators:
            try:
                if re.match(pattern, cmd_str, re.IGNORECASE):
                    logger.debug(f"Command matches {pattern_type} pattern: {pattern}")
                    command_matched = True
                    break
            except Exception as e:
                logger.error(f"Error checking command pattern '{pattern}': {str(e)}")

        if not command_matched:
            logger.debug("Command does not match any valid command patterns")
            return False, "Does not match valid command patterns"

        # Check for commands that are too short or too simple
        if len(cmd_str.split()) == 1 and len(cmd_str) < 3:
            logger.debug("Command is too short or simple")
            return False, "Command is too short or simple"

        # Check for commands that are too long (likely not actual commands)
        if len(cmd_str) > 500:
            logger.debug(f"Command is too long ({len(cmd_str)} characters)")
            return False, "Command is too long to be a valid shell command"

        # Check for commands that are just numbers or special characters
        if re.match(r"^[\d\s\W]+$", cmd_str):
            logger.debug("Command contains only numbers or special characters")
            return False, "Command contains only numbers or special characters"

        # Check for internal tool paths that shouldn't be executed
        internal_paths = ["/tmp/", "/var/", "/usr/local/", "~/.cache/", "/dev/"]
        for path in internal_paths:
            if path in cmd_str:
                logger.debug(f"Command references internal tool path: {path}")
                return False, f"References internal tool path: {path}"

        logger.debug("Command passed all validation checks")
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
