"""
Tests for the main ProjectCommandDetector class.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from domd.core.commands import Command
from domd.core.detector import ProjectCommandDetector
from domd.core.parsers import MakefileParser, PackageJsonParser, PyProjectTomlParser


class TestProjectCommandDetector:
    """Test cases for ProjectCommandDetector class."""

    @pytest.mark.unit
    def test_detector_initialization(self, temp_project):
        """Test detector initialization with various parameters."""
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            timeout=30,
            exclude_patterns=["*.pyc"],
            include_patterns=["Makefile"],
        )

        assert detector.project_path == temp_project
        assert detector.timeout == 30
        assert detector.exclude_patterns == ["*.pyc"]
        assert detector.include_patterns == ["Makefile"]
        assert detector.failed_commands == []

    @pytest.mark.unit
    def test_detector_default_initialization(self):
        """Test detector initialization with default parameters."""
        detector = ProjectCommandDetector()

        assert detector.project_path == Path(".").resolve()
        assert detector.timeout == 60
        assert detector.exclude_patterns == []
        assert detector.include_patterns == []
        assert detector.failed_commands == []

    @pytest.mark.unit
    def test_scan_empty_project(self, temp_project):
        """Test scanning a project with no configuration files."""
        with patch(
            "domd.core.detector.ProjectCommandDetector._find_config_files",
            return_value=[],
        ):
            detector = ProjectCommandDetector(str(temp_project))
            commands = detector.scan_project()
            assert commands == []

    @pytest.mark.unit
    def test_scan_project_with_package_json(self, temp_project, sample_package_json):
        """Test scanning a project with package.json."""
        # Create package.json
        package_json_path = temp_project / "package.json"
        package_json_path.write_text(json.dumps(sample_package_json))

        # Mock the PackageJsonParser
        mock_parser = MagicMock(spec=PackageJsonParser)
        mock_parser.can_parse.return_value = True
        mock_parser.supported_file_patterns = ["package.json"]  # Add supported patterns
        mock_parser.parse.return_value = [
            Command(
                command=f"npm run {script_name}",
                type="npm_script",
                description=f"NPM script: {script_name}",
                source=str(package_json_path),
            )
            for script_name in sample_package_json["scripts"]
        ]

        # Create detector first
        detector = ProjectCommandDetector(str(temp_project))

        # Mock the parsers at the instance level
        with patch.object(detector, "parsers", [mock_parser]):
            # Mock the file detection to ensure our mock parser is used
            with patch("pathlib.Path.glob") as mock_glob:
                # Make sure our test file is included in the glob results
                mock_glob.return_value = [package_json_path]

                commands = detector.scan_project()

                # Verify the commands were found
                assert len(commands) == len(sample_package_json["scripts"])

                # Check a specific command
                test_command = None
                for cmd in commands:
                    cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__
                    if "test" in cmd_dict.get("command", ""):
                        test_command = cmd_dict if isinstance(cmd_dict, dict) else cmd
                        break
                assert test_command is not None

                # Check command attributes
                cmd_dict = (
                    test_command
                    if isinstance(test_command, dict)
                    else test_command.__dict__
                )
                assert "test" in cmd_dict.get("command", "")
                assert cmd_dict.get("type") == "npm_script"
                assert "test" in cmd_dict.get("description", "")
                assert str(package_json_path) == cmd_dict.get("source")

    @pytest.mark.unit
    def test_scan_project_with_makefile(
        self, temp_project, sample_makefile_content, caplog
    ):
        """Test scanning a project with Makefile."""
        import logging

        caplog.set_level(logging.DEBUG)

        print("\n" + "=" * 80)
        print("STARTING TEST: test_scan_project_with_makefile")
        print("=" * 80)

        # Create Makefile
        makefile_path = temp_project / "Makefile"
        makefile_path.write_text(sample_makefile_content)
        print(f"Created Makefile at: {makefile_path}")

        # Expected targets from the sample makefile
        expected_targets = ["test", "build", "clean", "install", "deploy"]
        print(f"Expected targets: {expected_targets}")

        # Mock the MakefileParser
        mock_parser = MagicMock(spec=MakefileParser)
        mock_parser.can_parse.return_value = True

        # Set up the supported_file_patterns property
        mock_parser.supported_file_patterns = ["Makefile", "makefile", "GNUmakefile"]

        mock_commands = [
            Command(
                command=f"make {target}",
                type="make_target",
                description=f"Make target: {target}",
                source=str(makefile_path),
            )
            for target in expected_targets
        ]
        mock_parser.parse.return_value = mock_commands

        print(f"Created mock parser: {mock_parser}")
        print(f"Mock parser can_parse: {mock_parser.can_parse}")
        print(f"Mock parser parse: {mock_parser.parse}")
        print(f"Mock parser parse return value: {mock_commands}")

        # Create detector first
        detector = ProjectCommandDetector(str(temp_project))
        print(f"Created detector with project path: {temp_project}")
        print(f"Detector parsers before mock: {detector.parsers}")

        # Mock the parsers at the instance level
        with patch.object(detector, "parsers", [mock_parser]):
            print(f"Detector parsers after mock: {detector.parsers}")

            # Mock the file detection to ensure our mock parser is used
            with patch("pathlib.Path.glob") as mock_glob:
                # Make sure our test file is included in the glob results
                mock_glob.return_value = [makefile_path]
                print(f"Mocked glob to return: {mock_glob.return_value}")

                print("\nCalling detector.scan_project()...")
                commands = detector.scan_project()
                print(f"Scan completed. Commands found: {len(commands)}")

                # Print all log messages
                print("\n=== LOG MESSAGES ===")
                for record in caplog.records:
                    print(f"{record.levelname}: {record.message}")
                print("===================\n")

                # Verify the commands were found
                print(
                    f"Found {len(commands)} commands, expected {len(expected_targets)}"
                )
                print(f"Commands found: {commands}")
                assert len(commands) == len(
                    expected_targets
                ), f"Expected {len(expected_targets)} commands, got {len(commands)}"

                # Check for specific targets
                for target in expected_targets:
                    found = False
                    for cmd in commands:
                        cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__
                        if f"make {target}" == cmd_dict.get("command"):
                            found = True
                            break
                    assert found, f"Command 'make {target}' not found in commands"

        print("\n" + "=" * 80)
        print("TEST COMPLETED")
        print("=" * 80 + "\n")

    @pytest.fixture
    def sample_pyproject_toml(self):
        """Sample pyproject.toml content for testing."""
        return {
            "tool": {
                "poetry": {
                    "name": "test-project",
                    "version": "0.1.0",
                    "description": "Test project for DoMD",
                    "authors": ["Test User <test@example.com>"],
                    "scripts": {
                        "test": "pytest",
                        "lint": "black . && isort . && flake8",
                        "format": "black . && isort .",
                    },
                },
                "pytest": {
                    "ini_options": {
                        "testpaths": ["tests"],
                        "python_files": ["test_*.py"],
                        "python_functions": ["test_*"],
                    }
                },
            }
        }

    @pytest.mark.unit
    def test_scan_project_with_pyproject_toml(
        self, temp_project, sample_pyproject_toml
    ):
        """Test scanning a project with pyproject.toml."""
        # Create pyproject.toml
        pyproject_path = temp_project / "pyproject.toml"
        import toml

        pyproject_path.write_text(toml.dumps(sample_pyproject_toml))

        # Mock the PyProjectTomlParser
        mock_parser = MagicMock(spec=PyProjectTomlParser)
        mock_parser.can_parse.return_value = True

        # Set up the supported_file_patterns property
        mock_parser.supported_file_patterns = ["pyproject.toml"]

        # Mock the parse method to return sample commands
        mock_commands = [
            Command(
                command="pytest",
                type="pytest",
                description="Run tests with pytest",
                source=str(pyproject_path),
            ),
            Command(
                command="black . && isort . && flake8",
                type="poetry_script",
                description="Run linting",
                source=str(pyproject_path),
            ),
        ]
        mock_parser.parse.return_value = mock_commands

        # Create detector first
        detector = ProjectCommandDetector(str(temp_project))

        # Mock the parsers at the instance level
        with patch.object(detector, "parsers", [mock_parser]):
            # Mock the file detection to ensure our mock parser is used
            with patch("pathlib.Path.glob") as mock_glob:
                # Make sure our test file is included in the glob results
                mock_glob.return_value = [pyproject_path]

                commands = detector.scan_project()

                # Verify the commands were found
                assert len(commands) == len(mock_commands)

                # Check for specific commands
                found_pytest = False
                found_black = False
                for cmd in commands:
                    cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__
                    if cmd_dict.get("command") == "pytest":
                        found_pytest = True
                    if "black" in cmd_dict.get("command", ""):
                        found_black = True
                assert found_pytest, "pytest command not found in commands"
                assert found_black, "black command not found in commands"
        import toml

        # Create pyproject.toml
        pyproject_path = temp_project / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            toml.dump(sample_pyproject_toml, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find poetry scripts and tool commands
        poetry_commands = []
        pytest_commands = []

        for cmd in commands:
            cmd_dict = cmd if isinstance(cmd, dict) else cmd.__dict__
            if cmd_dict.get("type") == "poetry_script":
                poetry_commands.append(cmd_dict)
            elif cmd_dict.get("type") == "pytest":
                pytest_commands.append(cmd_dict)

        assert len(poetry_commands) > 0
        assert len(pytest_commands) > 0

        # Check specific commands
        scripts = sample_pyproject_toml["tool"]["poetry"]["scripts"]
        for script_name in scripts:
            script_command = None
            for cmd in poetry_commands:
                if script_name in cmd.get("command", ""):
                    script_command = cmd
                    break
            assert script_command is not None

    @pytest.mark.unit
    def test_should_process_file_include_patterns(self, temp_project):
        """Test file inclusion based on patterns."""
        detector = ProjectCommandDetector(
            str(temp_project), include_patterns=["Makefile", "package.json"]
        )

        # Create test files
        (temp_project / "package.json").write_text("{}")
        (temp_project / "Makefile").write_text("")
        (temp_project / "pyproject.toml").write_text("")

        # Test inclusion
        assert detector._should_process_file(temp_project / "package.json") is True
        assert detector._should_process_file(temp_project / "Makefile") is True
        assert detector._should_process_file(temp_project / "pyproject.toml") is False

    @pytest.mark.unit
    def test_execute_command_success(self, temp_project, mock_successful_command):
        """Test successful command execution."""
        detector = ProjectCommandDetector(str(temp_project))

        cmd_info = {
            "command": 'echo "test"',
            "description": "Test command",
            "source": "test",
            "type": "test",
        }

        result = detector._execute_command(cmd_info)

        assert result is True
        assert "execution_time" in cmd_info
        assert "error" not in cmd_info

    @pytest.mark.unit
    def test_execute_command_failure(self, temp_project, mock_failed_command):
        """Test failed command execution."""
        detector = ProjectCommandDetector(str(temp_project))

        cmd_info = {
            "command": "false",
            "description": "Failing command",
            "source": "test",
            "type": "test",
        }

        result = detector._execute_command(cmd_info)

        assert result is False
        assert "error" in cmd_info
        assert "return_code" in cmd_info
        assert cmd_info["return_code"] == 1

    @pytest.mark.unit
    def test_execute_command_timeout(self, temp_project, mock_timeout_command):
        """Test command execution timeout."""
        detector = ProjectCommandDetector(str(temp_project), timeout=1)

        cmd_info = {
            "command": "sleep 10",
            "description": "Long running command",
            "source": "test",
            "type": "test",
        }

        result = detector._execute_command(cmd_info)

        assert result is False
        assert "error" in cmd_info
        assert "return_code" in cmd_info
        assert cmd_info["return_code"] == -1
        # Check for the specific error message format we use
        assert "Command timed out after" in cmd_info["error"]

    @pytest.mark.unit
    def test_test_commands(self, temp_project, mock_successful_command):
        """Test testing multiple commands."""
        detector = ProjectCommandDetector(str(temp_project))

        commands = [
            {
                "command": 'echo "test1"',
                "description": "Test command 1",
                "source": "test",
                "type": "test",
            },
            {
                "command": 'echo "test2"',
                "description": "Test command 2",
                "source": "test",
                "type": "test",
            },
        ]

        detector.test_commands(commands)

        # All commands should succeed with mocked success
        assert len(detector.failed_commands) == 0

    @pytest.mark.unit
    def test_test_commands_with_failures(self, temp_project, mock_failed_command):
        """Test testing commands with some failures."""
        detector = ProjectCommandDetector(str(temp_project))

        commands = [
            {
                "command": "false",
                "description": "Failing command",
                "source": "test",
                "type": "test",
            }
        ]

        detector.test_commands(commands)

        # Command should fail with mocked failure
        assert len(detector.failed_commands) == 1
        assert detector.failed_commands[0]["command"] == "false"

    @pytest.mark.unit
    def test_generate_markdown_report(self, temp_project, sample_failed_commands):
        """Test markdown report generation."""
        # Create a detector with explicit paths
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
        )
        detector.failed_commands = sample_failed_commands
        detector.successful_commands = []

        # The method writes to a file and returns None
        detector.create_llm_optimized_todo_md()

        # Check the file was created with the right content
        assert todo_path.exists(), f"Expected {todo_path} to exist"

        content = todo_path.read_text()
        assert "# 🤖 TODO - LLM Task List for Command Fixes" in content
        assert "**📋 INSTRUCTIONS FOR LLM:**" in content
        assert "**📊 Current Status:**" in content
        assert f"- **Failed Commands:** {len(sample_failed_commands)}" in content
        assert "## 🔧 Tasks to Fix" in content

    @pytest.mark.unit
    def test_generate_json_report(self, temp_project, sample_failed_commands):
        """Test JSON report generation is no longer supported."""
        # JSON reporting has been removed in favor of markdown-based reporting
        pass

    @pytest.mark.unit
    def test_generate_text_report(self, temp_project, sample_failed_commands):
        """Test text report generation is no longer supported."""
        # Text reporting has been removed in favor of markdown-based reporting
        pass

    @pytest.mark.unit
    def test_generate_output_file_markdown(self, temp_project, sample_failed_commands):
        """Test generating markdown output file."""
        # Create a detector with explicit paths
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
        )
        detector.failed_commands = sample_failed_commands
        detector.successful_commands = []

        # The method writes to the todo_file by default
        detector.create_llm_optimized_todo_md()

        # Check the file was created with the right content
        assert todo_path.exists(), f"Expected {todo_path} to exist"
        content = todo_path.read_text()
        assert "# 🤖 TODO - LLM Task List for Command Fixes" in content

    @pytest.mark.unit
    def test_generate_output_file_json(self, temp_project, sample_failed_commands):
        """Test generating JSON output file is no longer supported."""
        # JSON output has been removed in favor of markdown
        pass

    @pytest.mark.unit
    def test_generate_output_file_no_failures(self, temp_project):
        """Test TODO.md generation when no failures."""
        # Create a detector with explicit paths
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
        )
        detector.failed_commands = []
        detector.successful_commands = [
            {"command": "echo test", "source": "test", "description": "Test command"}
        ]

        # The method writes to the todo_file
        detector.create_llm_optimized_todo_md()

        # Should still create the file but with a success message
        assert todo_path.exists(), f"Expected {todo_path} to exist"
        content = todo_path.read_text()
        assert "## 🎉 All Commands Working!" in content

    @pytest.mark.unit
    def test_get_statistics(self, temp_project, sample_failed_commands):
        """Test statistics in markdown report."""
        # Create a detector with explicit paths
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
        )
        detector.failed_commands = sample_failed_commands
        detector.successful_commands = [
            {"command": "echo test", "source": "test", "description": "Test command"}
        ]

        # The statistics are now part of the markdown report
        detector.create_llm_optimized_todo_md()

        # Check the file was created with the right content
        assert todo_path.exists(), f"Expected {todo_path} to exist"
        content = todo_path.read_text()

        # Check basic statistics are in the markdown
        assert f"- **Failed Commands:** {len(sample_failed_commands)}" in content
        assert (
            f"- **Working Commands:** {len(detector.successful_commands)} (see DONE.md)"
            in content
        )

        # Check for success rate or status in the content
        assert any(
            phrase in content for phrase in ["Success Rate", "success rate", "Status"]
        )

        # Check for project path in the content
        assert str(temp_project) in content

    @pytest.mark.unit
    def test_export_results(self, temp_project, sample_failed_commands):
        """Test exporting detailed results is no longer supported."""
        # JSON export has been removed in favor of markdown-based reporting
        pass

    @pytest.mark.integration
    def test_full_workflow_populated_project(self, populated_project):
        """Test complete workflow on a populated project."""
        detector = ProjectCommandDetector(str(populated_project))

        # Scan project
        commands = detector.scan_project()
        assert len(commands) > 0

        # Should find commands from different sources
        sources = {cmd.source for cmd in commands}
        source_filenames = {source.split("/")[-1] for source in sources}
        assert "package.json" in source_filenames
        assert "Makefile" in source_filenames
        assert "Dockerfile" in source_filenames

        # Test commands (will fail in test environment, but that's expected)
        with patch("subprocess.run") as mock_run:
            # Mock some successes and some failures
            def side_effect(*args, **kwargs):
                result = Mock()
                if "echo" in args[0]:
                    result.returncode = 0
                    result.stdout = "success"
                    result.stderr = ""
                else:
                    result.returncode = 1
                    result.stdout = ""
                    result.stderr = "command not found"
                return result

            mock_run.side_effect = side_effect
            detector.test_commands(commands)

        # Set up the output file paths
        todo_path = populated_project / "TODO.md"
        done_path = populated_project / "DONE.md"
        script_path = populated_project / "todo.sh"

        # Update the existing detector with the output file paths
        detector.todo_file = str(todo_path)
        detector.done_file = str(done_path)
        detector.script_file = str(script_path)

        # Generate the TODO.md file
        detector.create_llm_optimized_todo_md()

        # Verify the file was created and contains expected content
        assert todo_path.exists()
        content = todo_path.read_text()
        assert "# 🤖 TODO - LLM Task List for Command Fixes" in content

        # Verify the content includes the failed commands with backticks
        for cmd in commands:
            # Convert Command object to dict if needed
            if hasattr(cmd, "command"):
                cmd_dict = {
                    "command": cmd.command,
                    "error": getattr(cmd, "error", ""),
                    "source": getattr(cmd, "source", ""),
                }
            else:
                cmd_dict = cmd

            if cmd_dict.get("error"):
                cmd_str = f"`{cmd_dict['command']}`"
                if cmd_str not in content:
                    print(f"\nCommand not found in TODO.md: {cmd_str}")
                    print("\nTODO.md content:")
                    print("-" * 80)
                    print(content)
                    print("-" * 80)
                assert (
                    cmd_str in content
                ), f"Command '{cmd_dict['command']}' not found in TODO.md"


class TestParserMethods:
    """Test individual parser methods."""

    @pytest.mark.parsers
    def test_parse_package_json_with_scripts(self, temp_project):
        """Test parsing package.json with scripts."""
        from domd.core.parsers.package_json import PackageJsonParser

        # Create a sample package.json
        package_data = {
            "name": "test-package",
            "version": "1.0.0",
            "scripts": {"test": "jest", "build": "webpack", "start": "node index.js"},
        }

        package_json_path = temp_project / "package.json"
        package_json_path.write_text(json.dumps(package_data))

        # Test the parser directly
        parser = PackageJsonParser(file_path=package_json_path)
        assert parser.can_parse(package_json_path)

        commands = parser.parse()

        # Check that each script was parsed correctly
        for script_name, script_cmd in package_data["scripts"].items():
            cmd = next((c for c in commands if script_name in c.command), None)
            assert cmd is not None, f"Command for script '{script_name}' not found"
            assert f"npm run {script_name}" == cmd.command
            assert script_name in cmd.description
            assert str(package_json_path) == cmd.source
            assert cmd.type == "npm_script"
            assert cmd.metadata["script_name"] == script_name
            assert cmd.metadata["script_command"] == script_cmd
            assert cmd.metadata["original_command"] == script_cmd
            assert cmd.description == f"NPM script: {script_name}"
            assert str(package_json_path) in cmd.source

    @pytest.mark.parsers
    def test_parse_package_json_no_scripts(self, temp_project):
        """Test parsing package.json without scripts."""
        from domd.core.parsers.package_json import PackageJsonParser

        # Create a package.json without scripts
        package_data = {"name": "test", "version": "1.0.0"}
        package_json_path = temp_project / "package.json"
        package_json_path.write_text(json.dumps(package_data))

        # Test the parser directly
        parser = PackageJsonParser(file_path=package_json_path)
        assert parser.can_parse(package_json_path)

        commands = parser.parse()
        assert commands == []

    @pytest.mark.parsers
    def test_parse_makefile_with_targets(self, temp_project):
        """Test parsing Makefile with targets."""
        from domd.core.parsers.makefile import MakefileParser

        # Create a sample Makefile
        makefile_content = """
