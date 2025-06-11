"""Tests for environment detection and Docker execution."""
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from docker.errors import DockerException

from domd.core.utils.environment import EnvironmentDetector, detect_environment


class TestEnvironmentDetection:
    """Test environment detection functionality."""

    def test_detect_environment(self):
        """Test basic environment detection."""
        env = detect_environment()
        assert "is_docker" in env
        assert "is_ci" in env
        assert "platform" in env
        assert "python_version" in env
        assert isinstance(env["python_version"], str)

    @patch("os.path.exists")
    def test_detect_environment_in_docker(self, mock_exists):
        """Test environment detection inside Docker."""
        mock_exists.return_value = True
        env = detect_environment()
        assert env["is_docker"] is True


class TestEnvironmentDetector:
    """Test EnvironmentDetector class."""

    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client."""
        with patch("docker.from_env") as mock_docker:
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_client.ping.return_value = True
            yield mock_client

    def test_init_with_docker(self, mock_docker_client):
        """Test initialization with Docker available."""
        detector = EnvironmentDetector()
        assert detector.docker_client is not None

    def test_init_without_docker(self):
        """Test initialization without Docker."""
        with patch("docker.from_env", side_effect=DockerException("No Docker")):
            detector = EnvironmentDetector()
            assert detector.docker_client is None

    def test_load_dodocker_config(self, tmp_path):
        """Test loading .dodocker config."""
        config_content = """
        pytest:
          image: python:3.9
          description: Test runner
        """
        with patch("builtins.open", mock_open(read_data=config_content)):
            detector = EnvironmentDetector()
            config = detector._load_dodocker_config()
            assert "pytest" in config
            assert config["pytest"]["image"] == "python:3.9"

    def test_get_docker_config(self, mock_docker_client):
        """Test getting Docker config for a command."""
        config_content = """
        pytest:
          image: python:3.9
        """
        with patch("builtins.open", mock_open(read_data=config_content)):
            detector = EnvironmentDetector()
            config = detector.get_docker_config("pytest tests/")
            assert config is not None
            assert config["image"] == "python:3.9"

    def test_should_use_docker(self, mock_docker_client):
        """Test Docker usage decision."""
        config_content = """
        pytest:
          image: python:3.9
        """
        with patch("builtins.open", mock_open(read_data=config_content)):
            detector = EnvironmentDetector()
            assert detector.should_use_docker("pytest tests/") is True
            assert detector.should_use_docker("ls -la") is False

    @patch("docker.models.containers.Container")
    def test_execute_in_docker(self, mock_container, mock_docker_client):
        """Test Docker command execution."""
        # Setup mock container
        mock_container.logs.return_value = [b"test output\n"]
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_docker_client.containers.run.return_value = mock_container

        detector = EnvironmentDetector()
        exit_code = detector.execute_in_docker("echo 'test'")

        assert exit_code == 0
        mock_docker_client.containers.run.assert_called_once()
        mock_container.logs.assert_called_once()
        mock_container.wait.assert_called_once()

    def test_expand_paths(self):
        """Test path expansion in Docker config."""
        detector = EnvironmentDetector()
        config = {
            "volumes": {
                "~/.ssh": "/root/.ssh",
                "/local/path": {"bind": "/container/path", "mode": "ro"},
            }
        }

        expanded = detector._expand_paths(config)
        assert "volumes" in expanded
        assert str(Path("~/.ssh").expanduser()) in expanded["volumes"]
        assert "/local/path" in expanded["volumes"]
        assert expanded["volumes"]["/local/path"] == {
            "bind": "/container/path",
            "mode": "ro",
        }
