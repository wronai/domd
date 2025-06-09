"""Base reporter interface for domd."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Union


class BaseReporter(ABC):
    """Base class for all reporters."""

    def __init__(self, output_file: Optional[Union[str, Path]] = None):
        """Initialize the reporter.

        Args:
            output_file: Path to the output file (optional)
        """
        self.output_file = Path(output_file) if output_file else None

    @abstractmethod
    def generate_report(self, data: Dict) -> str:
        """Generate the report content.

        Args:
            data: Data to include in the report

        Returns:
            The generated report as a string
        """
        pass

    def write_report(
        self, data: Dict, output_file: Optional[Union[str, Path]] = None
    ) -> Path:
        """Generate and write the report to a file.

        Args:
            data: Data to include in the report
            output_file: Optional output file path (overrides instance path)

        Returns:
            Path to the generated report file
        """
        output_file = Path(output_file) if output_file else self.output_file
        if not output_file:
            raise ValueError("No output file specified")

        content = self.generate_report(data)
        output_file.write_text(content, encoding="utf-8")
        return output_file
