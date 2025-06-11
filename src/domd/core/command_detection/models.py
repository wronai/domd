"""Data models for command detection and execution."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class CommandResult:
    """Result of a command execution."""

    command: str
    return_code: int
    stdout: str = ""
    stderr: str = ""
    success: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time": self.execution_time,
        }


@dataclass
class Command:
    """Represents a command to be executed."""

    command: str
    type: str = ""
    description: str = ""
    source: str = ""
    file: Union[str, Path] = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # These fields are populated during/after execution
    return_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    success: bool = False
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the command to a dictionary."""
        return {
            "command": self.command,
            "type": self.type,
            "description": self.description,
            "source": self.source,
            "file": str(self.file),
            "metadata": self.metadata,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "success": self.success,
            "error": self.error,
            "execution_time": self.execution_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """Create a Command from a dictionary."""
        return cls(**data)


@dataclass
class CommandBatch:
    """A batch of commands to be executed."""

    commands: List[Command] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_command(self, command: Command) -> None:
        """Add a command to the batch."""
        self.commands.append(command)

    def extend(self, commands: List[Command]) -> None:
        """Extend the batch with multiple commands."""
        self.commands.extend(commands)

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert the batch to a list of command dictionaries."""
        return [cmd.to_dict() for cmd in self.commands]

    def __len__(self) -> int:
        """Return the number of commands in the batch."""
        return len(self.commands)
