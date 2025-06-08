#!/bin/bash
set -e

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install build tools
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip
pip install build pytest

# Build the package
echo "Building the package..."
python -m build

# Install the package
echo "Installing the package..."
pip install -e .

# Verify installation
echo -e "\nVerifying installation..."
python -c "import domd; print(f'Successfully installed domd version: {domd.__version__}')"

# Run tests if they exist
if [ -d "tests" ]; then
    echo -e "\nRunning tests..."
    pytest -v tests/
else
    echo -e "\nNo tests directory found. Skipping tests."
fi

echo -e "\nInstallation test completed successfully!"
echo "Virtual environment: $PWD/.venv"
echo "To activate: source $PWD/.venv/bin/activate"
