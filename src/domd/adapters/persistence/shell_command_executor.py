"""
Implementacja wykonawcy komend powłoki systemowej.
"""

# Standard library imports
import logging
import os
import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Local application imports
from ...core.domain.command import Command, CommandResult
from ...core.ports.command_executor import CommandExecutor

# List of common shell built-in commands
SHELL_BUILTINS = {
    "source",
    ".",
    "cd",
    "alias",
    "bg",
    "bind",
    "break",
    "builtin",
    "caller",
    "command",
    "compgen",
    "complete",
    "compopt",
    "continue",
    "declare",
    "dirs",
    "disown",
    "echo",
    "enable",
    "eval",
    "exec",
    "exit",
    "export",
    "false",
    "fc",
    "fg",
    "getopts",
    "hash",
    "help",
    "history",
    "jobs",
    "kill",
    "let",
    "local",
    "logout",
    "mapfile",
    "popd",
    "printf",
    "pushd",
    "pwd",
    "read",
    "readarray",
    "readonly",
    "return",
    "set",
    "shift",
    "shopt",
    "suspend",
    "test",
    "times",
    "trap",
    "true",
    "type",
    "typeset",
    "ulimit",
    "umask",
    "unalias",
    "unset",
    "wait",
}

logger = logging.getLogger(__name__)


