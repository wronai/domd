"""Integration tests for Docker command execution."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from domd.core.command_execution.executor import CommandExecutor
from domd.core.utils.environment import EnvironmentDetector

# Skip these tests if Docker is not available
pytestmark = pytest.mark.skipif(
    not EnvironmentDetector().docker_client, reason="Docker is not available"
)


class TestDockerIntegration:
    """Integration tests for Docker command execution."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.dodocker_path = self.test_dir / ".dodocker"

        # Create a simple .dodocker config
        config = {
            "echo": {"image": "alpine:latest", "description": "Test echo command"},
            "python": {"image": "python:3.9-slim", "description": "Python interpreter"},
        }

        with open(self.dodocker_path, "w") as f:
            yaml.dump(config, f)

    def test_docker_command_execution(self):
        """Test executing a command in Docker."""
        executor = CommandExecutor(str(self.test_dir))

        # This command should run in Docker based on .dodocker
        exit_code = executor.execute("echo 'Hello from Docker'")

        assert exit_code == 0

    def test_python_command_execution(self):
        """Test executing a Python command in Docker."""
        executor = CommandExecutor(str(self.test_dir))

        # This command should run in Docker based on .dodocker
        exit_code = executor.execute("python --version")

        assert exit_code == 0

    def test_local_command_execution(self):
        """Test that non-matching commands run locally."""
        # Mock subprocess to avoid actual command execution
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.wait.return_value = 0
            mock_process.stdout = []
            mock_popen.return_value = mock_process

            executor = CommandExecutor(str(self.test_dir))
            exit_code = executor.execute("ls -la", use_docker=False)

            assert exit_code == 0
            mock_popen.assert_called_once()

    def test_docker_command_with_volumes(self):
        """Test Docker command with volume mounts."""
        # Create a test file
        test_file = self.test_dir / "test.txt"
        test_file.write_text("test content")

        # Update .dodocker with volume configuration
        with open(self.dodocker_path, "r") as f:
            config = yaml.safe_load(f)

        config["cat"] = {
            "image": "alpine:latest",
            "volumes": {str(self.test_dir): "/test"},
            "workdir": "/test",
        }

        with open(self.dodocker_path, "w") as f:
            yaml.dump(config, f)

        executor = CommandExecutor(str(self.test_dir))
        exit_code = executor.execute("cat test.txt")

        assert exit_code == 0

    def test_docker_command_with_environment(self):
        """Test Docker command with environment variables."""
        # Update .dodocker with environment configuration
        with open(self.dodocker_path, "r") as f:
            config = yaml.safe_load(f)

        config["env"] = {
            "image": "alpine:latest",
            "environment": {"TEST_VAR": "test_value"},
            "command": "echo $TEST_VAR",
        }

        with open(self.dodocker_path, "w") as f:
            yaml.dump(config, f)

        executor = CommandExecutor(str(self.test_dir))
        exit_code = executor.execute("env")

        assert exit_code == 0

    def test_docker_command_failure(self):
        """Test handling of failed Docker commands."""
        executor = CommandExecutor(str(self.test_dir))

        # This command should fail
        exit_code = executor.execute("command_that_does_not_exist")

        assert exit_code != 0
