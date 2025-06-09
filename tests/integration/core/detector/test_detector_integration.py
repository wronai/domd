"""
Integration tests for ProjectCommandDetector class.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.project_detection.command_handling import CommandHandler
from domd.core.project_detection.config_files import ConfigFileHandler
from domd.core.project_detection.detector import ProjectCommandDetector


class TestDetectorIntegration:
    """Integration test scenarios for ProjectCommandDetector."""

    def test_mixed_project_types(self, temp_project, sample_package_json):
        """Test project with multiple configuration file types."""
        # Create package.json
        package_json = temp_project / "package.json"
        package_json.write_text(json.dumps(sample_package_json))

        # Create Makefile
        makefile = temp_project / "Makefile"
        makefile_content = """
        test:
        	echo 'Running tests'

        build:
        	echo 'Building...'
        """
        makefile.write_text(makefile_content)

        # Mock the command handler to avoid actual command execution
        with patch(
            "domd.core.project_detection.detector.CommandHandler"
        ) as mock_handler:
            # Set up the mock to return commands
            mock_instance = mock_handler.return_value
            mock_instance.parse_commands.return_value = [
                {"command": "npm test", "source": str(package_json)},
                {"command": "make test", "source": str(makefile)},
                {"command": "make build", "source": str(makefile)},
            ]

            detector = ProjectCommandDetector(str(temp_project))
            commands = detector.scan_project()

            # Verify we found commands from both files
            assert len(commands) == 3
            assert any(cmd.get("command") == "npm test" for cmd in commands)
            assert any(cmd.get("command") == "make test" for cmd in commands)
            assert any(cmd.get("command") == "make build" for cmd in commands)

    def test_exclude_patterns_integration(self, temp_project):
        """Test exclude patterns in real scenario."""
        # Create test files
        include_file = temp_project / "include.txt"
        exclude_file = temp_project / "exclude.txt"
        include_file.touch()
        exclude_file.touch()

        # Create a mock config file handler
        with patch(
            "domd.core.project_detection.detector.ConfigFileHandler"
        ) as mock_handler:
            # Set up the mock to return our test files
            mock_instance = mock_handler.return_value
            mock_instance.find_config_files.return_value = [include_file, exclude_file]

            # Test with exclude pattern
            detector = ProjectCommandDetector(
                str(temp_project), exclude_patterns=["exclude.*"]
            )

            # Mock the command handler to avoid actual command execution
            with patch("domd.core.project_detection.detector.CommandHandler"):
                detector.scan_project()

                # Verify the config file handler was called with the correct exclude patterns
                mock_instance.find_config_files.assert_called_once()
                call_args = mock_instance.find_config_files.call_args[1]
                assert "exclude_patterns" in call_args
                assert "exclude.*" in call_args["exclude_patterns"]
