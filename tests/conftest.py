"""
pytest configuration and shared fixtures for DoMD tests.
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

from domd.core.detector import ProjectCommandDetector


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
\techo "Running tests..."
\tpython -m pytest

build:
\techo "Building project..."
\tmkdir -p dist
\tcp src/* dist/

clean:
\techo "Cleaning..."
\trm -rf dist/

install:
\techo "Installing dependencies..."
\tpip install -r requirements.txt

deploy: build
\techo "Deploying..."
\t./deploy.sh

# This target should be ignored
.PHONY: help
help:
\techo "Available targets: all, test, build, clean, install, deploy"
"""


@pytest.fixture
def sample_pyproject_toml() -> Dict[str, Any]:
    """Sample pyproject.toml content for testing."""
    return {
        "tool": {
            "poetry": {
                "name": "test-project",
                "version": "0.1.0",
                "description": "Test project",
                "scripts": {
                    "test": "pytest",
                    "lint": "flake8 src/",
                    "format": "black src/",
                    "start": "python -m test_project",
                },
            },
            "pytest": {
                "ini_options": {"testpaths": ["tests"], "python_files": ["test_*.py"]}
            },
            "black": {"line-length": 88, "target-version": ["py38"]},
            "isort": {"profile": "black"},
        }
    }


@pytest.fixture
def sample_tox_ini_content() -> str:
    """Sample tox.ini content for testing."""
    return """[tox]
envlist = py38,py39,py310,lint,docs

[testenv]
deps = pytest
       pytest-cov
commands = pytest

[testenv:lint]
deps = flake8
       black
       isort
commands =
    flake8 src/
    black --check src/
    isort --check-only src/

[testenv:docs]
deps = mkdocs
       mkdocs-material
commands = mkdocs build

[testenv:py38]
basepython = python3.8

[testenv:py39]
basepython = python3.9

[testenv:py310]
basepython = python3.10
"""


@pytest.fixture
def sample_dockerfile_content() -> str:
    """Sample Dockerfile content for testing."""
    return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
"""


@pytest.fixture
def sample_docker_compose_content() -> str:
    """Sample docker-compose.yml content for testing."""
    return """version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""


@pytest.fixture
def sample_composer_json() -> Dict[str, Any]:
    """Sample composer.json content for testing."""
    return {
        "name": "test/project",
        "description": "Test PHP project",
        "type": "project",
        "require": {"php": "^8.0"},
        "require-dev": {"phpunit/phpunit": "^9.0"},
        "scripts": {
            "test": "phpunit",
            "lint": "php-cs-fixer fix --dry-run",
            "fix": "php-cs-fixer fix",
            "static": "phpstan analyse",
        },
        "autoload": {"psr-4": {"Test\\": "src/"}},
    }


@pytest.fixture
def sample_cargo_toml() -> str:
    """Sample Cargo.toml content for testing."""
    return """[package]
name = "test-project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
criterion = "0.4"

[[bin]]
name = "main"
path = "src/main.rs"

[[bench]]
name = "benchmarks"
harness = false
"""


@pytest.fixture
def populated_project(
    temp_project: Path,
    sample_package_json: Dict[str, Any],
    sample_makefile_content: str,
    sample_pyproject_toml: Dict[str, Any],
) -> Path:
    """Create a fully populated test project with multiple config files."""

    # Create package.json
    with open(temp_project / "package.json", "w") as f:
        json.dump(sample_package_json, f, indent=2)

    # Create Makefile
    with open(temp_project / "Makefile", "w") as f:
        f.write(sample_makefile_content)

    # Create pyproject.toml
    import toml

    with open(temp_project / "pyproject.toml", "w") as f:
        toml.dump(sample_pyproject_toml, f)

    # Create some source files
    src_dir = temp_project / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('Hello, World!')")
    (src_dir / "app.js").write_text("console.log('Hello, World!');")

    # Create requirements.txt
    (temp_project / "requirements.txt").write_text("pytest>=7.0\nblack>=22.0\n")

    # Create tests directory
    tests_dir = temp_project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").write_text(
        """
def test_example():
    assert True
"""
    )

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
    """Mock subprocess.run to return successful command execution."""
    import subprocess
    from unittest.mock import Mock

    def mock_run(*args, **kwargs):
        result = Mock()
        result.returncode = 0
        result.stdout = "Command executed successfully"
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_failed_command(monkeypatch):
    """Mock subprocess.run to return failed command execution."""
    import subprocess
    from unittest.mock import Mock

    def mock_run(*args, **kwargs):
        result = Mock()
        result.returncode = 1
        result.stdout = ""
        result.stderr = "Command failed with error"
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_timeout_command(monkeypatch):
    """Mock subprocess.run to raise TimeoutExpired."""
    import subprocess

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("test_command", 5)

    monkeypatch.setattr(subprocess, "run", mock_run)


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
