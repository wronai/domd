#!/bin/bash
# Script to reset the database (WARNING: This will delete all data!)

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Change to project root directory
cd "$PROJECT_ROOT"

# Source environment variables if .env exists
if [ -f ".env" ]; then
    # Only export valid environment variables (lines with VAR=value format)
    export $(grep -v '^#' .env | grep -v '^$' | grep '=' | xargs) 2>/dev/null || true
fi

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

echo "Resetting database..."
read -p "Are you sure you want to reset the database? This will delete all data! [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if we're in a Poetry environment
    if ! command -v poetry &> /dev/null; then
        echo "Error: Poetry is required but not installed or not in PATH"
        exit 1
    fi

    # Install dependencies if not already installed
    if ! PYTHONPATH="$PROJECT_ROOT/src" poetry run python -c "import domd.db" &> /dev/null; then
        echo "Installing Python dependencies..."
        poetry install --no-interaction
    fi

    # Install Alembic if not already installed
    if ! poetry run alembic --version &> /dev/null; then
        echo "Installing Alembic..."
        poetry add alembic --dev
    fi

    echo "Dropping and recreating database..."
    if ! PYTHONPATH="$PROJECT_ROOT/src" poetry run python -c "import domd.db" &> /dev/null; then
        echo "Error: Could not find domd.db module. Check your project structure."
        echo "Looking for module in: $PROJECT_ROOT/src/domd/"
        exit 1
    fi
    
    # Run the database reset with the correct PYTHONPATH
    PYTHONPATH="$PROJECT_ROOT/src" poetry run python -m domd.db reset
    
    echo "Running migrations..."
    PYTHONPATH="$PROJECT_ROOT/src" poetry run alembic upgrade head
    
    echo "Cleaning frontend dependencies..."
    rm -rf frontend/node_modules 2>/dev/null || true
    rm -f frontend/package-lock.json 2>/dev/null || true
    
    echo "Database reset complete."
else
    echo "Database reset cancelled."
fi
