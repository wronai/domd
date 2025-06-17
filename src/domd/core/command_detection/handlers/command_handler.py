"""Handler for executing and managing project commands with Docker testing support."""

import logging
import re
import time
import shlex
import shutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Pattern

from domd.core.command_execution.command_runner import CommandRunner
from domd.core.domain.command import Command

# Import DockerTester if available
try:
    from domd.core.command_detection.docker_tester import DockerTester, test_commands_in_docker
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
        'cd', 'export', 'source', 'alias', 'unalias', 'echo', 'pwd', 'exit',
        'return', 'shift', 'test', 'true', 'false', ':', '.', 'exec', 'eval',
        'set', 'unset', 'readonly', 'read', 'printf', 'wait', 'times', 'trap',
        'umask', 'ulimit', 'type', 'hash', 'command', 'jobs', 'fg', 'bg', 'kill',
        'getopts', 'shopt', 'complete', 'compgen', 'compopt', 'declare',
        'typeset', 'local', 'let', 'readonly', 'unset', 'export', 'alias',
        'unalias', 'echo', 'pwd', 'exit', 'return', 'shift', 'test', 'true',
        'false', ':', '.', 'exec', 'eval', 'set', 'unset', 'readonly', 'read',
        'printf', 'wait', 'times', 'trap', 'umask', 'ulimit', 'type', 'hash',
        'command', 'jobs', 'fg', 'bg', 'kill', 'getopts', 'shopt', 'complete',
        'compgen', 'compopt', 'declare', 'typeset', 'local', 'let'
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
    path = os.environ.get('PATH', '').split(os.pathsep)
    
    # On Windows, also check PATHEXT for executable extensions
    if sys.platform == 'win32':
        pathext = os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD').split(';')
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
        doignore_path: str = ".doignore"
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
        self._compiled_non_command_patterns = [re.compile(p) for p in self.NON_COMMAND_PATTERNS]
        
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
            with open(self.doignore_path, 'r') as f:
                existing_ignores = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        
        new_commands = [cmd for cmd in commands if cmd not in existing_ignores]
        if not new_commands:
            return 0
            
        # Add new commands to .doignore with a note
        with open(self.doignore_path, 'a') as f:
            f.write('\n# Commands that failed in Docker testing\n')
            for cmd in sorted(new_commands):
                f.write(f'{cmd}\n')
        
        return len(new_commands)
    
    def validate_commands(self, commands: List[str], test_in_docker: bool = False) -> Dict[str, Tuple[bool, str]]:
        """Validate multiple commands and optionally test them in Docker.
        
        Args:
            commands: List of commands to validate
            test_in_docker: Whether to test commands in Docker
            
        Returns:
            Dictionary mapping commands to (is_valid, reason) tuples
        """
        results = {}
        
        for cmd in commands:
            # First check if it's a valid command
            is_valid, reason = self.is_valid_command(cmd)
            results[cmd] = (is_valid, reason)
            
            # Track validation results
            if is_valid:
                self.valid_commands.add(cmd)
                if test_in_docker and self.enable_docker_testing:
                    self.untested_commands.add(cmd)
            else:
                self.invalid_commands[cmd] = reason
        
        # If more than half of commands are invalid and Docker testing is enabled,
        # test the invalid commands in Docker before adding them to .doignore
        if (len(self.invalid_commands) > len(commands) / 2 and 
            self.enable_docker_testing and 
            test_in_docker):
            
            # Test invalid commands in Docker
            docker_results = test_commands_in_docker(
                list(self.invalid_commands.keys()),
                str(self.dodocker_path)
            )
            
            # Update .doignore with commands that failed in Docker
            failed_in_docker = [
                cmd for cmd, (success, _) in docker_results.items() 
                if not success and cmd in self.invalid_commands
            ]
            
            if failed_in_docker:
                count = self.update_doignore(failed_in_docker)
                logger.info(f"Added {count} commands to .doignore after Docker testing")
        
        return results
    
    def is_valid_command(self, command: Union[str, Dict, Command]) -> Tuple[bool, str]:
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

        # Check for markdown task items (e.g., "- [ ] Task")
        if re.match(r"^\s*-\s*\[\s*[xX\s]?\s*\]", cmd_str):
            logger.debug("Markdown task item detected")
            return False, "Markdown task item"

        # Check for plain text (starts with capital letter, no special chars)
        if re.match(r"^[A-Z][a-z]+(?:\s+[a-z]+)*[.!?]?$", cmd_str):
            logger.debug("Plain text detected")
            return False, "Plain text"

        # Check for file paths
        if re.match(r"^(?:/|./|~?/)[\w./-]+$", cmd_str):
            logger.debug("File path detected")
            return False, "File path"

        # Check for timestamped logs (e.g., "2023-01-01 12:00:00 [INFO] message")
        if re.match(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\[\w+\]", cmd_str):
            logger.debug("Timestamped log detected")
            return False, "Timestamped log"

        # Check for valid command patterns
        valid_command_indicators = [
            # Basic commands and paths with complex shell features
            r'^[a-zA-Z0-9_./-]+(?:\s+[^\s\|&;<>"\']+|\s*[&|;]\s*|\s*\(\s*|\s*\)\s*|\s*\{\s*|\s*\}\s*|\s*"[^"]*"|\s*\'[^\']*\')*$',
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
            # Documentation patterns - be more specific to avoid false positives
            (r"^For\s+\w+\s+information", "Documentation line"),
            (r"^To\s+\w+", "Documentation line"),
            (r"^This\s+\w+", "Documentation line"),
            (r"^The\s+\w+", "Documentation line"),
            (r"^[A-Z][a-z]+\s+the\s+\w+", "Documentation line"),
            # More specific documentation patterns that won't match shell commands
            (r"^[A-Z][a-z]{3,}\s+[A-Z][a-z]{3,}", "Documentation line"),  # At least 4 letters each word
            (r"^[A-Z][a-z]+\s+[a-z]{3,}\s+[a-z]{3,}", "Documentation line"),  # At least 4 letters each word
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
