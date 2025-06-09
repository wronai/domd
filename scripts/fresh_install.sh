#!/bin/bash
# Script to create a fresh Python virtual environment and install the project

# Exit on error
set -e

echo "=== Setting up fresh Python environment ==="

# Remove existing virtual environment
echo "Removing existing virtual environment..."
rm -rf .venv

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install build tools
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip
pip install --upgrade setuptools wheel build

# Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Configure Poetry
echo "Configuring Poetry..."
poetry config virtualenvs.in-project true

# Install project in development mode
echo "Installing project in development mode..."
poetry install --with dev,docs,testing,lint,all -v

echo -e "\n=== Installation complete! ==="
echo "To activate the virtual environment, run: source .venv/bin/activate"
