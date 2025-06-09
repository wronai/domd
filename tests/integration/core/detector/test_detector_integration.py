"""
Integration tests for ProjectCommandDetector class.
"""

import json
from unittest.mock import patch

import pytest

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

            def can_parse(self, file_path=None, content=None):
                if file_path is not None:
                    return file_path.name == "package.json"
                return False

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

            def can_parse(self, file_path=None, content=None):
                if file_path is not None:
                    return file_path.name.lower() in ("makefile", "gnumakefile")
                return False

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

        # Create mock parsers
        mock_parsers = [
            MockPackageJsonParser(),
            MockMakefileParser(),
        ]

        # Create the detector with our mock parsers and config files
        with patch(
            "domd.core.project_detection.detector.ParserRegistry.get_all_parsers"
        ) as mock_get_parsers, patch(
            "domd.core.project_detection.detector.ParserRegistry.get_parser_for_file"
        ) as mock_get_parser, patch(
            "domd.core.project_detection.detector.ConfigFileHandler.find_config_files"
        ) as mock_find_config_files:
            # Set up the mock to return our mock parsers
            mock_get_parsers.return_value = mock_parsers

            # Set up mock to return our test files
            test_files = [temp_project / "package.json", temp_project / "Makefile"]
            mock_find_config_files.return_value = test_files

            print("\n=== Test Files ===")
            for f in test_files:
                print(f"- {f} (exists: {f.exists()})")

            # Set up parser selection with debug output
            def get_parser_side_effect(file_path):
                print(f"\n=== Looking for parser for {file_path} ===")
                for parser in mock_parsers:
                    can_parse = parser.can_parse(file_path=file_path)
                    print(f"  - {parser.__class__.__name__}.can_parse: {can_parse}")
                    if can_parse:
                        print(f"  -> Selected parser: {parser.__class__.__name__}")
                        return parser
                print("  -> No suitable parser found")
                return None

            mock_get_parser.side_effect = get_parser_side_effect

            # Initialize the detector
            print("\n=== Initializing detector ===")
            detector = ProjectCommandDetector(str(temp_project))

            # Mock the command handler to avoid actual command execution
            with patch(
                "domd.core.project_detection.detector.CommandHandler"
            ) as mock_handler:
                mock_instance = mock_handler.return_value
                mock_instance.parse_commands.side_effect = (
                    lambda cmds: cmds
                )  # Just return the commands as-is

                # Patch the logger to capture log messages
                with patch(
                    "domd.core.project_detection.detector.logger"
                ) as mock_logger:
                    # Scan the project
                    print("\n=== Starting project scan ===")
                    commands = detector.scan_project()

                    # Print all log messages
                    print("\n=== Log Messages ===")
                    for call in mock_logger.method_calls:
                        if call[0] == "debug" and call[1] and len(call[1]) > 0:
                            print(f"DEBUG: {call[1][0]}")
                        elif call[0] == "info" and call[1] and len(call[1]) > 0:
                            print(f"INFO: {call[1][0]}")
                        elif call[0] == "warning" and call[1] and len(call[1]) > 0:
                            print(f"WARNING: {call[1][0]}")
                        elif call[0] == "error" and call[1] and len(call[1]) > 0:
                            print(f"ERROR: {call[1][0]}")

                print(f"\n=== Commands found: {len(commands)} ===")
                for i, cmd in enumerate(commands, 1):
                    print(f"Command {i}: {cmd}")

                # Verify we found commands from both files
                assert len(commands) == 4  # 2 from package.json + 2 from Makefile

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

            def can_parse(self, file_path=None, content=None):
                if file_path is not None:
                    return file_path.suffix == ".txt"
                return False

            def parse(self, file_path=None, content=None):
                return [
                    {
                        "command": f"process {file_path.name}",
                        "source": str(file_path),
                        "type": "test",
                        "metadata": {},
                    }
                ]

        # Create mock parser
        mock_parser = MockParser()

        # Create the detector with our mock parser and exclude pattern
        with patch(
            "domd.core.project_detection.detector.ParserRegistry.get_all_parsers"
        ) as mock_get_parsers, patch(
            "domd.core.project_detection.detector.ParserRegistry.get_parser_for_file"
        ) as mock_get_parser, patch(
            "domd.core.project_detection.detector.ProjectCommandDetector._should_process_file"
        ) as mock_should_process_file, patch.object(
            ConfigFileHandler, "find_config_files"
        ) as mock_find_config_files:
            # Set up the mock to return our mock parser
            mock_get_parsers.return_value = [mock_parser]
            mock_get_parser.return_value = mock_parser

            # Set up mock to return only include file
            test_files = [include_file]

            # Mock find_config_files to return only include file
            mock_find_config_files.return_value = test_files

            # Mock _should_process_file to exclude files matching the exclude pattern
            def should_process_side_effect(file_path):
                if str(file_path) == str(exclude_file):
                    return False
                return True

            mock_should_process_file.side_effect = should_process_side_effect

            print("\n=== Test Files ===")
            for f in test_files:
                print(f"- {f} (exists: {f.exists()})")

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

                # Patch the logger to capture log messages
                with patch(
                    "domd.core.project_detection.detector.logger"
                ) as mock_logger:
                    # Scan the project
                    print("\n=== Starting project scan ===")
                    commands = detector.scan_project()

                    # Print all log messages
                    print("\n=== Log Messages ===")
                    for call in mock_logger.method_calls:
                        if call[0] == "debug" and call[1] and len(call[1]) > 0:
                            print(f"DEBUG: {call[1][0]}")
                        elif call[0] == "info" and call[1] and len(call[1]) > 0:
                            print(f"INFO: {call[1][0]}")
                        elif call[0] == "warning" and call[1] and len(call[1]) > 0:
                            print(f"WARNING: {call[1][0]}")
                        elif call[0] == "error" and call[1] and len(call[1]) > 0:
                            print(f"ERROR: {call[1][0]}")

                # Convert commands to dict for easier assertion
                cmd_dicts = [
                    cmd if isinstance(cmd, dict) else cmd.__dict__ for cmd in commands
                ]

                print(f"\n=== Commands found: {len(cmd_dicts)} ===")
                for i, cmd in enumerate(cmd_dicts, 1):
                    print(f"Command {i}: {cmd}")

                # Verify only the include file was processed
                assert (
                    len(cmd_dicts) == 1
                ), f"Expected 1 command, got {len(cmd_dicts)}: {cmd_dicts}"
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