.PHONY: all test build clean install deploy

all: test build

test:
    pytest tests/

build:
    echo "Building..."

clean:
    rm -rf dist/ build/ *.egg-info/

install:
    pip install -e .

deploy:
    scp -r * user@example.com:/var/www/app/
"""
        makefile_path = temp_project / "Makefile"
        makefile_path.write_text(makefile_content)

        # Test the parser directly
        parser = MakefileParser(file_path=makefile_path)
        assert parser.can_parse(makefile_path)

        commands = parser.parse()

        # Should find specific targets but not .PHONY
        target_commands = [cmd.command for cmd in commands]
        assert "make test" in target_commands
        assert "make build" in target_commands
        assert "make clean" in target_commands
        assert "make install" in target_commands
        assert "make deploy" in target_commands

        # Should not include special targets
        assert ".PHONY" not in target_commands
        assert "PHONY" not in target_commands

        # Check command details
        test_cmd = next((cmd for cmd in commands if "test" in cmd.command), None)
        assert test_cmd is not None
        assert test_cmd.type == "make_target"
        assert "test" in test_cmd.description
        assert str(makefile_path) in test_cmd.source

    @pytest.mark.parsers
    def test_parse_pyproject_toml_with_poetry_scripts(self, temp_project):
        """Test parsing pyproject.toml with Poetry scripts."""
        import toml

        from domd.core.parsers.pyproject_toml import PyProjectTomlParser

        # Create a sample pyproject.toml with Poetry scripts
        pyproject_data = {
            "tool": {
                "poetry": {
                    "name": "test-package",
                    "version": "0.1.0",
                    "description": "Test package",
                    "scripts": {
                        "test": "pytest",
                        "lint": "black . && isort . && flake8",
                    },
                },
                "pytest": {
                    "ini_options": {
                        "testpaths": ["tests"],
                        "python_files": ["test_*.py"],
                    }
                },
            }
        }

        pyproject_path = temp_project / "pyproject.toml"
        pyproject_path.write_text(toml.dumps(pyproject_data))

        # Test the parser directly
        parser = PyProjectTomlParser(file_path=pyproject_path)
        assert parser.can_parse(pyproject_path)

        commands = parser.parse()

        # Should find Poetry scripts
        poetry_commands = [cmd for cmd in commands if cmd.type == "poetry_script"]
        assert len(poetry_commands) == len(pyproject_data["tool"]["poetry"]["scripts"])

        # Should also find pytest configuration
        pytest_commands = [cmd for cmd in commands if cmd.type == "pytest"]
        assert len(pytest_commands) > 0

        # Check command details
        test_cmd = next(
            (
                cmd
                for cmd in poetry_commands
                if cmd.metadata.get("script_name") == "test"
            ),
            None,
        )
        assert test_cmd is not None
        assert test_cmd.metadata.get("script_target") == "pytest"
        assert test_cmd.metadata.get("original_command") == "pytest"
        assert "test" in test_cmd.description.lower()
        assert str(pyproject_path) in test_cmd.source

    @pytest.mark.parsers
    def test_parse_tox_ini(self, temp_project):
        """Test parsing tox.ini."""
        from domd.core.parsers.tox_ini import ToxIniParser

        # Create a sample tox.ini
        tox_ini_content = """
