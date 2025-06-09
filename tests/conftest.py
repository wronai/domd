"""
pytest configuration and shared fixtures for DoMD tests.
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import pytest

from domd.core.detector import ProjectCommandDetector
from domd.core.parsers import (
    CargoTomlParser,
    ComposerJsonParser,
    DockerComposeParser,
    DockerfileParser,
    GoModParser,
    MakefileParser,
    PackageJsonParser,
    PyProjectTomlParser,
    ToxIniParser,
)
from domd.core.parsers.base import BaseParser

# Import test utilities
from tests.helpers.test_utils import (
    create_sample_cargo_toml,
    create_sample_composer_json,
    create_sample_docker_compose,
    create_sample_dockerfile,
    create_sample_makefile,
    create_sample_package_json,
    create_sample_pyproject_toml,
    create_sample_tox_ini,
)


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    yield temp_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_package_json() -> Dict[str, Any]:
    """Sample package.json content for testing."""
    return {
        "name": "test-project",
        "version": "1.0.0",
        "description": "Test project for DoMD",
        "scripts": {
            "test": "jest",
            "build": "webpack --mode production",
            "start": "node server.js",
            "lint": "eslint src/",
            "dev": "webpack-dev-server",
            "clean": "rm -rf dist/",
        },
        "devDependencies": {"jest": "^29.0.0", "webpack": "^5.0.0"},
    }


@pytest.fixture
def sample_makefile_content() -> str:
    """Sample Makefile content for testing."""
    return """# Test Makefile
.PHONY: all test build clean install

all: build test

test:
    pytest tests/

build:
    echo "Building..."

clean:
    rm -rf dist/ build/ *.egg-info/

install:
    pip install -e .
"""


@pytest.fixture
def populated_project(
    temp_project: Path,
) -> Path:
    """Create a fully populated test project with multiple config files."""
    # Create various config files using our test utilities
    create_sample_package_json(temp_project)
    create_sample_makefile(temp_project)
    create_sample_pyproject_toml(temp_project)
    create_sample_tox_ini(temp_project)
    create_sample_dockerfile(temp_project)
    create_sample_docker_compose(temp_project)
    create_sample_composer_json(temp_project)
    create_sample_cargo_toml(temp_project)

    return temp_project


@pytest.fixture
def detector_instance(temp_project: Path) -> ProjectCommandDetector:
    """Create a ProjectCommandDetector instance for testing."""
    return ProjectCommandDetector(
        project_path=str(temp_project),
        timeout=5,  # Short timeout for tests
        exclude_patterns=["__pycache__/*", "*.pyc"],
        include_patterns=[],
    )


@pytest.fixture
def mock_successful_command(monkeypatch):
    """Mock command execution to return successful CommandResult."""
    from domd.core.commands.executor import CommandResult

    def mock_execute(*args, **kwargs):
        return CommandResult(
            success=True,
            return_code=0,
            execution_time=0.01,
            output="Command executed successfully",
            error=None,
        )

    # Patch the CommandExecutor.execute method w obu możliwych ścieżkach
    monkeypatch.setattr("domd.core.detector.CommandExecutor.execute", mock_execute)
    monkeypatch.setattr("domd.command_execution.CommandExecutor.execute", mock_execute)
    monkeypatch.setattr(
        "domd.core.commands.executor.CommandExecutor.execute", mock_execute
    )


@pytest.fixture
def mock_failed_command(monkeypatch):
    """Mock command execution to return failed CommandResult."""
    from domd.core.commands.executor import CommandResult

    def mock_execute(*args, **kwargs):
        return CommandResult(
            success=False,
            return_code=1,
            execution_time=0.01,
            output="",
            error="Command failed",
        )

    # Patch the CommandExecutor.execute method
    monkeypatch.setattr("domd.core.detector.CommandExecutor.execute", mock_execute)


@pytest.fixture
def mock_timeout_command(monkeypatch):
    """Mock command execution to simulate a timeout."""
    import subprocess

    def mock_execute(*args, **kwargs):
        # Create a TimeoutExpired exception with the timeout value
        timeout = kwargs.get("timeout", 1)
        cmd = args[0] if args else ""
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

    # Patch the CommandExecutor.execute method
    monkeypatch.setattr("domd.core.detector.CommandExecutor.execute", mock_execute)


@pytest.fixture
def sample_failed_commands() -> list:
    """Sample failed commands for testing reporters."""
    return [
        {
            "command": "npm run test",
            "description": "NPM script: test",
            "source": "package.json",
            "type": "npm_script",
            "return_code": 1,
            "execution_time": 2.34,
            "error": "Error: Cannot find module 'jest'\nnpm ERR! missing script: test",
            "original_command": "jest",
        },
        {
            "command": "make build",
            "description": "Make target: build",
            "source": "Makefile",
            "type": "make_target",
            "return_code": 2,
            "execution_time": 0.12,
            "error": "make: *** No rule to make target 'src/main.c', needed by 'build'. Stop.",
        },
        {
            "command": "docker build -t test .",
            "description": "Build Docker image",
            "source": "Dockerfile",
            "type": "docker_build",
            "return_code": 1,
            "execution_time": 15.67,
            "error": "Error response from daemon: Cannot locate specified Dockerfile: Dockerfile",
        },
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "commands: mark test as command-related")
    config.addinivalue_line("markers", "parsers: mark test as parser-related")
    config.addinivalue_line("markers", "reporters: mark test as reporter-related")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add unit marker to most tests by default
        if "integration" not in item.keywords and "slow" not in item.keywords:
            item.add_marker(pytest.mark.unit)

        # Add markers based on file path
        if "test_parsers" in str(item.fspath):
            item.add_marker(pytest.mark.parsers)
        elif "test_reporters" in str(item.fspath):
            item.add_marker(pytest.mark.reporters)
        elif "test_commands" in str(item.fspath) or "test_detector" in str(item.fspath):
            item.add_marker(pytest.mark.commands)


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup temporary files after each test."""
    yield
    # Cleanup code could go here if needed
    pass


# Parser fixtures for testing
@pytest.fixture
def available_parsers() -> List[BaseParser]:
    """Return a list of all available parser instances."""
    return [
        CargoTomlParser(),
        ComposerJsonParser(),
        DockerComposeParser(),
        DockerfileParser(),
        GoModParser(),
        MakefileParser(),
        PackageJsonParser(),
        PyProjectTomlParser(),
        ToxIniParser(),
    ]


@pytest.fixture
def parser_factory():
    """Factory fixture to create parser instances by type."""

    def _create_parser(parser_type: str, **kwargs) -> Optional[BaseParser]:
        parsers = {
            "cargo_toml": CargoTomlParser,
            "composer_json": ComposerJsonParser,
            "docker_compose": DockerComposeParser,
            "dockerfile": DockerfileParser,
            "go_mod": GoModParser,
            "makefile": MakefileParser,
            "package_json": PackageJsonParser,
            "pyproject_toml": PyProjectTomlParser,
            "tox_ini": ToxIniParser,
        }

        parser_class = parsers.get(parser_type)
        if not parser_class:
            return None

        return parser_class(**kwargs)

    return _create_parser


# Helper functions for tests
def create_test_file(directory: Path, filename: str, content: str) -> Path:
    """Helper function to create test files."""
    file_path = directory / filename
    file_path.write_text(content)
    return file_path


def create_test_json_file(directory: Path, filename: str, data: dict) -> Path:
    """Helper function to create test JSON files."""
    file_path = directory / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    return file_path
