"""
Tests for the TODO.md reporter functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from domd.core.commands import Command, CommandResult
from domd.reporters.todo_md import TodoMdReporter


class TestTodoMdReporter:
    """Test cases for the TodoMdReporter class."""

    @pytest.fixture
    def sample_commands(self):
        """Sample commands for testing."""
        return [
            Command("test", "test", "Run tests", "test.py"),
            Command("build", "build", "Build project", "build.py"),
        ]

    @pytest.fixture
    def sample_failed_commands(self):
        """Sample failed commands for testing."""
        return [
            Command("test", "test", "Run tests", "test.py"),
            Command("build", "build", "Build project", "build.py"),
        ]

    @pytest.fixture
    def sample_results(self):
        """Sample command results for testing."""
        return [
            CommandResult(
                success=True,
                return_code=0,
                execution_time=1.23,
                stdout="Tests passed",
                stderr="",
                command="test",
                environment={},
            ),
            CommandResult(
                success=False,
                return_code=1,
                execution_time=2.34,
                stdout="Build failed",
                stderr="Error: Build failed",
                command="build",
                environment={},
            ),
        ]

    def test_generate_report(self, temp_project, sample_commands, sample_results):
        """Test generating a TODO.md report."""
        # Create a temporary TODO.md file
        todo_path = temp_project / "TODO.md"
        todo_path.touch()

        reporter = TodoMdReporter(todo_path)

        # Mock the file write operation
        with patch("builtins.open", mock_open()) as mock_file:
            reporter.generate_report(sample_commands, sample_results)

            # Verify the file was opened in write mode
            mock_file.assert_called_once_with(todo_path, "w", encoding="utf-8")

            # Get the content that was written
            written_content = "".join(
                call.args[0] for call in mock_file().write.call_args_list
            )

            # Verify the content contains expected sections
            assert "# Project Commands" in written_content
            assert "## Available Commands" in written_content
            assert "## Failed Commands" in written_content
            assert "test" in written_content
            assert "build" in written_content

    def test_update_todo_md_with_existing_content(
        self, temp_project, sample_commands, sample_results
    ):
        """Test updating an existing TODO.md file while preserving existing content."""
        # Create a TODO.md file with existing content
        todo_path = temp_project / "TODO.md"
        existing_content = "# Existing TODO\n\n- [ ] Existing item\n"
        todo_path.write_text(existing_content, encoding="utf-8")

        reporter = TodoMdReporter(todo_path)

        # Mock the file operations
        with patch("builtins.open", mock_open()) as mock_file:
            reporter.generate_report(sample_commands, sample_results)

            # Get the content that was written
            written_content = "".join(
                call.args[0] for call in mock_file().write.call_args_list
            )

            # Verify existing content is preserved and new content is added
            assert "# Existing TODO" in written_content
            assert "# Project Commands" in written_content
            assert "## Available Commands" in written_content
            assert "## Failed Commands" in written_content

    def test_handle_missing_todo_file(
        self, temp_project, sample_commands, sample_results
    ):
        """Test that a missing TODO.md file is created if it doesn't exist."""
        todo_path = temp_project / "TODO.md"
        assert not todo_path.exists()  # Ensure file doesn't exist

        reporter = TodoMdReporter(todo_path)

        # Mock the file operations
        with patch("builtins.open", mock_open()) as mock_file:
            reporter.generate_report(sample_commands, sample_results)

            # Verify the file was created and written to
            mock_file.assert_called_once_with(todo_path, "w", encoding="utf-8")
