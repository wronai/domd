"""
Prezenter komend dla interfejsu wiersza poleceń.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.ports.command_repository import CommandRepository

logger = logging.getLogger(__name__)


class CommandPresenter:
    """
    Prezenter komend dla interfejsu wiersza poleceń.

    Odpowiada za formatowanie i wyświetlanie informacji o komendach
    w interfejsie wiersza poleceń.
    """

    def __init__(self, repository: CommandRepository):
        """
        Inicjalizuje prezenter komend.

        Args:
            repository: Repozytorium komend
        """
        self.repository = repository

    def print_summary(
        self,
        todo_file: Optional[str] = None,
        done_file: Optional[str] = None,
        script_file: Optional[str] = None,
        ignore_file: Optional[str] = None,
    ) -> None:
        """
        Wyświetla podsumowanie wykonania komend.

        Args:
            todo_file: Ścieżka do pliku z nieudanymi komendami
            done_file: Ścieżka do pliku z udanymi komendami
            script_file: Ścieżka do pliku skryptu
            ignore_file: Ścieżka do pliku z wzorcami ignorowania
        """
        successful = len(self.repository.get_successful_commands())
        failed = len(self.repository.get_failed_commands())
        ignored = len(self.repository.get_ignored_commands())
        total_tested = successful + failed
        total_commands = total_tested + ignored

        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print("📊 Results:")
        print(f"   Total commands found: {total_commands}")
        print(f"   Commands tested:  {total_tested}")
        print(f"   Commands ignored:  {ignored} (via .domdignore)")
        print(f"   ✅ Successful:  {successful}")
        print(f"   ❌ Failed:  {failed}")

        if todo_file or done_file or script_file or ignore_file:
            print("📝 Files:")
            if todo_file:
                print(f"   📋 TODO file: {todo_file}")
            if script_file:
                print(f"   🔧 Script file: {script_file}")
            if ignore_file:
                print(f"   🚫 Ignore file: {ignore_file}")
            print()

        if failed == 0 and total_tested > 0:
            print("🎉 All testable commands executed successfully!")
        elif failed > 0:
            print(f"❌ {failed} commands failed. Check the TODO file for details.")
        elif total_tested == 0:
            print("⚠️ No commands were tested.")

    def print_dry_run(self, show_ignored: bool = False) -> None:
        """
        Wyświetla informacje o komendach w trybie dry-run.

        Args:
            show_ignored: Czy wyświetlać zignorowane komendy
        """
        commands = self.repository.get_all_commands()
        ignored_commands = self.repository.get_ignored_commands()

        # Filtruj komendy, jeśli nie pokazujemy zignorowanych
        if not show_ignored:
            commands = [cmd for cmd in commands if cmd not in ignored_commands]

        if not commands:
            print("\n🔍 DRY RUN MODE - No commands found")
            return

        print("\n🔍 DRY RUN MODE - Filtered commands:")
        for i, cmd in enumerate(commands, 1):
            print(f"{i:3d}. {cmd.description}")
            print(f"     Command:  {cmd.command}")
            print(f"     Source:   {cmd.source}")
            print()

        if ignored_commands and not show_ignored:
            print(f"🚫 Would ignore {len(ignored_commands)} commands via .domdignore")

    def print_init_only(
        self, todo_file: str, script_file: str, ignore_file: str
    ) -> None:
        """
        Wyświetla informacje w trybie init-only.

        Args:
            todo_file: Ścieżka do pliku z nieudanymi komendami
            script_file: Ścieżka do pliku skryptu
            ignore_file: Ścieżka do pliku z wzorcami ignorowania
        """
        commands = self.repository.get_all_commands()
        ignored_commands = self.repository.get_ignored_commands()

        print("\n✅ Initialization complete!")
        print(f"📋 Created {todo_file} with {len(commands)} testable commands")
        print(f"🔧 Created executable {script_file}")

        if ignored_commands:
            print(f"🚫 Ignored {len(ignored_commands)} commands via .domdignore")

        print("\n💡 Next steps:")
        print(f"   • Review and edit {ignore_file} to adjust ignored commands")
        print(f"   • Run: ./{script_file} to execute commands manually")
        print("   • Or run: domd to test with TodoMD")
        print("   • Use: domd --show-ignored to see ignored commands")