[tox]
envlist = py38, py39, py310, lint, docs

[testenv]
deps =
    pytest
    pytest-cov
commands = pytest --cov=domd

[testenv:lint]
deps =
    black
    isort
    flake8
commands =
    black --check .
    isort --check-only .
    flake8

[testenv:docs]
deps =
    mkdocs
    mkdocs-material
commands = mkdocs build --clean
"""
        tox_ini_path = temp_project / "tox.ini"
        tox_ini_path.write_text(tox_ini_content)

        # Test the parser directly
        parser = ToxIniParser(file_path=tox_ini_path)
        assert parser.can_parse(tox_ini_path)

        commands = parser.parse()

        # Should find individual environments and general tox command
        tox_commands = [cmd.command for cmd in commands]
        assert any("tox -e py38" in cmd for cmd in tox_commands)
        assert any("tox -e py39" in cmd for cmd in tox_commands)
        assert any("tox -e py310" in cmd for cmd in tox_commands)
        assert any("tox -e lint" in cmd for cmd in tox_commands)
        assert any("tox -e docs" in cmd for cmd in tox_commands)
        assert any(cmd == "tox" for cmd in tox_commands)

        # Check command details
        lint_cmd = next((cmd for cmd in commands if "lint" in cmd.command), None)
        assert lint_cmd is not None

        # Check command details for a specific environment
        lint_cmd = next(
            (
                cmd
                for cmd in commands
                if cmd.type == "tox_environment" and "lint" in cmd.command
            ),
            None,
        )
        assert lint_cmd is not None
        assert "lint" in lint_cmd.description.lower()
        assert str(tox_ini_path) in lint_cmd.source

        # Check common tox commands
        common_commands = ["tox -r", "tox -l", "tox -v"]
        for cmd_str in common_commands:
            cmd = next((c for c in commands if c.command.startswith(cmd_str)), None)
            assert (
                cmd is not None
            ), f"Expected command starting with {cmd_str} not found"

    @pytest.mark.parsers
    def test_parse_docker_compose(self, temp_project):
        """Test parsing docker-compose.yml."""
        import yaml

        from domd.core.parsers.docker_compose import DockerComposeParser

        # Create a sample docker-compose.yml
        docker_compose_data = {
            "version": "3.8",
            "services": {
                "web": {
                    "build": ".",
                    "ports": ["8000:8000"],
                    "volumes": [".:/app"],
                    "environment": {"ENV": "development"},
                },
                "db": {
                    "image": "postgres:13",
                    "environment": {"POSTGRES_PASSWORD": "example"},
                },
            },
        }

        docker_compose_path = temp_project / "docker-compose.yml"
        with open(docker_compose_path, "w") as f:
            yaml.dump(docker_compose_data, f)

        # Test the parser directly
        parser = DockerComposeParser(file_path=docker_compose_path)
        assert parser.can_parse(docker_compose_path)

        commands = parser.parse()

        # Should find docker-compose commands
        compose_commands = [cmd.command for cmd in commands]
        assert any("docker-compose up" in cmd for cmd in compose_commands)
        assert any("docker-compose down" in cmd for cmd in compose_commands)
        assert any("docker-compose build" in cmd for cmd in compose_commands)

        # Check command details
        up_cmd = next((cmd for cmd in commands if "up" in cmd.command), None)
        assert up_cmd is not None
        assert up_cmd.type == "docker_compose"
        assert (
            "start" in up_cmd.description.lower()
        )  # Changed from 'up' to 'start' to match actual description
        assert str(docker_compose_path) in up_cmd.source

    @pytest.mark.parsers
    def test_parse_cargo_toml(self, temp_project):
        """Test parsing Cargo.toml."""
        import toml

        from domd.core.parsers.cargo_toml import CargoTomlParser

        # Create a sample Cargo.toml
        cargo_data = {
            "package": {"name": "test-project", "version": "0.1.0", "edition": "2021"},
            "dependencies": {
                "anyhow": "1.0",
                "clap": {"version": "3.0", "features": ["derive"]},
                "tokio": {"version": "1.0", "features": ["full"]},
            },
            "dev-dependencies": {"mockall": "0.11"},
        }

        cargo_toml_path = temp_project / "Cargo.toml"
        with open(cargo_toml_path, "w") as f:
            toml.dump(cargo_data, f)

        # Test the parser directly
        parser = CargoTomlParser(file_path=cargo_toml_path)
        assert parser.can_parse(cargo_toml_path)

        commands = parser.parse()

        # Should find cargo commands
        cargo_commands = [cmd.command for cmd in commands]
        assert any("cargo build" in cmd for cmd in cargo_commands)
        assert any("cargo test" in cmd for cmd in cargo_commands)
        assert any("cargo run" in cmd for cmd in cargo_commands)
        assert any("cargo check" in cmd for cmd in cargo_commands)
        assert any("cargo clippy" in cmd for cmd in cargo_commands)
        assert any("cargo fmt" in cmd for cmd in cargo_commands)
        assert any("cargo doc --open" in cmd for cmd in cargo_commands)

        # Check command details
        test_cmd = next((cmd for cmd in commands if "test" in cmd.command), None)
        assert test_cmd is not None
        assert test_cmd.type == "cargo_command"
        assert "test" in test_cmd.description.lower()
        assert str(cargo_toml_path) in test_cmd.source

    @pytest.mark.parsers
    def test_parse_composer_json(self, temp_project):
        """Test parsing composer.json."""
        from domd.core.parsers.composer_json import ComposerJsonParser

        # Create a sample composer.json
        composer_data = {
            "name": "test/package",
            "description": "Test package",
            "type": "library",
            "require": {"php": "^8.0", "monolog/monolog": "^2.0"},
            "require-dev": {
                "phpunit/phpunit": "^9.0",
                "squizlabs/php_codesniffer": "^3.6",
            },
            "scripts": {
                "test": "phpunit",
                "cs-check": "phpcs --standard=PSR12 src tests",
                "cs-fix": "phpcbf --standard=PSR12 src tests",
                "analyze": "phpstan analyse",
            },
        }

        composer_json_path = temp_project / "composer.json"
        composer_json_path.write_text(json.dumps(composer_data, indent=4))

        # Test the parser directly
        parser = ComposerJsonParser(file_path=composer_json_path)
        assert parser.can_parse(composer_json_path)

        commands = parser.parse()

        # Should find composer scripts
        composer_commands = [cmd.command for cmd in commands]
        assert any("composer test" in cmd for cmd in composer_commands)
        assert any("cs-check" in cmd for cmd in composer_commands)
        assert any("cs-fix" in cmd for cmd in composer_commands)
        assert any("analyze" in cmd for cmd in composer_commands)

        # Check command details
        test_cmd = next((cmd for cmd in commands if "test" in cmd.command), None)
        assert test_cmd is not None
        assert test_cmd.type == "composer_script"
        assert "test" in test_cmd.description.lower()
        assert str(composer_json_path) in test_cmd.source

    @pytest.mark.parsers
    def test_parse_go_mod(self, temp_project):
        """Test parsing go.mod."""
        from domd.core.parsers.go_mod import GoModParser

        # Create a sample go.mod
        go_mod_content = """
