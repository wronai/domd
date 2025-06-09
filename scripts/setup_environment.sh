#!/bin/bash
# Script to set up a clean Poetry environment for the project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Setting up Poetry environment ===${NC}"

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Deactivate any active virtual environment
echo -e "${YELLOW}Deactivating any active virtual environment...${NC}
deactivate 2>/dev/null || true

# Remove existing virtual environment
echo -e "${YELLOW}Removing existing virtual environment...${NC}
poetry env remove python 2>/dev/null || true
rm -rf ~/.cache/pypoetry/virtualenvs/domd-* 2>/dev/null || true
rm -rf .venv 2>/dev/null || true

# Clear Poetry cache
echo -e "${YELLOW}Clearing Poetry cache...${NC}
poetry cache clear . --all -n 2>/dev/null || true

# Remove lock file if exists
if [ -f "poetry.lock" ]; then
    echo -e "${YELLOW}Removing existing lock file...${NC}
    rm poetry.lock
fi

# Install Python dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}
sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv

# Install/upgrade Poetry
echo -e "${YELLOW}Installing/upgrading Poetry...${NC}
curl -sSL https://install.python-poetry.org | python3 - --version 1.7.1

# Add Poetry to PATH if not already
export PATH="$HOME/.local/bin:$PATH"

# Configure Poetry
echo -e "${YELLOW}Configuring Poetry...${NC}
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Create new virtual environment
echo -e "${YELLOW}Creating new virtual environment...${NC}
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install build tools
echo -e "${YELLOW}Upgrading pip and installing build tools...${NC}
pip install --upgrade pip
pip install --upgrade setuptools wheel build

# Install the project in development mode
echo -e "${YELLOW}Installing project in development mode...${NC}
poetry install --with dev,docs,testing,lint,all -v

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}
if python -c "import domd; print(f'Successfully installed domd version: {domd.__version__}')"; then
    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo -e "${GREEN}To activate the virtual environment, run: source .venv/bin/activate${NC}"
else
    echo -e "${RED}✗ Setup failed. Please check the error messages above.${NC}"
    exit 1
fi