class ShellCommandExecutor(CommandExecutor):
    """
    Implementacja wykonawcy komend powłoki systemowej.
    """

    def __init__(self, max_retries: int = 1):
        """
        Inicjalizuje wykonawcę komend powłoki systemowej.

        Args:
            max_retries: Maksymalna liczba prób wykonania komendy
        """
        self.max_retries = max_retries

    def execute(self, command: Command, timeout: Optional[int] = None) -> CommandResult:
        """
        Wykonuje komendę i zwraca wynik jej wykonania.

        Args:
            command: Komenda do wykonania
            timeout: Limit czasu wykonania w sekundach

        Returns:
            Wynik wykonania komendy
        """
        # Domyślnie wykonaj komendę w bieżącym katalogu
        return self.execute_in_directory(command, Path.cwd(), timeout)

    def execute_in_directory(
        self,
        command: Command,
        directory: Path,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Wykonuje komendę w określonym katalogu i zwraca wynik jej wykonania.

        Args:
            command: Komenda do wykonania
            directory: Katalog, w którym ma być wykonana komenda
            timeout: Limit czasu wykonania w sekundach
            env: Dodatkowe zmienne środowiskowe

        Returns:
            Wynik wykonania komendy
        """
        cmd_str = command.command.strip()
        if not cmd_str:
            return CommandResult(
                success=False,
                return_code=1,
                execution_time=0,
                stdout="",
                stderr="Error: Empty command",
            )

        cmd_args, needs_shell = self._parse_command(cmd_str)

        # Prepare execution environment
        execution_env = None
        if env:
            execution_env = dict(os.environ)
            execution_env.update(env)

        # Execute command with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()

                # Special handling for 'cd' command
                if cmd_str.strip().startswith("cd"):
                    try:
                        # Get the target directory (everything after 'cd ')
                        target_dir = cmd_str[2:].strip()

                        # If no directory specified, use home directory
                        if not target_dir:
                            new_dir = str(Path.home())
                        else:
                            # Resolve the path relative to current directory
                            new_dir = str((directory / target_dir).resolve())

                        # Validate the directory exists
                        Path(new_dir).resolve(strict=True)

                        # Return success with the directory path in stdout
                        return CommandResult(
                            success=True,
                            return_code=0,
                            execution_time=time.time() - start_time,
                            stdout=f"Changed directory to {new_dir}",
                            stderr="",
                        )
                    except Exception as e:
                        return CommandResult(
                            success=False,
                            return_code=1,
                            execution_time=time.time() - start_time,
                            stdout="",
                            stderr=f"cd: {str(e)}",
                        )

                # Execute the command
                process = subprocess.run(
                    cmd_args,
                    cwd=str(directory),
                    shell=needs_shell,
                    capture_output=True,
                    text=True,
                    env=execution_env,
                    timeout=timeout,
                    executable="/bin/bash" if needs_shell else None,
                )

                execution_time = time.time() - start_time

                # Przygotuj wynik
                result = CommandResult(
                    success=(process.returncode == 0),
                    return_code=process.returncode,
                    execution_time=execution_time,
                    stdout=process.stdout,
                    stderr=process.stderr,
                )

                if result.success:
                    return result

                # Jeśli nie udało się wykonać komendy, spróbuj ponownie
                if attempt < self.max_retries:
                    logger.warning(
                        f"Command failed (attempt {attempt}/{self.max_retries}): {cmd_str}"
                    )
                    continue

                # Jeśli wszystkie próby się nie powiodły, zwróć ostatni wynik
                logger.error(f"Command failed after {attempt} attempts")
                return result

            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out after {timeout} seconds: {cmd_str}")
                return CommandResult(
                    success=False,
                    return_code=-1,
                    execution_time=timeout or 0,
                    error=f"Command timed out after {timeout} seconds",
                )

            except Exception as e:
                logger.error(f"Error executing command: {str(e)}", exc_info=True)
                return CommandResult(success=False, return_code=-1, error=str(e))

        # Ten kod nie powinien być nigdy osiągnięty
        return CommandResult(
            success=False, return_code=-1, error="Unexpected error in command execution"
        )

    def _needs_shell(self, command_str: str) -> bool:
        """
        Check if a command needs to be run in a shell.

        Args:
            command_str: The command string to check

        Returns:
            bool: True if the command should be run in a shell
        """
        # Check for shell built-ins
        first_word = command_str.strip().split(maxsplit=1)[0].lower()
        if first_word in SHELL_BUILTINS:
            return True

        # Check for shell operators
        shell_operators = {
            "|",
            ">",
            ">>",
            "<",
            "<<",
            "&&",
            "||",
            ";",
            "&",
            "`",
            "$",
            "(",
            ")",
        }
        if any(op in command_str for op in shell_operators):
            return True

        # Check for environment variable assignments
        if "=" in first_word and " " not in first_word.split("=")[0]:
            return True

        return False

    def _is_markdown_content(self, command_str: str) -> bool:
        """
        Check if the given string appears to be markdown or other non-command content.

        Args:
            command_str: The string to check

        Returns:
            bool: True if the string appears to be non-command content
        """
        # Skip empty strings
        if not command_str or not command_str.strip():
            return True

        # Common markdown patterns that shouldn't be executed as commands
        markdown_patterns = [
            # Headers
            (r"^#+\s+", "Markdown header"),
            # Lists
            (r"^[-*+]\s+", "Markdown list item"),
            (r"^\d+\.\s+", "Numbered list item"),
            # Code blocks
            (r"^```", "Markdown code block"),
            (r"`[^`]+`", "Inline code"),
            # Tables
            (r"^\|.*\|$", "Markdown table"),
            # Links and images
            (r"\[.*\]\(.*\)", "Markdown link"),
            (r"!\[.*\]\(.*\)", "Markdown image"),
            # Text formatting
            (r"\*\*[^*]+\*\*", "Bold text"),
            (r"__[^_]+__", "Underlined text"),
            (r"~~[^~]+~~", "Strikethrough"),
            (r"\*[^*]+\*", "Italic text"),
            (r"_[^_]+_", "Italic text (underscore)"),
            # Blockquotes
            (r"^>\s+", "Blockquote"),
            # Horizontal rules
            (r"^\s*[*_-]{3,}\s*$", "Horizontal rule"),
            # HTML tags
            (r"<[a-z][\s\S]*?>", "HTML tag"),
            # Common documentation patterns
            (r"^\s*[A-Z][A-Za-z0-9_\s-]+:", "Documentation line"),
            (r"^\s*<!--.*-->\s*$", "HTML comment"),
            (r"^\s*//", "Single-line comment"),
            (r"^\s*#", "Comment"),
            (r"^\s*/\*[\s\S]*?\*/\s*$", "Multi-line comment"),
            # Common metadata patterns
            (r"^\s*[\w-]+\s*:\s*.+", "YAML/JSON key-value pair"),
            # Directory listing patterns
            (r"^[│└├─]", "Tree-like directory structure"),
            (r"\s+\d+\s+\w+\s+\d+\s+[\d:]+\s+", "File size and date"),
            (r"\d+\s+[BKMGTPEZY]B\s*$", "File size"),
            (r"^total \d+$", "Directory total"),
            # Common documentation sections
            (
                r"^\s*(Installation|Usage|Configuration|Options|Examples):",
                "Documentation section",
            ),
            # Empty or whitespace-only lines
            (r"^\s*$", "Empty line"),
        ]

        # Check for markdown and other non-command patterns
        for pattern, description in markdown_patterns:
            if re.search(pattern, command_str, re.MULTILINE):
                logger.debug(f"Detected {description}: {command_str[:100]}")
                return True

        # Check for suspiciously long lines that aren't commands
        if len(command_str) > 1000 and not any(
            c in command_str for c in ["&&", "|", ">", "<", ";"]
        ):
            logger.debug(f"Suspiciously long line detected: {command_str[:100]}...")
            return True

        # Check for lines that are just special characters or numbers
        if re.match(r"^[\d\s\W]+$", command_str):
            logger.debug(
                f"Line contains only numbers/special chars: {command_str[:100]}"
            )
            return True

        # Check for common error messages or stack traces
        error_indicators = [
            "error:",
            "warning:",
            "exception:",
            "traceback",
            "stacktrace",
            'at ',
            'File "',
            r"line \d+",  # Raw string for regex
            "in <module>",
            "^",
            "~",
            "SyntaxError",
            "NameError",
            "TypeError",
            "ValueError",
            "ImportError",
        ]

        if any(
            indicator.lower() in command_str.lower() for indicator in error_indicators
        ):
            logger.debug(f"Error/warning message detected: {command_str[:100]}...")
            return True

        return False

    def _parse_command(self, command_str: str) -> Tuple[List[str], bool]:
        """
        Parses a command string into a list of arguments and determines if it needs a shell.

        Args:
            command_str: The command string to parse

        Returns:
            Tuple of (command_args, needs_shell)
        """
        if not command_str.strip():
            return [], False

        # Check if this is markdown content that shouldn't be executed
        if self._is_markdown_content(command_str):
            logger.debug(f"Ignoring markdown content: {command_str[:100]}...")
            return [], False

        # Check if this is a shell built-in or needs shell features
        needs_shell = self._needs_shell(command_str)

        # Special handling for 'source' command
        if command_str.strip().startswith("source ") or command_str.strip().startswith(
            ". "
        ):
            # For 'source' command, we need to use the shell to execute it
            return [command_str], True

        if needs_shell:
            # For other shell commands, return the full command as a single string
            return [command_str], True

        # For non-shell commands, use shlex for proper argument splitting
        try:
            return shlex.split(command_str), False
        except Exception as e:
            logger.warning(
                f"Error parsing command with shlex, falling back to simple split: {e}"
            )
            return command_str.split(), False
