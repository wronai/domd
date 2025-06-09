"""Test utilities for DOMD project."""

import json
from pathlib import Path
from typing import Any, Dict, Union


def create_test_file(
    directory: Union[str, Path],
    filename: str,
    content: Union[str, Dict[str, Any], None] = None,
) -> Path:
    """Create a test file with the given content.

    Args:
        directory: Directory where the file should be created
        filename: Name of the file to create
        content: Content to write to the file (string or dict for JSON/TOML)

    Returns:
        Path to the created file
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    file_path = directory / filename

    if content is None:
        file_path.touch()
    elif isinstance(content, dict):
        if filename.endswith(".json"):
            file_path.write_text(json.dumps(content, indent=2))
        elif filename.endswith(".toml"):
            import toml

            file_path.write_text(toml.dumps(content))
        else:
            file_path.write_text(str(content))
    else:
        file_path.write_text(str(content))

    return file_path


def create_sample_package_json(directory: Union[str, Path]) -> Path:
    """Create a sample package.json file for testing."""
    content = {
        "name": "test-package",
        "version": "1.0.0",
        "scripts": {
            "test": "jest",
            "build": "webpack",
            "start": "node index.js",
            "lint": "eslint .",
        },
    }
    return create_test_file(directory, "package.json", content)


def create_sample_makefile(directory: Union[str, Path]) -> Path:
    """Create a sample Makefile for testing."""
    content = """
.PHONY: all test build clean install deploy

all: test build

test:
    pytest tests/

build:
    echo "Building..."

clean:
    rm -rf build/ dist/ *.egg-info/

install:
    pip install -e .

deploy:
    scp -r * user@example.com:/var/www/app/
"""
    return create_test_file(directory, "Makefile", content)


def create_sample_pyproject_toml(directory: Union[str, Path]) -> Path:
    """Create a sample pyproject.toml file for testing."""
    content = {
        "tool": {
            "poetry": {
                "name": "test-package",
                "version": "0.1.0",
                "scripts": {"test": "pytest", "lint": "black . && isort . && flake8"},
            },
            "pytest": {
                "ini_options": {"testpaths": "tests", "python_files": "test_*.py"}
            },
        }
    }
    return create_test_file(directory, "pyproject.toml", content)


def create_sample_tox_ini(directory: Union[str, Path]) -> Path:
    """Create a sample tox.ini file for testing."""
    content = """
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
    return create_test_file(directory, "tox.ini", content)


def create_sample_dockerfile(directory: Union[str, Path]) -> Path:
    """Create a sample Dockerfile for testing."""
    content = """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
"""
    return create_test_file(directory, "Dockerfile", content)


def create_sample_docker_compose(directory: Union[str, Path]) -> Path:
    """Create a sample docker-compose.yml for testing."""
    content = {
        "version": "3.8",
        "services": {
            "web": {
                "build": ".",
                "ports": ["5000:5000"],
                "volumes": [".:/app"],
                "environment": {"FLASK_ENV": "development", "FLASK_APP": "app.py"},
            },
            "redis": {"image": "redis:alpine", "ports": ["6379:6379"]},
        },
    }
    return create_test_file(directory, "docker-compose.yml", content)


def create_sample_cargo_toml(directory: Union[str, Path]) -> Path:
    """Create a sample Cargo.toml for testing."""
    content = {
        "package": {"name": "test-package", "version": "0.1.0", "edition": "2021"},
        "dependencies": {
            "clap": {"version": "3.0", "features": ["derive"]},
            "tokio": {"version": "1.0", "features": ["full"]},
        },
        "bin": [{"name": "test-bin", "path": "src/main.rs"}],
    }
    return create_test_file(directory, "Cargo.toml", content)


def create_sample_composer_json(directory: Union[str, Path]) -> Path:
    """Create a sample composer.json for testing."""
    content = {
        "name": "test/package",
        "description": "A test package",
        "type": "library",
        "require": {"php": "^7.4 || ^8.0", "monolog/monolog": "^2.0"},
        "autoload": {"psr-4": {"Test\\": "src/"}},
        "scripts": {"test": "phpunit", "cs-check": "phpcs", "cs-fix": "phpcbf"},
    }
    return create_test_file(directory, "composer.json", content)
