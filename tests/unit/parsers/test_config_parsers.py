"""
Tests for configuration file parsers.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.parsers.base import BaseParser


def test_pyproject_toml_parser(temp_project):
    """Test parsing pyproject.toml files."""
    from domd.core.parsers.pyproject_toml import PyProjectTomlParser

    # Create a sample pyproject.toml
    pyproject_content = """
    [tool.poetry.scripts]
    test = "pytest tests/"
    lint = "flake8 ."

    [tool.poetry]
    name = "test-project"
    version = "0.1.0"
    """

    pyproject_path = temp_project / "pyproject.toml"
    pyproject_path.write_text(pyproject_content)

    # Initialize the parser with the file path
    parser = PyProjectTomlParser(file_path=pyproject_path)

    # Test can_parse
    assert parser.can_parse(pyproject_path)

    # Test parse
    commands = parser.parse()
    assert len(commands) == 2
    assert any(cmd.command == "poetry run test" for cmd in commands)
    assert any(cmd.command == "poetry run lint" for cmd in commands)


def test_package_json_parser(temp_project, sample_package_json):
    """Test parsing package.json files."""
    from domd.core.parsers.package_json import PackageJsonParser

    # Create a package.json file
    package_json_path = temp_project / "package.json"
    package_json_path.write_text(json.dumps(sample_package_json))

    # Initialize the parser with the file path
    parser = PackageJsonParser(file_path=package_json_path)

    # Test can_parse
    assert parser.can_parse(package_json_path)

    # Test parse
    commands = parser.parse()
    assert len(commands) == len(sample_package_json["scripts"])
    assert all(cmd.command.startswith("npm run ") for cmd in commands)
    assert all(cmd.type == "npm_script" for cmd in commands)
    assert all(cmd.source == str(package_json_path) for cmd in commands)


def test_makefile_parser(temp_project):
    """Test parsing Makefiles."""
    from domd.core.parsers.makefile import MakefileParser

    # Create a sample Makefile
    makefile_content = """
    .PHONY: test build clean

    test:
    	pytest tests/

    build:
    	echo "Building..."

    clean:
    	rm -rf dist/ build/
    """

    makefile_path = temp_project / "Makefile"
    makefile_path.write_text(makefile_content)

    # Initialize the parser with the file path
    parser = MakefileParser(file_path=makefile_path)

    # Test can_parse
    assert parser.can_parse(makefile_path)

    # Test parse
    commands = parser.parse()
    assert len(commands) == 3  # test, build, clean
    assert all(cmd.command.startswith("make ") for cmd in commands)
    assert all(cmd.type == "make_target" for cmd in commands)
    assert all(cmd.source == str(makefile_path) for cmd in commands)

    # Extract command names for easier assertion
    command_names = [cmd.command.split()[-1] for cmd in commands]
    assert "test" in command_names
    assert "build" in command_names
    assert "clean" in command_names
