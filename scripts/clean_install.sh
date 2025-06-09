#!/bin/bash
# Script to completely clean and recreate the Poetry environment

# Exit on error
set -e

echo "=== Cleaning up existing environment ==="

# Deactivate any active virtual environment
deactivate 2>/dev/null || true

# Remove Poetry virtual environment
poetry env remove python 2>/dev/null || true
rm -rf ~/.cache/pypoetry/virtualenvs/domd-* 2>/dev/null || true
rm -rf .venv 2>/dev/null || true

# Clear Poetry cache
poetry cache clear . --all -n 2>/dev/null || true

# Create a fresh virtual environment
echo -e "\n=== Creating fresh virtual environment ==="
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install Poetry
echo -e "\n=== Setting up Poetry ==="
pip install --upgrade pip
pip install poetry

# Configure Poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true

# Install dependencies with --no-interaction to avoid prompts
echo -e "\n=== Installing dependencies ==="
poetry install --with dev,docs,testing,lint,all --no-interaction

echo -e "\n=== Installation complete! ==="
echo "To activate the virtual environment, run: source .venv/bin/activate"
