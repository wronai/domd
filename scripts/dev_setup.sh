#!/bin/bash
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
echo "Run: poetry run domd --help"
