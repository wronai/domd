"""
Implementacja wykonawcy komend powłoki systemowej.
"""

import logging
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# List of common shell built-in commands
SHELL_BUILTINS = {
    'source', '.', 'cd', 'alias', 'bg', 'bind', 'break', 'builtin', 'caller',
    'command', 'compgen', 'complete', 'compopt', 'continue', 'declare', 'dirs',
    'disown', 'echo', 'enable', 'eval', 'exec', 'exit', 'export', 'false',
    'fc', 'fg', 'getopts', 'hash', 'help', 'history', 'jobs', 'kill', 'let',
    'local', 'logout', 'mapfile', 'popd', 'printf', 'pushd', 'pwd', 'read',
    'readarray', 'readonly', 'return', 'set', 'shift', 'shopt', 'suspend',
    'test', 'times', 'trap', 'true', 'type', 'typeset', 'ulimit', 'umask',
    'unalias', 'unset', 'wait'
}

from ...core.domain.command import Command, CommandResult
from ...core.ports.command_executor import CommandExecutor

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
                stderr="Error: Empty command"
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
                if cmd_str.startswith('cd '):
                    try:
                        new_dir = cmd_str[3:].strip()
                        if not new_dir:
                            new_dir = str(Path.home())
                        new_dir = str(Path(directory) / new_dir)
                        Path(new_dir).resolve(strict=True)  # Validate path exists
                        return CommandResult(
                            success=True,
                            return_code=0,
                            execution_time=0,
                            stdout=f"Changed directory to {new_dir}",
                            stderr=""
                        )
                    except Exception as e:
                        return CommandResult(
                            success=False,
                            return_code=1,
                            execution_time=0,
                            stdout="",
                            stderr=f"cd: {str(e)}"
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
        shell_operators = {'|', '>', '>>', '<', '<<', '&&', '||', ';', '&', '`', '$', '(', ')'}
        if any(op in command_str for op in shell_operators):
            return True
            
        # Check for environment variable assignments
        if '=' in first_word and ' ' not in first_word.split('=')[0]:
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
        needs_shell = self._needs_shell(command_str)
        
        if needs_shell:
            # For shell commands, return the full command as a single string
            return [command_str], True
            
        # For non-shell commands, use shlex for proper argument splitting
        try:
            return shlex.split(command_str), False
        except Exception as e:
            logger.warning(f"Error parsing command with shlex, falling back to simple split: {e}")
            return command_str.split(), False
