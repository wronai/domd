"""Tests for .dodocker file handling."""

from unittest.mock import MagicMock, os, patch

import pytest

from domd.core.command_execution.command_runner import CommandRunner
from domd.core.ports.command_handler import CommandHandler


class TestDodockerHandling:
    """Test handling of .dodocker file commands."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project with a .dodocker file."""
        project_path = tmp_path / "test_project"
        project_path.mkdir()

        # Create .dodocker file with mixed commands
        dodocker_content = """
        # Regular command (should run in shell)
        echo "Hello from shell"

        # Command to run in Docker
        docker: echo "Hello from Docker"

        # Another regular command
        ls -la

        # Another Docker command with pattern
        docker: pytest tests/*.py
        """

        (project_path / ".dodocker").write_text(dodocker_content)
        return project_path

    def test_dodocker_commands_parsing(self, temp_project):
        """Test that .dodocker commands are correctly parsed."""
        # Setup
        command_runner = MagicMock(spec=CommandRunner)
        handler = CommandHandler(temp_project, command_runner)

        # Verify commands were loaded correctly
        assert len(handler.docker_commands) == 4

        # Check regular command (should not run in Docker)
        assert handler.docker_commands.get('echo "Hello from shell"') is False

        # Check Docker command (should run in Docker)
        assert handler.docker_commands.get('echo "Hello from Docker"') is True

        # Check another regular command
        assert handler.docker_commands.get("ls -la") is False

        # Check Docker command with pattern
        assert handler.docker_commands.get("pytest tests/*.py") is True

    def test_should_run_in_docker(self, temp_project):
        """Test should_run_in_docker method behavior."""
        # Setup
        command_runner = MagicMock(spec=CommandRunner)
        handler = CommandHandler(temp_project, command_runner)

        # Test regular command (should not run in Docker)
        assert handler.should_run_in_docker('echo "Hello from shell"') is False

        # Test Docker command (should run in Docker)
        assert handler.should_run_in_docker('echo "Hello from Docker"') is True

        # Test command with pattern
        assert (
            handler.should_run_in_docker("pytest tests/unit/test_something.py") is True
        )

        # Test command not in .dodocker (should not run in Docker)
        assert handler.should_run_in_docker("some_other_command") is False

    @patch("subprocess.run")
    def test_docker_command_execution(self, mock_run, temp_project):
        """Test that Docker commands are properly executed in a container."""
        # Setup
        command_runner = MagicMock(spec=CommandRunner)
        handler = CommandHandler(temp_project, command_runner)

        # Mock the command runner
        mock_result = MagicMock()
        mock_result.return_code = 0
        mock_result.success = True
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_result.execution_time = 0.5

        command_runner.run.return_value = mock_result

        # Execute a Docker command
        cmd_info = {"command": 'echo "Hello from Docker"', "cwd": str(temp_project)}

        # The command is in .dodocker with docker: prefix, so it should run in Docker
        handler.execute_single_command(cmd_info)

        # Verify the command was executed with docker run
        command_runner.run.assert_called_once()
        actual_command = command_runner.run.call_args[1]["command"]
        assert "docker run --rm" in actual_command
        assert "python:3.9" in actual_command
        assert 'echo "Hello from Docker"' in actual_command

    @patch("subprocess.run")
    def test_shell_command_execution(self, mock_run, temp_project):
        """Test that regular commands are executed in shell, not in Docker."""
        # Setup
        command_runner = MagicMock(spec=CommandRunner)
        handler = CommandHandler(temp_project, command_runner)

        # Mock the command runner
        mock_result = MagicMock()
        mock_result.return_code = 0
        mock_result.success = True
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_result.execution_time = 0.5

        command_runner.run.return_value = mock_result

        # Execute a regular shell command
        cmd_info = {"command": 'echo "Hello from shell"', "cwd": str(temp_project)}

        # The command is in .dodocker without docker: prefix, so it should run in shell
        handler.execute_single_command(cmd_info)

        # Verify the command was executed directly, not in Docker
        command_runner.run.assert_called_once()
        actual_command = command_runner.run.call_args[1]["command"]
        assert "docker run" not in actual_command
        assert actual_command == 'echo "Hello from shell"'
