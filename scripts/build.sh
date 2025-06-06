#!/bin/bash
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
ls -la dist/