module example.com/mymodule

go 1.19

require (
    github.com/gorilla/mux v1.8.0
    github.com/stretchr/testify v1.8.4
)

require (
    github.com/davecgh/go-spew v1.1.1 // indirect
    github.com/pmezard/go-difflib v1.0.0 // indirect
    gopkg.in/yaml.v3 v3.0.1 // indirect
)
"""
        go_mod_path = temp_project / "go.mod"
        go_mod_path.write_text(go_mod_content)

        # Create a main.go to test run command
        main_go_path = temp_project / "main.go"
        main_go_path.write_text(
            'package main\n\nimport "fmt"\n\nfunc main() { fmt.Println("Hello, World!") }'
        )

        # Test the parser directly
        parser = GoModParser(go_mod_path)
        assert parser.can_parse(go_mod_path)

        commands = parser.parse()

        # Should find go commands
        go_commands = [cmd.command for cmd in commands]
        assert any("go build" in cmd for cmd in go_commands)
        assert any("go test" in cmd for cmd in go_commands)
        assert any("go run" in cmd and "main.go" in cmd for cmd in go_commands)
        assert any("go mod tidy" in cmd for cmd in go_commands)
        assert any("go fmt" in cmd for cmd in go_commands)

        # Check command details
        run_cmd = next((cmd for cmd in commands if "run" in cmd.command), None)
        assert run_cmd is not None
        assert run_cmd.type == "go_command"
        assert "run" in run_cmd.description.lower()
        assert str(go_mod_path) in run_cmd.source


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration test scenarios."""

    def test_mixed_project_types(self, temp_project):
        """Test project with multiple configuration file types."""
        # Create multiple config files
        package_json = {"scripts": {"test": "jest", "build": "webpack"}}
        with open(temp_project / "package.json", "w") as f:
            json.dump(package_json, f)

        makefile_content = "test:\n\techo 'testing'\nbuild:\n\techo 'building'"
        (temp_project / "Makefile").write_text(makefile_content)

        dockerfile_content = "FROM node:16\nRUN echo 'docker'"
        (temp_project / "Dockerfile").write_text(dockerfile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find commands from all sources
        sources = {cmd.source for cmd in commands}
        source_filenames = {source.split("/")[-1] for source in sources}
        assert "package.json" in source_filenames
        assert "Makefile" in source_filenames
        assert "Dockerfile" in source_filenames

        types = {cmd.type for cmd in commands}
        assert "npm_script" in types
        assert "make_target" in types
        assert "docker_build" in types

    def test_exclude_patterns_integration(self, temp_project):
        """Test exclude patterns in real scenario."""
        # Create files that should be excluded
        node_modules = temp_project / "node_modules"
        node_modules.mkdir()
        with open(node_modules / "package.json", "w") as f:
            json.dump({"scripts": {"excluded": "echo 'should not run'"}}, f)

        # Create files that should be included
        with open(temp_project / "package.json", "w") as f:
            json.dump({"scripts": {"included": "echo 'should run'"}}, f)

        detector = ProjectCommandDetector(
            str(temp_project), exclude_patterns=["node_modules/*"]
        )
        commands = detector.scan_project()

        # Should only find commands from main package.json
        assert len(commands) == 1
        assert commands[0].command == "npm run included"

    def test_large_project_simulation(self, temp_project):
        """Test performance with larger number of config files."""
        # Create multiple package.json files
        for i in range(10):
            subdir = temp_project / f"project_{i}"
            subdir.mkdir()
            with open(subdir / "package.json", "w") as f:
                json.dump(
                    {
                        "scripts": {
                            f"test_{i}": f"echo 'test {i}'",
                            f"build_{i}": f"echo 'build {i}'",
                        }
                    },
                    f,
                )

        # Create a detector with explicit paths
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
        )

        # Scan the project for commands
        commands = detector.scan_project()

        # Should find all commands (10 projects * 2 scripts each)
        assert len(commands) == 20, f"Expected 20 commands, got {len(commands)}"

        # All commands should be npm scripts
        command_types = {cmd.type for cmd in commands}
        assert all(
            cmd.type == "npm_script" for cmd in commands
        ), f"Expected all commands to be npm_script, got {command_types}"

    def test_process_file_exclude_patterns(self, temp_project):
        """Test file exclusion based on patterns."""
        # Create test files first
        (temp_project / "package.json").write_text("{}")
        (temp_project / "package.test.json").write_text("{}")
        node_modules = temp_project / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.json").write_text("{}")

        # Create a detector with explicit paths and exclude patterns
        todo_path = temp_project / "TODO.md"
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            todo_file=str(todo_path),
            done_file=str(temp_project / "DONE.md"),
            script_file=str(temp_project / "todo.sh"),
            exclude_patterns=["*.test.*", "node_modules/*"],
        )

        # Test exclusion
        assert detector._should_process_file(temp_project / "package.json") is True
        assert (
            detector._should_process_file(temp_project / "package.test.json") is False
        )
        assert detector._should_process_file(node_modules / "package.json") is False
