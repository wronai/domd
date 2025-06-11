"""Handles recording commands to .dodocker file."""

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30  # Default timeout in seconds


class CommandRecorder:
    """Handles recording commands to .dodocker file."""

    def __init__(self, config_path: str = ".dodocker"):
        """Initialize the CommandRecorder.

        Args:
            config_path: Path to the .dodocker file
        """
        self.config_path = Path(config_path)

    def record_command(
        self,
        command: str,
        reason: str,
        timeout: int = DEFAULT_TIMEOUT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record a command to the .dodocker file.

        Args:
            command: The command to record
            reason: Why this command is being recorded
            timeout: The timeout that was set for this command
            metadata: Additional metadata about the command

        Returns:
            bool: True if recording was successful, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare the content to write
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            lines = [
                "#" + "=" * 79,
                f"# Command recorded at {timestamp}",
                f"# Reason: {reason}",
                f"# Timeout: {timeout} seconds",
            ]

            # Add metadata if provided
            if metadata:
                lines.append("# Metadata:")
                for key, value in metadata.items():
                    lines.append(f"#   {key}: {value}")

            # Add the command
            lines.append(command)
            lines.append("\n")  # Add a blank line for separation

            # Write to file
            with open(self.config_path, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            logger.info("Command recorded to %s: %s", self.config_path, command)
            return True

        except Exception as e:
            logger.error("Failed to record command to %s: %s", self.config_path, e)
            return False

    def should_record_command(
        self,
        execution_time: float,
        timeout: int = DEFAULT_TIMEOUT,
        min_time_ratio: float = 0.8,
    ) -> bool:
        """Determine if a command should be recorded based on its execution time.

        Args:
            execution_time: How long the command took to execute (seconds)
            timeout: The timeout that was set for the command
            min_time_ratio: Minimum ratio of execution_time/timeout to trigger recording

        Returns:
            bool: True if the command should be recorded
        """
        if timeout <= 0:
            return False

        time_ratio = execution_time / timeout
        return time_ratio >= min_time_ratio
