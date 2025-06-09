"""Command class for representing executable commands."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Command:
    """Represents an executable command with metadata.

    Attributes:
        command: The actual command string to execute.
        type: The type of command (e.g., 'npm_script', 'make_target').
        description: A human-readable description of what the command does.
        source: The source file where this command was defined.
        metadata: Additional metadata about the command.
    """

    command: str
    type: str
    description: str
    source: str
    file: str = ""  # Path to the file where the command was found
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the command to a dictionary.

        Returns:
            A dictionary representation of the command.
        """
        return {
            "command": self.command,
            "type": self.type,
            "description": self.description,
            "source": self.source,
            "file": self.file,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """Create a Command from a dictionary.

        Args:
            data: Dictionary containing command data.

        Returns:
            A new Command instance.
        """
        return cls(
            command=data["command"],
            type=data["type"],
            description=data["description"],
            source=data["source"],
            file=data.get("file", ""),
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """Return a string representation of the command."""
        return f"{self.command} ({self.type}): {self.description}"
