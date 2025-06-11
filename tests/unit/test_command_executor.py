"""Tests for command execution with Docker support."""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.command_execution.executor import CommandExecutor
from domd.core.utils.environment import EnvironmentDetector


class TestCommandExecutor:
    """Test CommandExecutor class."""

    @pytest.fixture
    def mock_environment_detector(self):
        """Mock EnvironmentDetector."""
        with patch("domd.core.command_execution.executor.EnvironmentDetector") as mock:
            mock.return_value = MagicMock(spec=EnvironmentDetector)
            mock.return_value.should_use_docker.return_value = False
            mock.return_value.get_docker_config.return_value = None
            yield mock.return_value

    def test_init(self, mock_environment_detector):
        """Test command executor initialization."""
        executor = CommandExecutor("/test/path")
        assert executor.project_root == Path("/test/path").resolve()
        assert isinstance(executor.env_detector, EnvironmentDetector)

    @patch("subprocess.Popen")
    def test_execute_locally(self, mock_popen, mock_environment_detector):
        """Test local command execution."""
        # Setup mock process
        mock_process = MagicMock()
        mock_process.stdout = ["output1\n", "output2\n"]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        executor = CommandExecutor()
        exit_code = executor.execute("echo 'test'", cwd="/tmp")

        assert exit_code == 0
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert "echo 'test'" in args[0]
        # Handle both string and PosixPath for cwd
        cwd = kwargs["cwd"]
        assert str(cwd) == "/tmp"

    def test_execute_in_docker(self, mock_environment_detector):
        """Test Docker command execution."""
        # Setup mock environment detector
        mock_environment_detector.should_use_docker.return_value = True
        mock_environment_detector.get_docker_config.return_value = {
            "image": "python:3.9",
            "description": "Test runner",
        }
        mock_environment_detector.execute_in_docker.return_value = 0

        executor = CommandExecutor()
        exit_code = executor.execute("pytest", use_docker=True)

        assert exit_code == 0
        mock_environment_detector.execute_in_docker.assert_called_once()
        # Check that the command includes 'pytest' in the keyword arguments
        _, kwargs = mock_environment_detector.execute_in_docker.call_args
        assert "pytest" in kwargs["command"]

    @patch("subprocess.Popen")
    def test_execute_with_environment(self, mock_popen, mock_environment_detector):
        """Test command execution with custom environment variables."""
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_process.stdout = []
        mock_popen.return_value = mock_process

        executor = CommandExecutor()
        env_vars = {"TEST_VAR": "test_value", "PATH": "/custom/path"}
        executor.execute("echo $TEST_VAR", env=env_vars)

        _, kwargs = mock_popen.call_args
        assert "env" in kwargs
        assert kwargs["env"]["TEST_VAR"] == "test_value"
        assert "/custom/path" in kwargs["env"]["PATH"]

    @patch("subprocess.Popen")
    def test_execute_error_handling(self, mock_popen, mock_environment_detector):
        """Test command execution error handling."""
        mock_process = MagicMock()
        mock_process.wait.side_effect = subprocess.SubprocessError("Command failed")
        mock_popen.return_value = mock_process

        executor = CommandExecutor()
        exit_code = executor.execute("false")

        assert exit_code == 1

    @patch.object(CommandExecutor, "_execute_in_docker")
    def test_docker_execution_with_config(
        self, mock_execute_in_docker, mock_environment_detector
    ):
        """Test Docker execution with custom configuration."""
        # Setup mock environment detector
        docker_config = {
            "image": "custom-image:latest",
            "volumes": {"/host/path": "/container/path"},
            "environment": {"ENV_VAR": "value"},
            "workdir": "/custom/workdir",
        }
        mock_environment_detector.should_use_docker.return_value = True
        mock_environment_detector.get_docker_config.return_value = docker_config
        mock_execute_in_docker.return_value = 0

        executor = CommandExecutor()
        exit_code = executor.execute("run-tests")

        assert exit_code == 0
        mock_execute_in_docker.assert_called_once()
        args, kwargs = mock_execute_in_docker.call_args

        # Verify the command and docker_config are passed correctly
        assert args[0] == "run-tests"  # command
        assert kwargs["docker_config"] == docker_config
        assert kwargs["image"] == "custom-image:latest"

    def test_force_local_execution(self, mock_environment_detector):
        """Test forcing local execution even when Docker is available."""
        executor = CommandExecutor()
        executor.execute("ls -la", use_docker=False)

        # Should not call Docker-related methods
        mock_environment_detector.should_use_docker.assert_not_called()
        mock_environment_detector.execute_in_docker.assert_not_called()

    @patch("os.environ", {"PATH": "/usr/bin:/bin"})
    def test_environment_preservation(self, mock_environment_detector):
        """Test that environment variables are preserved."""
        executor = CommandExecutor()
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.wait.return_value = 0
            mock_process.stdout = []
            mock_popen.return_value = mock_process

            executor.execute("echo $PATH")

            _, kwargs = mock_popen.call_args
            assert "env" in kwargs
            assert "/usr/bin:/bin" in kwargs["env"]["PATH"]
