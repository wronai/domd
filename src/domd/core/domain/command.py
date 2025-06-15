"""
Modele domenowe dla komend w aplikacji DoMD.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CommandResult:
    """
    Wynik wykonania komendy.

    Attributes:
        success: Czy komenda została wykonana pomyślnie
        return_code: Kod powrotu komendy
        execution_time: Czas wykonania komendy w sekundach
        stdout: Standardowe wyjście komendy
        stderr: Standardowe wyjście błędów komendy
        error: Komunikat błędu, jeśli wystąpił
    """

    success: bool = False
    return_code: int = -1
    execution_time: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None


@dataclass
class Command:
    """
    Reprezentacja komendy w projekcie.

    Attributes:
        command: Treść komendy do wykonania
        type: Typ komendy (np. 'make', 'npm', 'pip')
        description: Opis komendy
        source: Źródło komendy (np. ścieżka do pliku)
        metadata: Dodatkowe metadane komendy
        result: Wynik wykonania komendy
    """

    command: str
    type: str
    description: str
    source: str
    file: str = ""  # Path to the file where the command was found
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[CommandResult] = None

    @property
    def is_executed(self) -> bool:
        """Sprawdza, czy komenda została wykonana."""
        return self.result is not None

    @property
    def is_successful(self) -> bool:
        """Sprawdza, czy komenda została wykonana pomyślnie."""
        return self.is_executed and self.result.success

    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje obiekt Command na słownik.

        Returns:
            Dict[str, Any]: Słownik reprezentujący komendę
        """
        result = {
            "command": self.command,
            "type": self.type,
            "description": self.description,
            "source": self.source,
            "file": self.file,
            "metadata": self.metadata.copy() if self.metadata else {},
        }

        # Dodaj informacje o wyniku wykonania, jeśli dostępne
        if self.result:
            result.update(
                {
                    "success": self.result.success,
                    "return_code": self.result.return_code,
                    "execution_time": self.result.execution_time,
                    "stdout": self.result.stdout,
                    "stderr": self.result.stderr,
                    "error": self.result.error,
                }
            )

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """
        Tworzy obiekt Command z słownika.

        Args:
            data: Słownik z danymi komendy

        Returns:
            Command: Nowy obiekt Command
        """
        # Wyodrębnij podstawowe pola
        command = data.get("command", "")
        type_ = data.get("type", "")
        description = data.get("description", "")
        source = data.get("source", "")
        metadata = data.get("metadata", {})

        # Utwórz obiekt Command
        cmd = cls(
            command=command,
            type=type_,
            description=description,
            source=source,
            metadata=metadata,
        )

        # Jeśli są dostępne informacje o wyniku wykonania, dodaj je
        if any(key in data for key in ["success", "return_code", "execution_time"]):
            cmd.result = CommandResult(
                success=data.get("success", False),
                return_code=data.get("return_code", -1),
                execution_time=data.get("execution_time", 0.0),
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                error=data.get("error"),
            )

        return cmd
