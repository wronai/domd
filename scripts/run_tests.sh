#!/bin/bash
# Test runner script

echo "Running DoMD tests..."

# Unit tests
echo "Running unit tests..."
poetry run pytest tests/ -m "unit" -v

# Integration tests
echo "Running integration tests..."
poetry run pytest tests/ -m "integration" -v

# All tests with coverage
echo "Running all tests with coverage..."
poetry run pytest tests/ --cov=domd --cov-report=html --cov-report=term

echo "Tests completed!"
