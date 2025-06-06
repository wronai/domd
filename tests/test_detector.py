"""
Tests for the main ProjectCommandDetector class.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from domd.core.detector import ProjectCommandDetector


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
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        assert commands == []

    @pytest.mark.unit
    def test_scan_project_with_package_json(self, temp_project, sample_package_json):
        """Test scanning a project with package.json."""
        # Create package.json
        package_json_path = temp_project / "package.json"
        with open(package_json_path, "w") as f:
            json.dump(sample_package_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find npm scripts
        assert len(commands) > 0
        npm_commands = [cmd for cmd in commands if cmd["type"] == "npm_script"]
        assert len(npm_commands) == len(sample_package_json["scripts"])

        # Check specific commands
        test_command = next(
            (cmd for cmd in npm_commands if "test" in cmd["command"]), None
        )
        assert test_command is not None
        assert test_command["command"] == "npm run test"
        assert test_command["description"] == "NPM script: test"
        assert test_command["source"] == "package.json"

    @pytest.mark.unit
    def test_scan_project_with_makefile(self, temp_project, sample_makefile_content):
        """Test scanning a project with Makefile."""
        # Create Makefile
        makefile_path = temp_project / "Makefile"
        makefile_path.write_text(sample_makefile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find make targets
        make_commands = [cmd for cmd in commands if cmd["type"] == "make_target"]
        assert len(make_commands) > 0

        # Check for specific targets
        expected_targets = ["all", "test", "build", "clean", "install", "deploy"]

        for target in expected_targets:
            assert f"make {target}" in [cmd["command"] for cmd in make_commands]

    @pytest.mark.unit
    def test_scan_project_with_pyproject_toml(
        self, temp_project, sample_pyproject_toml
    ):
        """Test scanning a project with pyproject.toml."""
        import toml

        # Create pyproject.toml
        pyproject_path = temp_project / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            toml.dump(sample_pyproject_toml, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find poetry scripts and tool commands
        poetry_commands = [cmd for cmd in commands if cmd["type"] == "poetry_script"]
        pytest_commands = [cmd for cmd in commands if cmd["type"] == "pytest"]

        assert len(poetry_commands) > 0
        assert len(pytest_commands) > 0

        # Check specific commands
        scripts = sample_pyproject_toml["tool"]["poetry"]["scripts"]
        for script_name in scripts:
            script_command = next(
                (cmd for cmd in poetry_commands if script_name in cmd["command"]), None
            )
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
        assert "timed out" in cmd_info["error"]

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
        sources = {cmd["source"] for cmd in commands}
        assert "package.json" in sources
        assert "Makefile" in sources
        assert "pyproject.toml" in sources

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
            if cmd.get("error"):
                cmd_str = f"`{cmd['command']}`"
                if cmd_str not in content:
                    print(f"\nCommand not found in TODO.md: {cmd_str}")
                    print("\nTODO.md content:")
                    print("-" * 80)
                    print(content)
                    print("-" * 80)
                assert (
                    cmd_str in content
                ), f"Command '{cmd['command']}' not found in TODO.md"


class TestParserMethods:
    """Test individual parser methods."""

    @pytest.mark.parsers
    def test_parse_package_json_with_scripts(self, temp_project, sample_package_json):
        """Test parsing package.json with scripts."""
        package_json_path = temp_project / "package.json"
        with open(package_json_path, "w") as f:
            json.dump(sample_package_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_package_json(package_json_path)

        assert len(commands) == len(sample_package_json["scripts"])

        for script_name in sample_package_json["scripts"]:
            script_command = next(
                (cmd for cmd in commands if script_name in cmd["command"]), None
            )
            assert script_command is not None
            assert script_command["type"] == "npm_script"
            assert script_command["source"] == "package.json"

    @pytest.mark.parsers
    def test_parse_package_json_no_scripts(self, temp_project):
        """Test parsing package.json without scripts."""
        package_json_data = {"name": "test", "version": "1.0.0"}
        package_json_path = temp_project / "package.json"
        with open(package_json_path, "w") as f:
            json.dump(package_json_data, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_package_json(package_json_path)

        assert commands == []

    @pytest.mark.parsers
    def test_parse_makefile_with_targets(self, temp_project, sample_makefile_content):
        """Test parsing Makefile with targets."""
        makefile_path = temp_project / "Makefile"
        makefile_path.write_text(sample_makefile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_makefile(makefile_path)

        # Should find specific targets but not .PHONY
        target_commands = [cmd["command"] for cmd in commands]
        assert "make all" in target_commands
        assert "make test" in target_commands
        assert "make build" in target_commands
        assert "make clean" in target_commands
        assert "make install" in target_commands
        assert "make deploy" in target_commands

        # Should not include special targets
        assert "make .PHONY" not in target_commands
        assert "make PHONY" not in target_commands

    @pytest.mark.parsers
    def test_parse_pyproject_toml_with_poetry_scripts(
        self, temp_project, sample_pyproject_toml
    ):
        """Test parsing pyproject.toml with Poetry scripts."""
        import toml

        pyproject_path = temp_project / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            toml.dump(sample_pyproject_toml, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_pyproject_toml(pyproject_path)

        # Should find Poetry scripts
        poetry_commands = [cmd for cmd in commands if cmd["type"] == "poetry_script"]
        scripts = sample_pyproject_toml["tool"]["poetry"]["scripts"]
        assert len(poetry_commands) == len(scripts)

        # Should also find pytest configuration
        pytest_commands = [cmd for cmd in commands if cmd["type"] == "pytest"]
        assert len(pytest_commands) > 0

    @pytest.mark.parsers
    def test_parse_tox_ini(self, temp_project, sample_tox_ini_content):
        """Test parsing tox.ini."""
        tox_ini_path = temp_project / "tox.ini"
        tox_ini_path.write_text(sample_tox_ini_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_tox_ini(tox_ini_path)

        # Should find individual environments and general tox command
        tox_commands = [cmd["command"] for cmd in commands]
        assert "tox -e py38" in tox_commands
        assert "tox -e py39" in tox_commands
        assert "tox -e py310" in tox_commands
        assert "tox -e lint" in tox_commands
        assert "tox -e docs" in tox_commands
        assert "tox" in tox_commands

    @pytest.mark.parsers
    def test_parse_dockerfile(self, temp_project, sample_dockerfile_content):
        """Test parsing Dockerfile."""
        dockerfile_path = temp_project / "Dockerfile"
        dockerfile_path.write_text(sample_dockerfile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_dockerfile(dockerfile_path)

        assert len(commands) == 1
        assert commands[0]["type"] == "docker_build"
        assert "docker build" in commands[0]["command"]
        assert commands[0]["source"] == "Dockerfile"

    @pytest.mark.parsers
    def test_parse_docker_compose(self, temp_project, sample_docker_compose_content):
        """Test parsing docker-compose.yml."""
        compose_path = temp_project / "docker-compose.yml"
        compose_path.write_text(sample_docker_compose_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_docker_compose(compose_path)

        assert len(commands) == 2

        up_command = next((cmd for cmd in commands if "up" in cmd["command"]), None)
        assert up_command is not None
        assert up_command["type"] == "docker_compose_up"

        down_command = next((cmd for cmd in commands if "down" in cmd["command"]), None)
        assert down_command is not None
        assert down_command["type"] == "docker_compose_down"

    @pytest.mark.parsers
    def test_parse_composer_json(self, temp_project, sample_composer_json):
        """Test parsing composer.json."""
        composer_path = temp_project / "composer.json"
        with open(composer_path, "w") as f:
            json.dump(sample_composer_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_composer_json(composer_path)

        # Should find install command and script commands
        command_types = [cmd["type"] for cmd in commands]
        assert "composer_install" in command_types
        assert "composer_script" in command_types

        # Check specific scripts
        script_commands = [cmd for cmd in commands if cmd["type"] == "composer_script"]
        script_names = [cmd["command"].split()[-1] for cmd in script_commands]
        expected_scripts = list(sample_composer_json["scripts"].keys())

        for script in expected_scripts:
            assert script in script_names

    @pytest.mark.parsers
    def test_parse_cargo_toml(self, temp_project, sample_cargo_toml):
        """Test parsing Cargo.toml."""
        cargo_path = temp_project / "Cargo.toml"
        cargo_path.write_text(sample_cargo_toml)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_cargo_toml(cargo_path)

        # Should find build, test, and check commands
        command_types = [cmd["type"] for cmd in commands]
        assert "cargo_build" in command_types
        assert "cargo_test" in command_types
        assert "cargo_check" in command_types

        assert len(commands) == 3


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
        sources = {cmd["source"] for cmd in commands}
        assert "package.json" in sources
        assert "Makefile" in sources
        assert "Dockerfile" in sources

        types = {cmd["type"] for cmd in commands}
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
        assert commands[0]["command"] == "npm run included"

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
        assert all(
            cmd["type"] == "npm_script" for cmd in commands
        ), f"Expected all commands to be npm_script, got {set(cmd['type'] for cmd in commands)}"

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
