"""
Tests for the TODO.md reporter functionality.
"""

from unittest.mock import mock_open, patch

import pytest

from domd.core.commands import Command
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

        # Call the method to get the content
        content = reporter.generate_report(sample_commands, sample_results)

        # Verify the content contains expected sections
        assert "# Project Commands" in content
        assert "test" in content
        assert "build" in content
        assert "Run tests" in content
        assert "Build project" in content

    def test_update_todo_md_with_existing_content(
        self, temp_project, sample_commands, sample_results
    ):
        """Test generating a report with existing content."""
        # Create a TODO.md file with existing content
        todo_path = temp_project / "TODO.md"
        existing_content = "# Existing TODO\n\n- [ ] Existing item\n"
        todo_path.write_text(existing_content, encoding="utf-8")

        reporter = TodoMdReporter(todo_path)

        # Call the method to get the content
        content = reporter.generate_report(sample_commands, sample_results)

        # Verify the content contains expected sections
        assert "# Project Commands" in content
        assert "test" in content
        assert "build" in content
        assert "Run tests" in content
        assert "Build project" in content

    def test_write_report(self, temp_project, sample_commands, sample_results):
        """Test writing the report to a file."""
        todo_path = temp_project / "TODO.md"
        assert not todo_path.exists()  # Ensure file doesn't exist

        reporter = TodoMdReporter(todo_path)
        content = reporter.generate_report(sample_commands, sample_results)

        # Write the content to the file
        reporter.write_report(content)

        # Verify the file was created and contains the expected content
        assert todo_path.exists()
        written_content = todo_path.read_text(encoding="utf-8")
        assert "# Project Commands" in written_content
        assert "test" in written_content
        assert "build" in written_content
