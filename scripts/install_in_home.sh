#!/bin/bash
# Script to install the project in a clean environment in the home directory

# Exit on error
set -e

# Create a temporary directory in the home folder
TEMP_DIR="$HOME/domd_temp_$(date +%s)"
echo "Creating temporary directory: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy only the necessary files
cp pyproject.toml poetry.lock README.md "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/src/domd"
cp -r src/domd/ "$TEMP_DIR/src/"

# Move to the temporary directory
cd "$TEMP_DIR"

# Create and activate a new virtual environment
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
poetry config virtualenvs.create true

# Install the project
echo "Installing project in development mode..."
poetry install --with dev,docs,testing,lint,all -v

# Verify installation
echo -e "\n=== Verifying installation ==="
if python -c "import domd; print(f'Successfully installed domd version: {domd.__version__}')"; then
    echo -e "\n=== Installation successful! ==="
    echo "Project has been installed in: $TEMP_DIR"
    echo "To activate the virtual environment, run:"
    echo "  cd $TEMP_DIR"
    echo "  source .venv/bin/activate"
else
    echo -e "\n=== Installation failed. See errors above. ==="
    exit 1
fi
