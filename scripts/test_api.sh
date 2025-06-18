#!/bin/bash
set -e

echo "Running API tests..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run 'make install' first."
    exit 1
fi

# Run tests
cd "$(dirname "$0")/.."  # Move to project root
python -m pytest tests/ -v --cov=domd --cov-report=term-missing
