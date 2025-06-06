"""
Tests for the main ProjectCommandDetector class.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from todomd.detector import ProjectCommandDetector


class TestProjectCommandDetector:
    """Test cases for ProjectCommandDetector class."""

    @pytest.mark.unit
    def test_detector_initialization(self, temp_project):
        """Test detector initialization with various parameters."""
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            timeout=30,
            exclude_patterns=["*.pyc"],
            include_patterns=["Makefile"]
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
        with open(package_json_path, 'w') as f:
            json.dump(sample_package_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find npm scripts
        assert len(commands) > 0
        npm_commands = [cmd for cmd in commands if cmd['type'] == 'npm_script']
        assert len(npm_commands) == len(sample_package_json['scripts'])

        # Check specific commands
        test_command = next((cmd for cmd in npm_commands if 'test' in cmd['command']), None)
        assert test_command is not None
        assert test_command['command'] == 'npm run test'
        assert test_command['description'] == 'NPM script: test'
        assert test_command['source'] == 'package.json'

    @pytest.mark.unit
    def test_scan_project_with_makefile(self, temp_project, sample_makefile_content):
        """Test scanning a project with Makefile."""
        # Create Makefile
        makefile_path = temp_project / "Makefile"
        makefile_path.write_text(sample_makefile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find make targets
        make_commands = [cmd for cmd in commands if cmd['type'] == 'make_target']
        assert len(make_commands) > 0

        # Check for specific targets
        target_names = [cmd['command'].split()[-1] for cmd in make_commands]
        expected_targets = ['all', 'test', 'build', 'clean', 'install', 'deploy']

        for target in expected_targets:
            assert f'make {target}' in [cmd['command'] for cmd in make_commands]

    @pytest.mark.unit
    def test_scan_project_with_pyproject_toml(self, temp_project, sample_pyproject_toml):
        """Test scanning a project with pyproject.toml."""
        import toml

        # Create pyproject.toml
        pyproject_path = temp_project / "pyproject.toml"
        with open(pyproject_path, 'w') as f:
            toml.dump(sample_pyproject_toml, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find poetry scripts and tool commands
        poetry_commands = [cmd for cmd in commands if cmd['type'] == 'poetry_script']
        pytest_commands = [cmd for cmd in commands if cmd['type'] == 'pytest']

        assert len(poetry_commands) > 0
        assert len(pytest_commands) > 0

        # Check specific commands
        scripts = sample_pyproject_toml['tool']['poetry']['scripts']
        for script_name in scripts:
            script_command = next((cmd for cmd in poetry_commands if script_name in cmd['command']), None)
            assert script_command is not None

    @pytest.mark.unit
    def test_should_process_file_include_patterns(self, temp_project):
        """Test file inclusion based on patterns."""
        detector = ProjectCommandDetector(
            str(temp_project),
            include_patterns=["Makefile", "package.json"]
        )

        # Create test files
        (temp_project / "package.json").write_text('{}')
        (temp_project / "Makefile").write_text('')
        (temp_project / "pyproject.toml").write_text('')

        # Test inclusion
        assert detector._should_process_file(temp_project / "package.json") == True
        assert detector._should_process_file(temp_project / "Makefile") == True
        assert detector._should_process_file(temp_project / "pyproject.toml") == False

    @pytest.mark.unit
    def test_execute_command_success(self, temp_project, mock_successful_command):
        """Test successful command execution."""
        detector = ProjectCommandDetector(str(temp_project))

        cmd_info = {
            'command': 'echo "test"',
            'description': 'Test command',
            'source': 'test',
            'type': 'test'
        }

        result = detector._execute_command(cmd_info)

        assert result == True
        assert 'execution_time' in cmd_info
        assert 'error' not in cmd_info

    @pytest.mark.unit
    def test_execute_command_failure(self, temp_project, mock_failed_command):
        """Test failed command execution."""
        detector = ProjectCommandDetector(str(temp_project))

        cmd_info = {
            'command': 'false',
            'description': 'Failing command',
            'source': 'test',
            'type': 'test'
        }

        result = detector._execute_command(cmd_info)

        assert result == False
        assert 'error' in cmd_info
        assert 'return_code' in cmd_info
        assert cmd_info['return_code'] == 1

    @pytest.mark.unit
    def test_execute_command_timeout(self, temp_project, mock_timeout_command):
        """Test command execution timeout."""
        detector = ProjectCommandDetector(str(temp_project), timeout=1)

        cmd_info = {
            'command': 'sleep 10',
            'description': 'Long running command',
            'source': 'test',
            'type': 'test'
        }

        result = detector._execute_command(cmd_info)

        assert result == False
        assert 'error' in cmd_info
        assert 'return_code' in cmd_info
        assert cmd_info['return_code'] == -1
        assert 'timed out' in cmd_info['error']

    @pytest.mark.unit
    def test_test_commands(self, temp_project, mock_successful_command):
        """Test testing multiple commands."""
        detector = ProjectCommandDetector(str(temp_project))

        commands = [
            {
                'command': 'echo "test1"',
                'description': 'Test command 1',
                'source': 'test',
                'type': 'test'
            },
            {
                'command': 'echo "test2"',
                'description': 'Test command 2',
                'source': 'test',
                'type': 'test'
            }
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
                'command': 'false',
                'description': 'Failing command',
                'source': 'test',
                'type': 'test'
            }
        ]

        detector.test_commands(commands)

        # Command should fail with mocked failure
        assert len(detector.failed_commands) == 1
        assert detector.failed_commands[0]['command'] == 'false'

    @pytest.mark.unit
    def test_generate_markdown_report(self, temp_project, sample_failed_commands):
        """Test markdown report generation."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        markdown_content = detector._generate_markdown_report()

        assert "# TODO - Failed Project Commands" in markdown_content
        assert "npm run test" in markdown_content
        assert "make build" in markdown_content
        assert "docker build" in markdown_content
        assert "Return Code:" in markdown_content
        assert "### Suggested Actions:" in markdown_content

    @pytest.mark.unit
    def test_generate_json_report(self, temp_project, sample_failed_commands):
        """Test JSON report generation."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        json_content = detector._generate_json_report()
        data = json.loads(json_content)

        assert "generated_at" in data
        assert "project_path" in data
        assert "total_failed" in data
        assert "failed_commands" in data
        assert data["total_failed"] == len(sample_failed_commands)
        assert len(data["failed_commands"]) == len(sample_failed_commands)

    @pytest.mark.unit
    def test_generate_text_report(self, temp_project, sample_failed_commands):
        """Test text report generation."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        text_content = detector._generate_text_report()

        assert "TODO - Failed Project Commands" in text_content
        assert "npm run test" in text_content
        assert "make build" in text_content
        assert "docker build" in text_content
        assert f"Failed Commands: {len(sample_failed_commands)}" in text_content

    @pytest.mark.unit
    def test_generate_output_file_markdown(self, temp_project, sample_failed_commands):
        """Test generating markdown output file."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        output_path = temp_project / "test_output.md"
        detector.generate_output_file(str(output_path), "markdown")

        assert output_path.exists()
        content = output_path.read_text()
        assert "# TODO - Failed Project Commands" in content

    @pytest.mark.unit
    def test_generate_output_file_json(self, temp_project, sample_failed_commands):
        """Test generating JSON output file."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        output_path = temp_project / "test_output.json"
        detector.generate_output_file(str(output_path), "json")

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "failed_commands" in data

    @pytest.mark.unit
    def test_generate_output_file_no_failures(self, temp_project):
        """Test output file generation when no failures."""
        detector = ProjectCommandDetector(str(temp_project))

        output_path = temp_project / "test_output.md"
        detector.generate_output_file(str(output_path), "markdown")

        # Should not create file when no failures
        assert not output_path.exists()

    @pytest.mark.unit
    def test_get_statistics(self, temp_project, sample_failed_commands):
        """Test statistics generation."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        stats = detector.get_statistics()

        assert "total_commands" in stats
        assert "successful_commands" in stats
        assert "failed_commands" in stats
        assert "success_rate" in stats
        assert "failure_rate" in stats
        assert "failure_by_type" in stats
        assert "failure_by_source" in stats
        assert "project_path" in stats
        assert "timeout_setting" in stats

        assert stats["failed_commands"] == len(sample_failed_commands)
        assert "npm_script" in stats["failure_by_type"]
        assert "make_target" in stats["failure_by_type"]

    @pytest.mark.unit
    def test_export_results(self, temp_project, sample_failed_commands):
        """Test exporting detailed results to JSON."""
        detector = ProjectCommandDetector(str(temp_project))
        detector.failed_commands = sample_failed_commands

        output_path = temp_project / "results.json"
        detector.export_results(str(output_path))

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)

        assert "metadata" in data
        assert "statistics" in data
        assert "failed_commands" in data
        assert data["metadata"]["project_path"] == str(temp_project)

    @pytest.mark.integration
    def test_full_workflow_populated_project(self, populated_project):
        """Test complete workflow on a populated project."""
        detector = ProjectCommandDetector(str(populated_project))

        # Scan project
        commands = detector.scan_project()
        assert len(commands) > 0

        # Should find commands from different sources
        sources = {cmd['source'] for cmd in commands}
        assert 'package.json' in sources
        assert 'Makefile' in sources
        assert 'pyproject.toml' in sources

        # Test commands (will fail in test environment, but that's expected)
        with patch('subprocess.run') as mock_run:
            # Mock some successes and some failures
            def side_effect(*args, **kwargs):
                result = Mock()
                if 'echo' in args[0]:
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

        # Generate reports
        output_path = populated_project / "TODO.md"
        detector.generate_output_file(str(output_path), "markdown")

        # Verify statistics
        stats = detector.get_statistics()
        assert stats["total_commands"] == len(commands)


class TestParserMethods:
    """Test individual parser methods."""

    @pytest.mark.parsers
    def test_parse_package_json_with_scripts(self, temp_project, sample_package_json):
        """Test parsing package.json with scripts."""
        package_json_path = temp_project / "package.json"
        with open(package_json_path, 'w') as f:
            json.dump(sample_package_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_package_json(package_json_path)

        assert len(commands) == len(sample_package_json['scripts'])

        for script_name in sample_package_json['scripts']:
            script_command = next((cmd for cmd in commands if script_name in cmd['command']), None)
            assert script_command is not None
            assert script_command['type'] == 'npm_script'
            assert script_command['source'] == 'package.json'

    @pytest.mark.parsers
    def test_parse_package_json_no_scripts(self, temp_project):
        """Test parsing package.json without scripts."""
        package_json_data = {"name": "test", "version": "1.0.0"}
        package_json_path = temp_project / "package.json"
        with open(package_json_path, 'w') as f:
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
        target_commands = [cmd['command'] for cmd in commands]
        assert 'make all' in target_commands
        assert 'make test' in target_commands
        assert 'make build' in target_commands
        assert 'make clean' in target_commands
        assert 'make install' in target_commands
        assert 'make deploy' in target_commands

        # Should not include special targets
        assert 'make .PHONY' not in target_commands
        assert 'make PHONY' not in target_commands

    @pytest.mark.parsers
    def test_parse_pyproject_toml_with_poetry_scripts(self, temp_project, sample_pyproject_toml):
        """Test parsing pyproject.toml with Poetry scripts."""
        import toml

        pyproject_path = temp_project / "pyproject.toml"
        with open(pyproject_path, 'w') as f:
            toml.dump(sample_pyproject_toml, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_pyproject_toml(pyproject_path)

        # Should find Poetry scripts
        poetry_commands = [cmd for cmd in commands if cmd['type'] == 'poetry_script']
        scripts = sample_pyproject_toml['tool']['poetry']['scripts']
        assert len(poetry_commands) == len(scripts)

        # Should also find pytest configuration
        pytest_commands = [cmd for cmd in commands if cmd['type'] == 'pytest']
        assert len(pytest_commands) > 0

    @pytest.mark.parsers
    def test_parse_tox_ini(self, temp_project, sample_tox_ini_content):
        """Test parsing tox.ini."""
        tox_ini_path = temp_project / "tox.ini"
        tox_ini_path.write_text(sample_tox_ini_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_tox_ini(tox_ini_path)

        # Should find individual environments and general tox command
        tox_commands = [cmd['command'] for cmd in commands]
        assert 'tox -e py38' in tox_commands
        assert 'tox -e py39' in tox_commands
        assert 'tox -e py310' in tox_commands
        assert 'tox -e lint' in tox_commands
        assert 'tox -e docs' in tox_commands
        assert 'tox' in tox_commands

    @pytest.mark.parsers
    def test_parse_dockerfile(self, temp_project, sample_dockerfile_content):
        """Test parsing Dockerfile."""
        dockerfile_path = temp_project / "Dockerfile"
        dockerfile_path.write_text(sample_dockerfile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_dockerfile(dockerfile_path)

        assert len(commands) == 1
        assert commands[0]['type'] == 'docker_build'
        assert 'docker build' in commands[0]['command']
        assert commands[0]['source'] == 'Dockerfile'

    @pytest.mark.parsers
    def test_parse_docker_compose(self, temp_project, sample_docker_compose_content):
        """Test parsing docker-compose.yml."""
        compose_path = temp_project / "docker-compose.yml"
        compose_path.write_text(sample_docker_compose_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_docker_compose(compose_path)

        assert len(commands) == 2

        up_command = next((cmd for cmd in commands if 'up' in cmd['command']), None)
        assert up_command is not None
        assert up_command['type'] == 'docker_compose_up'

        down_command = next((cmd for cmd in commands if 'down' in cmd['command']), None)
        assert down_command is not None
        assert down_command['type'] == 'docker_compose_down'

    @pytest.mark.parsers
    def test_parse_composer_json(self, temp_project, sample_composer_json):
        """Test parsing composer.json."""
        composer_path = temp_project / "composer.json"
        with open(composer_path, 'w') as f:
            json.dump(sample_composer_json, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector._parse_composer_json(composer_path)

        # Should find install command and script commands
        command_types = [cmd['type'] for cmd in commands]
        assert 'composer_install' in command_types
        assert 'composer_script' in command_types

        # Check specific scripts
        script_commands = [cmd for cmd in commands if cmd['type'] == 'composer_script']
        script_names = [cmd['command'].split()[-1] for cmd in script_commands]
        expected_scripts = list(sample_composer_json['scripts'].keys())

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
        command_types = [cmd['type'] for cmd in commands]
        assert 'cargo_build' in command_types
        assert 'cargo_test' in command_types
        assert 'cargo_check' in command_types

        assert len(commands) == 3


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration test scenarios."""

    def test_mixed_project_types(self, temp_project):
        """Test project with multiple configuration file types."""
        # Create multiple config files
        package_json = {"scripts": {"test": "jest", "build": "webpack"}}
        with open(temp_project / "package.json", 'w') as f:
            json.dump(package_json, f)

        makefile_content = "test:\n\techo 'testing'\nbuild:\n\techo 'building'"
        (temp_project / "Makefile").write_text(makefile_content)

        dockerfile_content = "FROM node:16\nRUN echo 'docker'"
        (temp_project / "Dockerfile").write_text(dockerfile_content)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find commands from all sources
        sources = {cmd['source'] for cmd in commands}
        assert 'package.json' in sources
        assert 'Makefile' in sources
        assert 'Dockerfile' in sources

        types = {cmd['type'] for cmd in commands}
        assert 'npm_script' in types
        assert 'make_target' in types
        assert 'docker_build' in types

    def test_exclude_patterns_integration(self, temp_project):
        """Test exclude patterns in real scenario."""
        # Create files that should be excluded
        node_modules = temp_project / "node_modules"
        node_modules.mkdir()
        with open(node_modules / "package.json", 'w') as f:
            json.dump({"scripts": {"excluded": "echo 'should not run'"}}, f)

        # Create files that should be included
        with open(temp_project / "package.json", 'w') as f:
            json.dump({"scripts": {"included": "echo 'should run'"}}, f)

        detector = ProjectCommandDetector(
            str(temp_project),
            exclude_patterns=["node_modules/*"]
        )
        commands = detector.scan_project()

        # Should only find commands from main package.json
        assert len(commands) == 1
        assert commands[0]['command'] == 'npm run included'

    def test_large_project_simulation(self, temp_project):
        """Test performance with larger number of config files."""
        # Create multiple package.json files
        for i in range(10):
            subdir = temp_project / f"project_{i}"
            subdir.mkdir()
            with open(subdir / "package.json", 'w') as f:
                json.dump({
                    "scripts": {
                        f"test_{i}": f"echo 'test {i}'",
                        f"build_{i}": f"echo 'build {i}'"
                    }
                }, f)

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should find all commands
        assert len(commands) == 20  # 10 projects * 2 scripts each

        # All commands should be npm scripts
        assert all(cmd['type'] == 'npm_script' for cmd in commands)process_file_exclude_patterns(self, temp_project):
        """Test file exclusion based on patterns."""
        detector = ProjectCommandDetector(
            str(temp_project),
            exclude_patterns=["*.test.*", "node_modules/*"]
        )

        # Create test files
        (temp_project / "package.json").write_text('{}')
        (temp_project / "package.test.json").write_text('{}')
        node_modules = temp_project / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.json").write_text('{}')

        # Test exclusion
        assert detector._should_process_file(temp_project / "package.json") == True
        assert detector._should_process_file(temp_project / "package.test.json") == False
        assert detector._should_process_file(node_modules / "package.json") == False

