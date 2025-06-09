#!/bin/bash
# Script to completely clean and recreate the Poetry environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit on error
set -e

# Check Python version
check_python_version() {
    local required_python="3.8"
    local python_version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')

    if [ "$(printf '%s\n' "$required_python" "$python_version" | sort -V | head -n1)" = "$required_python" ]; then
        echo -e "${GREEN}✓ Python $python_version is installed${NC}"
    else
        echo -e "${RED}✗ Python $required_python or higher is required (found $python_version)${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}=== Checking system requirements ===${NC}"
check_python_version

echo -e "\n${YELLOW}=== Cleaning up existing environment ===${NC}"

# Deactivate any active virtual environment
deactivate 2>/dev/null || true

# Remove Poetry virtual environment
poetry env remove python 2>/dev/null || true
rm -rf ~/.cache/pypoetry/virtualenvs/domd-* 2>/dev/null || true
rm -rf .venv 2>/dev/null || true

# Clear Poetry cache
poetry cache clear . --all -n 2>/dev/null || true

# Create a fresh virtual environment
echo -e "\n${YELLOW}=== Creating fresh virtual environment ===${NC}"
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
