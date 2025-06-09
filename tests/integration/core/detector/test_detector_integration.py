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

        # Create a mock parser for package.json
        class MockPackageJsonParser:
            supported_file_patterns = {"package.json"}

            def can_parse(self, file_path):
                return file_path.name == "package.json"

            def parse(self, file_path=None, content=None):
                return [
                    {
                        "command": "npm test",
                        "source": str(file_path),
                        "type": "npm_script",
                        "metadata": {},
                    }
                ]

        # Create a mock parser for Makefile
        class MockMakefileParser:
            supported_file_patterns = {"Makefile", "makefile"}

            def can_parse(self, file_path):
                return file_path.name.lower() in ("makefile", "gnumakefile")

            def parse(self, file_path=None, content=None):
                return [
                    {
                        "command": "make test",
                        "source": str(file_path),
                        "type": "make_target",
                        "metadata": {"target": "test"},
                    },
                    {
                        "command": "make build",
                        "source": str(file_path),
                        "type": "make_target",
                        "metadata": {"target": "build"},
                    },
                ]

        # Create the detector with our mock parsers
        with patch(
            "domd.core.project_detection.detector.ProjectCommandDetector._initialize_parsers"
        ) as mock_init_parsers:
            # Set up the mock to return our mock parsers
            mock_init_parsers.return_value = [
                MockPackageJsonParser(),
                MockMakefileParser(),
            ]

            # Initialize the detector
            detector = ProjectCommandDetector(str(temp_project))

            # Mock the command handler to avoid actual command execution
            with patch(
                "domd.core.project_detection.detector.CommandHandler"
            ) as mock_handler:
                mock_instance = mock_handler.return_value
                mock_instance.parse_commands.side_effect = (
                    lambda cmds: cmds
                )  # Just return the commands as-is

                # Scan the project
                commands = detector.scan_project()

                # Verify we found commands from both files
                assert (
                    len(commands) == 3
                ), f"Expected 3 commands, got {len(commands)}: {commands}"

                # Convert commands to dict for easier assertion
                cmd_dicts = [
                    cmd if isinstance(cmd, dict) else cmd.__dict__ for cmd in commands
                ]

                assert any(
                    cmd.get("command") == "npm test" for cmd in cmd_dicts
                ), "npm test command not found"
                assert any(
                    cmd.get("command") == "make test" for cmd in cmd_dicts
                ), "make test command not found"
                assert any(
                    cmd.get("command") == "make build" for cmd in cmd_dicts
                ), "make build command not found"

    def test_exclude_patterns_integration(self, temp_project):
        """Test exclude patterns in real scenario."""
        # Create test files
        include_file = temp_project / "include.txt"
        exclude_file = temp_project / "exclude.txt"
        include_file.write_text("test content")
        exclude_file.write_text("test content")

        # Create a mock parser that can parse both files
        class MockParser:
            supported_file_patterns = {"*.txt"}

            def can_parse(self, file_path):
                return file_path.suffix == ".txt"

            def parse(self, file_path=None, content=None):
                return [
                    {
                        "command": f"process {file_path.name}",
                        "source": str(file_path),
                        "type": "test",
                        "metadata": {},
                    }
                ]

        # Create the detector with our mock parser and exclude pattern
        with patch(
            "domd.core.project_detection.detector.ProjectCommandDetector._initialize_parsers"
        ) as mock_init_parsers:
            # Set up the mock to return our mock parser
            mock_init_parsers.return_value = [MockParser()]

            # Initialize the detector with exclude pattern
            detector = ProjectCommandDetector(
                str(temp_project), exclude_patterns=["exclude.*"]
            )

            # Mock the command handler to avoid actual command execution
            with patch(
                "domd.core.project_detection.detector.CommandHandler"
            ) as mock_handler:
                mock_instance = mock_handler.return_value
                mock_instance.parse_commands.side_effect = (
                    lambda cmds: cmds
                )  # Just return the commands as-is

                # Scan the project
                commands = detector.scan_project()

                # Convert commands to dict for easier assertion
                cmd_dicts = [
                    cmd if isinstance(cmd, dict) else cmd.__dict__ for cmd in commands
                ]

                # Verify only the include file was processed
                assert len(cmd_dicts) == 1, f"Expected 1 command, got {len(cmd_dicts)}"
                assert (
                    "include.txt" in cmd_dicts[0]["source"]
                ), "Excluded file was processed"

                # Verify the config handler was called with the correct exclude patterns
                assert hasattr(
                    detector.config_handler, "exclude_patterns"
                ), "Config handler missing exclude_patterns"
                assert (
                    "exclude.*" in detector.config_handler.exclude_patterns
                ), "Exclude pattern not set correctly"
