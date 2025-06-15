"""Report generation and management for command execution results."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from .formatters import (
    BaseFormatter,
    ConsoleFormatter,
    JsonFormatter,
    MarkdownFormatter,
)

logger = logging.getLogger(__name__)


class Reporter:
    """Handles generation and management of execution reports."""

    # Default formatters
    DEFAULT_FORMATTERS = {
        "console": ConsoleFormatter,
        "markdown": MarkdownFormatter,
        "md": MarkdownFormatter,
        "json": JsonFormatter,
    }

    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        formatters: Optional[Dict[str, Type[BaseFormatter]]] = None,
        default_format: str = "console",
        project_root: Optional[Union[str, Path]] = None,
        **formatter_kwargs: Any,
    ):
        """Initialize the reporter.

        Args:
            output_dir: Base directory for report output
            formatters: Additional formatters to register
            default_format: Default format to use
            project_root: Root directory of the project (for relative paths)
            **formatter_kwargs: Default arguments for formatters
        """
        self.output_dir = Path(output_dir).resolve() if output_dir else None
        self.default_format = default_format
        self.project_root = Path(project_root).resolve() if project_root else None

        # Set default formatter kwargs
        self.formatter_kwargs = formatter_kwargs.copy()
        if self.project_root and "base_path" not in self.formatter_kwargs:
            self.formatter_kwargs["base_path"] = self.project_root

        # Register formatters
        self._formatters = dict(self.DEFAULT_FORMATTERS)
        if formatters:
            self._formatters.update(formatters)

        # Initialize formatter instances
        self._formatter_instances: Dict[str, BaseFormatter] = {}

        # Pattern matcher for output paths
        self.matcher = PatternMatcher()

        # Report data
        self.reset()

    def reset(self) -> None:
        """Reset the reporter state."""
        self.data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "commands": [],
            "successful_commands": [],
            "failed_commands": [],
            "ignored_commands": [],
            "execution_time": 0.0,
            "summary": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "ignored": 0,
            },
        }

    def add_command(
        self,
        command: str,
        return_code: int,
        execution_time: float,
        source: Optional[str] = None,
        output: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ignore: bool = False,
        ignore_reason: Optional[str] = None,
    ) -> None:
        """Add a command execution result to the report.

        Args:
            command: The command that was executed
            return_code: Command return code
            execution_time: Command execution time in seconds
            source: Source of the command (e.g., file path)
            output: Command output (stdout)
            error: Command error output (stderr)
            metadata: Additional metadata about the command
            ignore: Whether to ignore this command in the report
            ignore_reason: Reason for ignoring the command
        """
        command_data = {
            "command": command,
            "return_code": return_code,
            "execution_time": execution_time,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        if output is not None:
            command_data["output"] = output
        if error is not None:
            command_data["error"] = error

        self.data["commands"].append(command_data)

        if ignore:
            command_data["ignored"] = True
            command_data["ignore_reason"] = ignore_reason or "Not specified"
            self.data["ignored_commands"].append(command_data)
        elif return_code == 0:
            self.data["successful_commands"].append(command_data)
        else:
            self.data["failed_commands"].append(command_data)

        # Update summary
        self.data["summary"] = {
            "total": len(self.data["commands"]),
            "successful": len(self.data["successful_commands"]),
            "failed": len(self.data["failed_commands"]),
            "ignored": len(self.data["ignored_commands"]),
        }

        # Update total execution time
        self.data["execution_time"] = sum(
            cmd.get("execution_time", 0) for cmd in self.data["commands"]
        )

    def get_formatter(self, format_name: Optional[str] = None) -> BaseFormatter:
        """Get a formatter instance.

        Args:
            format_name: Format name (default: self.default_format)

        Returns:
            Formatter instance

        Raises:
            ValueError: If the format is not supported
        """
        format_name = format_name or self.default_format

        if format_name not in self._formatters:
            raise ValueError(f"Unsupported format: {format_name}")

        if format_name not in self._formatter_instances:
            self._formatter_instances[format_name] = self._formatters[format_name](
                **self.formatter_kwargs
            )

        return self._formatter_instances[format_name]

    def format_report(self, format_name: Optional[str] = None, **kwargs: Any) -> str:
        """Format the report.

        Args:
            format_name: Format name (default: self.default_format)
            **kwargs: Additional formatting options

        Returns:
            Formatted report as a string
        """
        formatter = self.get_formatter(format_name)
        return formatter.format_report(self.data, **kwargs)

    def generate_report(
        self,
        output_path: Optional[Union[str, Path]] = None,
        format: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a report in the specified format.

        Args:
            output_path: Path to write the report to. If None, returns the report as a string.
            format: Output format (e.g., 'markdown', 'json'). Uses default if not specified.
            **kwargs: Additional arguments to pass to the formatter.

        Returns:
            The generated report as a string if output_path is None, otherwise an empty string.
        """
        format = format or self.default_format
        formatter = self._get_formatter(format)

        # Ensure base_path is set for path handling
        format_kwargs = self.formatter_kwargs.copy()
        if "base_path" not in format_kwargs and self.project_root:
            format_kwargs["base_path"] = self.project_root

        # Merge with any provided kwargs (allowing override of base_path)
        format_kwargs.update(kwargs)

        if output_path is not None:
            formatter.write_report(self.data, output_path, **format_kwargs)
            return ""
        return formatter.format_report(self.data, **format_kwargs)

    def write_report(
        self,
        output_path: Optional[Union[str, Path]] = None,
        format_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Path:
        """Write the report to a file.

        Args:
            output_path: Output path (default: auto-generated in output_dir)
            format_name: Format name (default: determined from output_path or self.default_format)
            **kwargs: Additional formatting options

        Returns:
            Path to the generated report

        Raises:
            ValueError: If output_path is not specified and output_dir is not set
        """
        # Determine format
        if format_name is None and output_path:
            format_name = self._get_format_from_path(output_path)
        format_name = format_name or self.default_format

        # Determine output path
        if output_path is None:
            if self.output_dir is None:
                raise ValueError("Either output_path or output_dir must be specified")
            output_path = self._generate_output_path(format_name)
        else:
            output_path = Path(output_path)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Format and write the report
        formatter = self.get_formatter(format_name)
        formatter.write_report(self.data, output_path, **kwargs)

        return output_path

    def print_report(
        self, format_name: Optional[str] = None, file=None, **kwargs: Any
    ) -> None:
        """Print the report to stdout or a file.

        Args:
            format_name: Format name (default: 'console')
            file: File-like object to write to (default: sys.stdout)
            **kwargs: Additional formatting options
        """
        if format_name is None:
            format_name = "console" if file is None else self.default_format

        if file is None:
            file = sys.stdout

        formatted = self.format_report(format_name, **kwargs)
        print(formatted, file=file)

    def _get_format_from_path(self, path: Union[str, Path]) -> str:
        """Determine format from file extension.

        Args:
            path: Path to the output file

        Returns:
            Format name
        """
        path = str(path).lower()

        # Check for known extensions
        if path.endswith(".json"):
            return "json"
        if path.endswith((".md", ".markdown")):
            return "markdown"
        if path.endswith((".txt", ".log")):
            return "console"

        return self.default_format

    def _generate_output_path(self, format_name: str) -> Path:
        """Generate an output path based on the format.

        Args:
            format_name: Format name

        Returns:
            Output path
        """
        if self.output_dir is None:
            raise ValueError("output_dir is not set")

        # Create a filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Map format to extension
        extensions = {
            "json": "json",
            "markdown": "md",
            "md": "md",
            "console": "log",
        }

        ext = extensions.get(format_name, "txt")
        filename = f"report_{timestamp}.{ext}"

        return self.output_dir / filename

    def generate_report(
        self,
        data: Any,
        formatter_name: str = "markdown",
        output_file: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> Path:
        """Generate a report from the provided data.

        Args:
            data: Data to include in the report
            formatter_name: Name of the formatter to use
            output_file: Path to the output file
            **kwargs: Additional formatting options

        Returns:
            Path to the generated report
        """
        logger.info(f"Generating report with formatter '{formatter_name}'")

        # Determine the output path
        if output_file:
            output_path = Path(output_file)
        elif self.output_dir:
            # Generate a filename based on the formatter
            output_path = self._generate_output_path(formatter_name)
        else:
            raise ValueError("No output path specified and no output_dir set")

        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get the formatter and use it to write the report
        try:
            # Sprawdź, czy formatter_name jest w self._formatter_instances
            if formatter_name in self._formatter_instances:
                # Pobierz instancję formatera
                formatter = self._formatter_instances[formatter_name]
                # Sformatuj dane i zapisz do pliku
                formatted_content = formatter.format_report(data, **kwargs)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
            # Sprawdź, czy formatter_name jest w self._formatters (klasy formaterów)
            elif formatter_name in self._formatters:
                # Użyj metody write_report, która utworzy instancję formatera
                output_path = self.write_report(
                    output_path=output_path, format_name=formatter_name, **kwargs
                )
            else:
                # Fallback - użyj domyślnego formatera
                logger.warning(
                    f"Formatter '{formatter_name}' not found, using default '{self.default_format}'"
                )
                # Użyj domyślnego formatera
                formatter = self.get_formatter(self.default_format)
                formatted_content = formatter.format_report(data, **kwargs)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            # Ensure the file exists even if there was an error
            if not output_path.exists():
                output_path.touch()

        # Ensure the file exists (create empty file if needed)
        if not output_path.exists():
            output_path.touch()

        return output_path
