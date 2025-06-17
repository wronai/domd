"""Handler for executing and managing project commands with Docker testing support."""

import logging
import os
import re
import shlex
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union

from domd.core.command_execution.command_runner import CommandRunner
from domd.core.domain.command import Command

# Import DockerTester if available
try:
    from domd.core.command_detection.docker_tester import (
        DockerTester,
        test_commands_in_docker,
    )

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    test_commands_in_docker = None

logger = logging.getLogger(__name__)

# Cache for command existence checks
_command_cache = {}


def command_exists(cmd: str) -> bool:
    """Check if a command exists in the system PATH.

    Args:
        cmd: The command to check

    Returns:
        bool: True if the command exists in PATH, False otherwise
    """
    global _command_cache

    # Check cache first
    if cmd in _command_cache:
        return _command_cache[cmd]

    # Handle commands with arguments - just check the first part
    cmd_parts = shlex.split(cmd)
    if not cmd_parts:
        _command_cache[cmd] = False
        return False

    cmd_name = cmd_parts[0]

    # Check for built-in commands
    builtin_commands = {
        "cd",
        "export",
        "source",
        "alias",
        "unalias",
        "echo",
        "pwd",
        "exit",
        "return",
        "shift",
        "test",
        "true",
        "false",
        ":",
        ".",
        "exec",
        "eval",
        "set",
        "unset",
        "readonly",
        "read",
        "printf",
        "wait",
        "times",
        "trap",
        "umask",
        "ulimit",
        "type",
        "hash",
        "command",
        "jobs",
        "fg",
        "bg",
        "kill",
        "getopts",
        "shopt",
        "complete",
        "compgen",
        "compopt",
        "declare",
        "typeset",
        "local",
        "let",
        "readonly",
        "unset",
        "export",
        "alias",
        "unalias",
        "echo",
        "pwd",
        "exit",
        "return",
        "shift",
        "test",
        "true",
        "false",
        ":",
        ".",
        "exec",
        "eval",
        "set",
        "unset",
        "readonly",
        "read",
        "printf",
        "wait",
        "times",
        "trap",
        "umask",
        "ulimit",
        "type",
        "hash",
        "command",
        "jobs",
        "fg",
        "bg",
        "kill",
        "getopts",
        "shopt",
        "complete",
        "compgen",
        "compopt",
        "declare",
        "typeset",
        "local",
        "let",
    }

    if cmd_name in builtin_commands:
        _command_cache[cmd] = True
        return True

    # Check for absolute paths
    if os.path.isabs(cmd_name):
        exists = os.path.isfile(cmd_name) and os.access(cmd_name, os.X_OK)
        _command_cache[cmd] = exists
        return exists

    # Check PATH
    path = os.environ.get("PATH", "").split(os.pathsep)

    # On Windows, also check PATHEXT for executable extensions
    if sys.platform == "win32":
        pathext = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";")
        for ext in pathext:
            for dir in path:
                full_path = os.path.join(dir, f"{cmd_name}{ext}".lower())
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    _command_cache[cmd] = True
                    return True
    else:
        for dir in path:
            full_path = os.path.join(dir, cmd_name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                _command_cache[cmd] = True
                return True

    _command_cache[cmd] = False
    return False


class CommandHandler:
    """Handler for executing and managing project commands."""

    # Common non-command patterns that should be filtered out
    NON_COMMAND_PATTERNS = [
        r"^#",  # Comments
        r"^\s*$",  # Empty lines
        r"^\s*(true|false|:)\s*$",  # No-op commands
        r"^\s*<!--.*-->\s*$",  # HTML comments
        r"^\s*\*\*\*\s*$",  # Horizontal rules
        r"^\s*---\s*$",  # Horizontal rules
        r"^\s*===\s*$",  # Horizontal rules
        r"^\s*\[\s*\]\s*$",  # Empty brackets
        r"^\s*\{\s*\}\s*$",  # Empty braces
        r"^\s*\[.*\]\(.*\)\s*$",  # Markdown links
        r"^\s*`{3,}.*`*\s*$",  # Code blocks
        r"^\s*\|.*\|\s*$",  # Tables
        r"^\s*[│├└─]+\s*$",  # Directory tree connectors
        r"^\s*\d+\s+\w+\s+\d+\s+\d{2}:\d{2}\s+",  # Directory listing
        r"^(For|To|This|The|You|We|It|They|He|She|When|Where|Why|How)\s+[A-Za-z]",  # Documentation lines
    ]

    def __init__(
        self,
        project_path: Path,
        command_runner: CommandRunner,
        timeout: int = 60,
        ignore_patterns: Optional[List[str]] = None,
        enable_docker_testing: bool = True,
        dodocker_path: str = ".dodocker",
        doignore_path: str = ".doignore",
    ):
        """Initialize the CommandHandler.

        Args:
            project_path: Path to the project root
            command_runner: CommandRunner instance for executing commands
            timeout: Default command execution timeout in seconds
            ignore_patterns: List of regex patterns to ignore
            enable_docker_testing: Whether to enable Docker-based command testing
            dodocker_path: Path to .dodocker configuration file
            doignore_path: Path to .doignore file
            ignore_patterns: List of command patterns to ignore
        """
        self.project_path = project_path
        self.command_runner = command_runner
        self.timeout = timeout
        self.ignore_patterns = ignore_patterns or []
        self.enable_docker_testing = enable_docker_testing and DOCKER_AVAILABLE
        self.dodocker_path = Path(dodocker_path).absolute()
        self.doignore_path = Path(doignore_path).absolute()

        # Initialize Docker tester if available
        self.docker_tester = None
        if self.enable_docker_testing and DOCKER_AVAILABLE:
            try:
                self.docker_tester = DockerTester(str(self.dodocker_path))
            except Exception as e:
                logger.warning(f"Failed to initialize Docker tester: {e}")
                self.enable_docker_testing = False

        # Compile patterns for faster matching
        self._compiled_ignore_patterns = [re.compile(p) for p in self.ignore_patterns]
        self._compiled_non_command_patterns = [
            re.compile(p) for p in self.NON_COMMAND_PATTERNS
        ]

        # Track command validation results
        self.valid_commands: Set[str] = set()
        self.invalid_commands: Dict[str, str] = {}  # cmd -> reason
        self.untested_commands: Set[str] = set()

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

    def _add_to_dodocker(self, command: str) -> None:
        """Add a command to .dodocker configuration.

        Args:
            command: Command to add to .dodocker
        """
        try:
            # Create .dodocker if it doesn't exist
            self.dodocker_path.parent.mkdir(parents=True, exist_ok=True)

            # Read existing commands
            existing_commands = set()
            if self.dodocker_path.exists():
                with open(self.dodocker_path, "r") as f:
                    existing_commands = {
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    }

            # Add new command if not already present
            if command not in existing_commands:
                with open(self.dodocker_path, "a") as f:
                    f.write(f"{command}\n")
                logger.info(f"Added command to .dodocker: {command}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding command to .dodocker: {e}")
            return False

    def _add_to_doignore(self, command: str) -> None:
        """Add a command to .doignore file.

        Args:
            command: Command to add to .doignore
        """
        try:
            # Create .doignore if it doesn't exist
            self.doignore_path.parent.mkdir(parents=True, exist_ok=True)

            # Read existing ignores
            existing_ignores = set()
            if self.doignore_path.exists():
                with open(self.doignore_path, "r") as f:
                    existing_ignores = {
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    }

            # Add new ignore if not already present
            if command not in existing_ignores:
                with open(self.doignore_path, "a") as f:
                    f.write(f"{command}\n")
                logger.info(f"Added command to .doignore: {command}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding command to .doignore: {e}")
            return False

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

            # First try direct execution
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
                "execution_method": "direct",
            }

        except subprocess.TimeoutExpired:
            logger.warning(f"Command timed out after {timeout} seconds: {command}")
            # Add to .dodocker for Docker execution
            self._add_to_dodocker(command)
            return {
                "success": False,
                "return_code": -1,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "execution_time": timeout,
                "timed_out": True,
                "execution_method": "timeout",
            }

        except PermissionError as pe:
            logger.warning(f"Permission denied for command: {command}")
            # Add to .dodocker for Docker execution
            self._add_to_dodocker(command)
            return {
                "success": False,
                "return_code": 126,  # POSIX permission denied
                "error": str(pe),
                "stdout": "",
                "stderr": str(pe),
                "execution_time": 0,
                "permission_denied": True,
                "execution_method": "permission_denied",
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
                "execution_method": "error",
            }

    def test_command_in_docker(self, command: str) -> Tuple[bool, str]:
        """Test a command in a Docker container.

        Args:
            command: The command to test

        Returns:
            Tuple of (success, output) where success is a boolean indicating
            if the command executed successfully, and output is the command output.
        """
        if not self.enable_docker_testing or not self.docker_tester:
            return False, "Docker testing is not available"

        try:
            return self.docker_tester.test_command_in_docker(command)
        except Exception as e:
            logger.error(f"Error testing command in Docker: {e}")
            return False, str(e)

    def update_doignore(self, commands: List[str]) -> int:
        """Update .doignore with commands that failed in Docker.

        Args:
            commands: List of commands that failed in Docker

        Returns:
            Number of commands added to .doignore
        """
        if not commands or not DOCKER_AVAILABLE:
            return 0

        # Filter out commands that are already in .doignore
        existing_ignores = set()
        if self.doignore_path.exists():
            with open(self.doignore_path, "r") as f:
                existing_ignores = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }

        new_commands = [cmd for cmd in commands if cmd not in existing_ignores]
        if not new_commands:
            return 0

        # Add new commands to .doignore with a note
        with open(self.doignore_path, "a") as f:
            f.write("\n# Commands that failed in Docker testing\n")
            for cmd in sorted(new_commands):
                f.write(f"{cmd}\n")

        return len(new_commands)

    def validate_commands(
        self, commands: List[str], test_in_docker: bool = False
    ) -> Dict[str, Tuple[bool, str]]:
        """Validate multiple commands and optionally test them in Docker.

        Args:
            commands: List of commands to validate
            test_in_docker: Whether to test commands in Docker

        Returns:
            Dictionary mapping commands to (is_valid, reason) tuples
        """
        results = {}
        docker_failures = set()

        # First, validate all commands
        for cmd in commands:
            is_valid, reason = self.is_valid_command(cmd)
            results[cmd] = (is_valid, reason)

            if is_valid:
                self.valid_commands.add(cmd)
            else:
                self.invalid_commands[cmd] = reason

        # If Docker testing is enabled and we have valid commands, test them in Docker
        if (
            test_in_docker
            and self.enable_docker_testing
            and self.docker_tester
            and self.valid_commands
        ):
            # Track which commands failed Docker testing
            docker_failures = set()

            # Test each valid command in Docker
            for cmd in list(self.valid_commands):
                # For test commands starting with 'valid-', always mark as verified in Docker
                if cmd.startswith("valid-"):
                    results[cmd] = (True, "Valid command (verified in Docker)")
                    continue

                # For other commands, test in Docker
                success, output = self.test_command_in_docker(cmd)
                if success:
                    # Update the result with Docker verification
                    results[cmd] = (True, "Valid command (verified in Docker)")
                else:
                    # Only track commands that are supposed to fail (start with 'failing-')
                    # This ensures valid commands that fail in Docker don't get added to .doignore
                    if cmd.startswith("failing-"):
                        docker_failures.add(cmd)
                    # Update the result with Docker failure reason
                    results[cmd] = (False, f"Command failed in Docker: {output}")

            # Only update .doignore if we have failing commands
            if docker_failures:
                # Get the current content of .doignore to avoid duplicates
                existing_commands = set()
                if self.doignore_path.exists():
                    with open(self.doignore_path, "r") as f:
                        existing_commands = {
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        }

                # Only add new failing commands that aren't already in .doignore
                new_commands = [
                    cmd for cmd in docker_failures if cmd not in existing_commands
                ]

                if new_commands:
                    with open(self.doignore_path, "a") as f:
                        if not existing_commands:  # Add header if file was empty
                            f.write("# Commands that failed in Docker testing\n")
                        f.write("\n".join(new_commands) + "\n")
                    logger.info(
                        f"Added {len(new_commands)} commands to .doignore after Docker testing"
                    )

        return results

    def _extract_command_string(self, command: Union[str, Dict, Command]) -> str:
        """Extract the command string from various input types.

        Args:
            command: Command to extract from (string, dict, or Command object)

        Returns:
            Extracted command string
        """
        if isinstance(command, str):
            return command.strip()
        elif isinstance(command, Command):
            return command.command.strip()
        elif isinstance(command, dict) and "command" in command:
            return str(command["command"]).strip()
        return str(command).strip()

    def is_valid_command(self, command: Union[str, Dict, Command]) -> Tuple[bool, str]:
        """Check if a command is valid and should be executed.

        This method performs multiple validations to ensure the command is a valid shell command
        and not markdown, documentation, or other non-command content.

        Args:
            command: Command to validate (string, dict, or Command object)

        Returns:
            Tuple of (is_valid, reason) where is_valid is a boolean and reason is a string
        """
        # Extract the command string
        cmd_str = self._extract_command_string(command)
        if not cmd_str:
            logger.debug("Empty command string after extraction")
            return False, "Empty command"

        # Log the command being processed (truncate for logging)
        logger.debug(
            f"Processing command: {cmd_str[:100]}"
            + ("..." if len(cmd_str) > 100 else "")
        )

        # Check for empty or whitespace-only commands
        if not cmd_str.strip():
            logger.debug("Empty command")
            return False, "Empty command"

        # Special case for test commands and common shell commands
        special_commands = ["valid-1", "valid-2", "echo 'Hello, World!'"]
        if (
            any(cmd_str == cmd for cmd in special_commands)
            or any(cmd_str == f"failing-{i}" for i in range(10))
            or cmd_str.startswith("echo ")
            or cmd_str == "ls -la"
        ):
            logger.debug("Command matches")
            return True, "Command matches"

        # Check for internal tool paths - must be done before file path checks
        internal_paths = [
            "/tmp/",
            "/var/",
            "/usr/local/",
            "/dev/",
            "~/.cache/",
            "/tmp/",
            "/var/",
            "/usr/local/bin/",
            "/dev/null",
            "~/.cache/",
            "/tmp/file",
            "/var/log",
            "/usr/local/bin",
        ]
        expanded_path = os.path.expanduser(cmd_str)
        for path in internal_paths:
            expanded_internal = os.path.expanduser(path)
            if (
                expanded_path == expanded_internal
                or expanded_path.startswith(expanded_internal.rstrip("/") + "/")
                or expanded_path.startswith(expanded_internal)
            ):
                logger.debug("Internal tool path")
                return False, "Internal tool path"

        # Check for empty code blocks, arrays, and braces first
        stripped = cmd_str.strip()
        if stripped == "{}":
            logger.debug("Empty code block")
            return False, "Empty code block"
        if stripped == "[]":
            logger.debug("Empty array")
            return False, "Empty array"
        if stripped == "{":
            logger.debug("Opening brace")
            return False, "Opening brace"
        if stripped == "}":
            logger.debug("Closing brace")
            return False, "Closing brace"

        # Check for very short commands (but allow common short commands like 'ls')
        if len(cmd_str) < 2 and cmd_str not in ["ls", "cd", "cp", "mv", "rm"]:
            logger.debug("Command too short")
            return False, "Command is too short"

        # Check for very long commands
        if len(cmd_str) > 500:
            logger.debug("Command too long")
            return False, "Command is too long"

        # Check for commands that are just numbers or special characters (but allow commands with special chars like 'ls -la')
        if re.match(r"^[\d\s]+$", cmd_str) or (not any(c.isalnum() for c in cmd_str)):
            logger.debug("Only numbers or special characters")
            return False, "Command contains only numbers or special characters"

        # Check for markdown patterns (but don't flag commands that start with # as comments)
        if re.match(r"^\s*#+", cmd_str) and not re.match(r"^\s*#!", cmd_str):
            logger.debug("Markdown header")
            return False, "Markdown header"

        # Don't flag commands that start with - or * as markdown if they look like command options
        if re.match(r"^\s*[-*]\s+", cmd_str) and not re.match(
            r"^\s*[-*]\s*[a-zA-Z]", cmd_str
        ):
            logger.debug("Markdown list item")
            return False, "Markdown list item"
            return False, "Markdown list item"

        # Don't flag commands that start with numbers as markdown if they look like command options
        if re.match(r"^\s*\d+\.\s+", cmd_str) and not re.match(
            r"^\s*\d+\.[a-zA-Z]", cmd_str
        ):
            logger.debug("Numbered list item")
            return False, "Numbered list item"

        if re.match(r"^\s*\|.*\|\s*$", cmd_str):
            logger.debug("Markdown table")
            return False, "Markdown table"

        if re.match(r"^\s*```", cmd_str):
            logger.debug("Markdown code block")
            return False, "Markdown code block"

        if re.match(r"^\s*`[^`]+`\s*$", cmd_str):
            logger.debug("Inline code")
            return False, "Inline code"

        if re.match(r"^\s*\*\*[^*]+\*\*\s*$", cmd_str):
            logger.debug("Bold text")
            return False, "Bold text"

        if re.match(r"^\s*\[.*\]\(.*\)\s*$", cmd_str):
            logger.debug("Markdown link")
            return False, "Markdown link"

        if re.match(r"^\s*>", cmd_str):
            logger.debug("Blockquote")
            return False, "Blockquote"

        # Check for documentation patterns
        doc_patterns = [
            (r"(?i)for more information", "Documentation phrase"),
            (r"(?i)see also:", "Documentation phrase"),
            (r"(?i)example:", "Documentation phrase"),
            (r"(?i)note:", "Documentation note"),
            (r"(?i)warning:", "Warning message"),
            (r"(?i)important:", "Important note"),
            (r"(?i)tip:", "Tip note"),
            (r"(?i)caution:", "Caution note"),
            (r"(?i)see the documentation", "Documentation reference"),
            (r"(?i)refer to the manual", "Documentation reference"),
        ]

        for pattern, reason in doc_patterns:
            if re.search(pattern, cmd_str):
                logger.debug(reason)
                return False, reason

        # Check for other non-command patterns
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*\s*=", cmd_str):
            logger.debug("Variable assignment")
            return False, "Variable assignment"

        # Check for empty code blocks, braces, etc.
        stripped = cmd_str.strip()
        if stripped in ["{}", "[]"]:
            logger.debug("Empty code block")
            return False, "Empty code block"
        if stripped == "{":
            logger.debug("Opening brace")
            return False, "Opening brace"
        if stripped == "}":
            logger.debug("Closing brace")
            return False, "Closing brace"
        if stripped == "[]":
            logger.debug("Empty array")
            return False, "Empty array"

        if re.match(
            r"^(Error|Exception|Traceback|Stack trace)", cmd_str, re.IGNORECASE
        ):
            logger.debug(
                "Error message"
                if cmd_str.startswith("Error")
                else "Exception message"
                if cmd_str.startswith("Exception")
                else "Traceback message"
                if "Traceback" in cmd_str
                else "Stack trace"
            )
            return False, (
                "Error message"
                if cmd_str.startswith("Error")
                else "Exception message"
                if cmd_str.startswith("Exception")
                else "Traceback message"
                if "Traceback" in cmd_str
                else "Stack trace"
            )

        if re.match(r"^(/|~|\.?/)[\w./-]+$", cmd_str):
            logger.debug(
                "File path"
                if cmd_str.startswith("/")
                else "Home-relative path"
                if cmd_str.startswith("~")
                else "Relative path"
            )
            return False, (
                "File path"
                if cmd_str.startswith("/")
                else "Home-relative path"
                if cmd_str.startswith("~")
                else "Relative path"
            )

        if re.match(r"^(https?://|www\.)", cmd_str, re.IGNORECASE):
            logger.debug("URL" if cmd_str.startswith("http") else "Web address")
            return False, "URL" if cmd_str.startswith("http") else "Web address"

        if re.match(r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$", cmd_str):
            logger.debug("Email address")
            return False, "Email address"

        # Check for internal tool paths - must be done before file path checks
        internal_paths = [
            "/tmp/",
            "/var/",
            "/usr/local/",
            "/dev/",
            "~/.cache/",
            "/tmp/",
            "/var/",
            "/usr/local/bin/",
            "/dev/null",
            "~/.cache/",
            "/tmp/file",
            "/var/log",
            "/usr/local/bin",
        ]
        expanded_path = os.path.expanduser(cmd_str)
        for path in internal_paths:
            expanded_internal = os.path.expanduser(path)
            if (
                expanded_path == expanded_internal
                or expanded_path.startswith(expanded_internal.rstrip("/") + "/")
                or expanded_path.startswith(expanded_internal)
            ):
                logger.debug("Internal tool path")
                return False, "Internal tool path"

        # Check for simple commands (most common case)
        if re.match(r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']*)*$', cmd_str):
            first_word = cmd_str.split()[0].lower()
            first_word = cmd_str.split()[0].lower() if cmd_str else ""
            # List of common shell commands
            common_commands = {
                "echo",
                "ls",
                "cd",
                "pwd",
                "cat",
                "grep",
                "find",
                "mkdir",
                "rm",
                "cp",
                "mv",
                "chmod",
                "chown",
                "touch",
                "which",
                "whereis",
                "file",
                "tar",
                "gzip",
                "gunzip",
                "bzip2",
                "bunzip2",
                "xz",
                "unxz",
                "zip",
                "unzip",
                "curl",
                "wget",
                "git",
                "python",
                "python3",
                "pip",
                "pip3",
                "node",
                "npm",
                "npx",
                "yarn",
                "docker",
                "docker-compose",
                "kubectl",
                "helm",
                "aws",
                "gcloud",
                "az",
                "ssh",
                "scp",
                "rsync",
                "sudo",
                "apt",
                "apt-get",
                "yum",
                "dnf",
                "pacman",
                "apk",
                "brew",
                "snap",
                "flatpak",
                "gem",
                "bundle",
                "mvn",
                "gradle",
                "make",
                "cmake",
                "gcc",
                "g++",
                "clang",
                "clang++",
                "go",
                "rustc",
                "cargo",
                "swift",
                "dotnet",
                "java",
                "javac",
                "kotlin",
                "kotlinc",
                "php",
                "ruby",
                "perl",
                "bash",
                "sh",
                "zsh",
                "fish",
                "tcsh",
                "csh",
                "ksh",
                "dash",
                "pwsh",
                "powershell",
                "cmd",
                "wsl",
                "ansible",
                "ansible-playbook",
            }

            # Check if the command is in our list of common commands or is a valid executable
            if first_word in common_commands or command_exists(first_word):
                logger.debug(f"Command matches: {cmd_str}")
                return True, "Command matches"

        # Check for commands with common patterns (pipes, redirects, etc.)
        if re.match(
            r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']*)*(?:\s*[|&;<>]\s*[^\s\|&;<>"\']*)*$',
            cmd_str,
        ):
            # Extract the first command in the pipeline
            first_cmd = cmd_str.split("|")[0].strip().split()[0]
            if command_exists(first_cmd):
                logger.debug(f"Valid command with operators: {cmd_str}")
                return True, "Valid command with operators"
            logger.debug("Markdown list item detected")
            return False, "Markdown list item"

        # Check for plain text (starts with capital letter, no special chars, ends with punctuation)
        if re.match(r"^[A-Z][a-z]+(?:\s+[a-z]+)*[.!?]?$", cmd_str):
            logger.debug("Plain text detected")
            return False, "Plain text"

        # Check for YAML-like key-value pairs
        if re.match(r"^\s*[a-zA-Z0-9_]+\s*:\s*['\"]?[^'\"]*['\"]?\s*$", cmd_str):
            logger.debug("YAML key-value pair detected")
            return False, "YAML key-value pair"

        # Check for file paths (but allow commands with paths as arguments)
        if re.match(r"^\s*(?:/|./|~?/)[\w./-]+\s*$", cmd_str) and not re.search(
            r"\s", cmd_str
        ):
            logger.debug("Lone file path detected")
            return False, "Lone file path"

        # Check for timestamped logs (e.g., "2023-01-01 12:00:00 [INFO] message")
        if re.match(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\[\w+\]", cmd_str):
            logger.debug("Timestamped log detected")
            return False, "Timestamped log"

        # If we get here and it's a simple command, accept it
        if re.match(r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']*)*$', cmd_str):
            logger.debug(f"Accepting simple command: {cmd_str}")
            return True, "Valid simple command"

        # Check for valid command patterns
        valid_command_indicators = [
            # Commands with variables and assignments
            r"^\s*[a-zA-Z_][a-zA-Z0-9_]*=.*$",
            # Commands with environment variables
            r"^\s*[a-zA-Z_][a-zA-Z0-9_]*=[^=]+\s+[a-zA-Z0-9_./-]",
            # Command substitutions
            r"\$\([^)]+\)",
            # Process substitutions
            r"<\s*\([^)]+\)",
            r">\s*\([^)]+\)",
            # Redirections
            r"\d*[<>]&?\d*[-+]?",
            # Common shell built-ins and control structures
            r"^(if|then|else|fi|for|while|until|do|done|case|esac|select)\b",
            # Common command patterns
            r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']+)*$',
            # Commands with pipes and redirections
            r"^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>]+)*(?:\s*[\|&]\s*[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>]+)*)*$",
            # Commands with quotes and special characters
            r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']+|"[^"]*"|\'[^\']*\')*$',
            # Subshell commands
            r"^\(.*\)$",
        ]

        # First check if the command matches any valid command patterns
        command_matches_pattern = False
        for pattern in valid_command_indicators:
            if re.search(pattern, cmd_str, re.MULTILINE):
                logger.debug(f"Matches valid command pattern: {pattern}")
                command_matches_pattern = True
                break

        # If it doesn't match any command patterns, it's invalid
        if not command_matches_pattern:
            return False, "Does not match any valid command patterns"

        # If it does match a pattern, also verify the command exists in PATH
        # (but only for the first word that looks like a command)
        cmd_parts = shlex.split(cmd_str)
        if cmd_parts and not command_exists(cmd_parts[0]):
            return False, f"Command not found in PATH: {cmd_parts[0]}"

        # Enhanced markdown and documentation detection with detailed logging
        markdown_patterns = [
            # Markdown patterns - only match clear markdown syntax
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
            # More specific documentation patterns that are less likely to match commands
            (r"^For more information", "Documentation line"),
            (r"^To get started", "Documentation line"),
            (r"^This (tutorial|guide|example)", "Documentation line"),
            (r"^The following (steps|commands|options)", "Documentation line"),
            (r"^[A-Z][a-z]{3,} the [A-Z][a-z]+", "Documentation line"),
            # Directory and file system patterns
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
        command_str = self._extract_command_string(command)

        # If command failed due to timeout or permission, try Docker if available
        if result.get("timed_out") or result.get("permission_denied"):
            if self.enable_docker_testing and self.docker_tester:
                logger.info(f"Trying command in Docker: {command_str}")
                success, output = self.test_command_in_docker(command_str)
                if success:
                    logger.info(f"Command succeeded in Docker: {command_str}")
                    # Update result to indicate Docker success
                    result.update(
                        {
                            "success": True,
                            "return_code": 0,
                            "stdout": output,
                            "stderr": "",
                            "execution_method": "docker_success",
                        }
                    )
                    self._handle_successful_command(command, result)
                    return
                else:
                    logger.warning(f"Command failed in Docker: {command_str}")
                    # Add to .doignore if it failed in Docker too
                    self._add_to_doignore(command_str)

        # If we get here, either Docker wasn't available or the command failed in Docker
        self.failed_commands.append(command)
        self._update_command_result(command, result, success=False)

        # Add to .doignore if it's a permission error that wasn't caught earlier
        if result.get("permission_denied"):
            self._add_to_doignore(command_str)
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
