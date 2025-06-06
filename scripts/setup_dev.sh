#!/bin/bash
# TodoMD Project Setup Script
# Automatically creates the complete project structure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="todomd"
PROJECT_DESC="Project Command Detector - Automatically detects and tests project commands"
AUTHOR_NAME="Your Name"
AUTHOR_EMAIL="your.email@example.com"
GITHUB_USERNAME="yourusername"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

create_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        log_info "Created directory: $1"
    fi
}

create_file() {
    local file_path="$1"
    local content="$2"

    # Create directory if it doesn't exist
    local dir_path=$(dirname "$file_path")
    create_directory "$dir_path"

    # Create file with content
    echo "$content" > "$file_path"
    log_info "Created file: $file_path"
}

# Main setup function
setup_project() {
    log_info "Setting up TodoMD project structure..."

    # Create main directories
    create_directory "src/${PROJECT_NAME}"
    create_directory "src/${PROJECT_NAME}/parsers"
    create_directory "src/${PROJECT_NAME}/reporters"
    create_directory "src/${PROJECT_NAME}/utils"
    create_directory "tests"
    create_directory "tests/parsers"
    create_directory "tests/reporters"
    create_directory "tests/utils"
    create_directory "tests/fixtures"
    create_directory "docs"
    create_directory "scripts"
    create_directory "examples"

    # Create __init__.py files
    create_file "src/${PROJECT_NAME}/__init__.py" '"""TodoMD Package"""

__version__ = "0.1.0"

from .detector import ProjectCommandDetector
from .cli import main

__all__ = ["ProjectCommandDetector", "main", "__version__"]'

    create_file "src/${PROJECT_NAME}/parsers/__init__.py" '"""Parsers package"""'
    create_file "src/${PROJECT_NAME}/reporters/__init__.py" '"""Reporters package"""'
    create_file "src/${PROJECT_NAME}/utils/__init__.py" '"""Utils package"""'
    create_file "tests/__init__.py" '"""Tests package"""'
    create_file "tests/parsers/__init__.py" ''
    create_file "tests/reporters/__init__.py" ''
    create_file "tests/utils/__init__.py" ''

    # Create detector.py (simplified version)
    create_file "src/${PROJECT_NAME}/detector.py" '"""Main detector module"""

import os
import json
import subprocess
import sys
import re
from pathlib import Path
import toml
import configparser
from typing import Dict, List, Tuple, Any
import yaml

class ProjectCommandDetector:
    """Main class for detecting and testing project commands."""

    def __init__(self, project_path: str = ".", timeout: int = 60,
                 exclude_patterns: List[str] = None,
                 include_patterns: List[str] = None):
        self.project_path = Path(project_path).resolve()
        self.timeout = timeout
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.failed_commands = []

    def scan_project(self) -> List[Dict]:
        """Scan project for commands."""
        # Implementation from original script
        return []

    def test_commands(self, commands: List[Dict]) -> None:
        """Test all commands."""
        # Implementation from original script
        pass

    def generate_output_file(self, output_path: str, format_type: str) -> None:
        """Generate output file."""
        # Implementation from original script
        pass'

    # Create basic test files
    create_file "tests/conftest.py" '"""Pytest configuration"""

import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_package_json():
    """Sample package.json content."""
    return {
        "name": "test-project",
        "version": "1.0.0",
        "scripts": {
            "test": "jest",
            "build": "webpack",
            "start": "node server.js"
        }
    }'

    create_file "tests/test_detector.py" '"""Test detector module"""

import pytest
from todomd.detector import ProjectCommandDetector

def test_detector_init():
    """Test detector initialization."""
    detector = ProjectCommandDetector()
    assert detector.project_path.exists()
    assert detector.timeout == 60
    assert detector.failed_commands == []

def test_scan_project_empty(temp_project):
    """Test scanning empty project."""
    detector = ProjectCommandDetector(str(temp_project))
    commands = detector.scan_project()
    assert commands == []'

    # Create documentation files
    create_file "docs/index.md" "# TodoMD Documentation

Welcome to TodoMD documentation.

## Quick Start

\`\`\`bash
pip install todomd
todomd
\`\`\`"

    create_file "docs/mkdocs.yml" "site_name: TodoMD Documentation
nav:
  - Home: index.md
  - Installation: installation.md
  - Usage: usage.md
  - API Reference: api.md

theme:
  name: material"

    # Create example files
    create_file "examples/package.json" '{
  "name": "example-project",
  "scripts": {
    "test": "echo \"Test command\"",
    "build": "echo \"Build command\""
  }
}'

    create_file "examples/Makefile" 'test:
	echo "Testing..."

build:
	echo "Building..."

.PHONY: test build'

    # Create tox.ini
    create_file "tox.ini" '[tox]
envlist = py38,py39,py310,py311,py312

[testenv]
deps = pytest
       pytest-cov
commands = pytest

[testenv:lint]
deps = black
       isort
       flake8
       mypy
commands =
    black --check src/ tests/
    isort --check-only src/ tests/
    flake8 src/ tests/
    mypy src/

[testenv:docs]
deps = mkdocs
       mkdocs-material
commands = mkdocs build'

    # Create pre-commit config
    create_file ".pre-commit-config.yaml" 'repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8'

    log_success "Project structure created successfully!"
}

# Install dependencies and setup environment
setup_environment() {
    log_info "Setting up development environment..."

    # Check if Poetry is installed
    if ! command -v poetry &> /dev/null; then
        log_error "Poetry not found. Please install Poetry first:"
        echo "curl -sSL https://install.python-poetry.org | python3 -"
        exit 1
    fi

    # Install dependencies
    log_info "Installing dependencies with Poetry..."
    poetry install --with dev,docs,testing,lint

    # Install pre-commit hooks
    log_info "Installing pre-commit hooks..."
    poetry run pre-commit install

    log_success "Development environment setup complete!"
}

# Initialize git repository
setup_git() {
    log_info "Setting up Git repository..."

    if [ ! -d ".git" ]; then
        git init
        log_info "Initialized Git repository"
    fi

    # Add all files
    git add .
    git commit -m "Initial commit: TodoMD project setup"

    log_success "Git repository initialized with initial commit!"
}

# Run initial tests
run_tests() {
    log_info "Running initial tests..."

    # Format code
    poetry run black src/ tests/
    poetry run isort src/ tests/

    # Run tests
    if poetry run pytest tests/ -v; then
        log_success "All tests passed!"
    else
        log_warning "Some tests failed, but this is expected in initial setup"
    fi
}

# Create development scripts
create_dev_scripts() {
    log_info "Creating development scripts..."

    # Create development setup script
    create_file "scripts/dev_setup.sh" '#!/bin/bash
# Development environment setup

echo "Setting up TodoMD development environment..."

# Install dependencies
poetry install --with dev,docs,testing,lint

# Install pre-commit hooks
poetry run pre-commit install

# Run initial formatting
poetry run black src/ tests/
poetry run isort src/ tests/

echo "Development environment ready!"
echo "Run: poetry run todomd --help"'

    # Create test runner script
    create_file "scripts/run_tests.sh" '#!/bin/bash
# Test runner script

echo "Running TodoMD tests..."

# Unit tests
echo "Running unit tests..."
poetry run pytest tests/ -m "unit" -v

# Integration tests
echo "Running integration tests..."
poetry run pytest tests/ -m "integration" -v

# All tests with coverage
echo "Running all tests with coverage..."
poetry run pytest tests/ --cov=todomd --cov-report=html --cov-report=term

echo "Tests completed!"'

    # Create build script
    create_file "scripts/build.sh" '#!/bin/bash
# Build script

echo "Building TodoMD package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Run quality checks
echo "Running quality checks..."
poetry run black --check src/ tests/
poetry run isort --check-only src/ tests/
poetry run flake8 src/ tests/
poetry run mypy src/

# Run tests
echo "Running tests..."
poetry run pytest

# Build package
echo "Building package..."
poetry build

echo "Build completed successfully!"
echo "Distribution files:"
ls -la dist/'

    # Create documentation build script
    create_file "scripts/build_docs.sh" '#!/bin/bash
# Documentation build script

echo "Building TodoMD documentation..."

# Install docs dependencies
poetry install --with docs

# Build documentation
poetry run mkdocs build

echo "Documentation built successfully!"
echo "Open: site/index.html"'

    # Make scripts executable
    chmod +x scripts/*.sh

    log_success "Development scripts created!"
}

# Display completion message
show_completion_message() {
    echo
    echo "======================================"
    log_success "TodoMD Project Setup Complete!"
    echo "======================================"
    echo
    echo "📁 Project structure created"
    echo "📦 Dependencies installed"
    echo "🔧 Development environment ready"
    echo "📚 Documentation framework setup"
    echo "🧪 Testing framework configured"
    echo "🎨 Code quality tools installed"
    echo
    echo "Next steps:"
    echo "1. Update author information in pyproject.toml"
    echo "2. Update GitHub URLs in README.md and pyproject.toml"
    echo "3. Implement the detector logic in src/todomd/detector.py"
    echo "4. Add more comprehensive tests"
    echo "5. Build and publish: make build"
    echo
    echo "Quick commands:"
    echo "  poetry run todomd --help      # Show CLI help"
    echo "  make test                      # Run tests"
    echo "  make lint                      # Run linting"
    echo "  make docs                      # Build documentation"
    echo "  make health-check              # Test on current project"
    echo
    echo "Development workflow:"
    echo "  make dev                       # Full development setup"
    echo "  make quick-test                # Quick test run"
    echo "  make format                    # Format code"
    echo "  make ci                        # Run CI pipeline locally"
    echo
}

# Main execution
main() {
    echo "🚀 TodoMD Project Setup Script"
    echo "==============================="
    echo

    # Check if we're in the right directory
    if [ -f "pyproject.toml" ] && grep -q "name = \"todomd\"" pyproject.toml; then
        log_info "Found existing TodoMD project configuration"
    else
        log_warning "pyproject.toml not found or not a TodoMD project"
        log_info "Make sure you have the pyproject.toml file in the current directory"
    fi

    # Create project structure
    setup_project

    # Create development scripts
    create_dev_scripts

    # Setup environment
    setup_environment

    # Setup git
    setup_git

    # Run initial tests
    run_tests

    # Show completion message
    show_completion_message

    log_success "Setup completed successfully! 🎉"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi