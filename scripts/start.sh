#!/bin/bash
set -e

echo "Starting Flask API server..."
cd "$(dirname "$0")/.."  # Move to project root

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies if not already installed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
fi

# Run the Flask API
export FLASK_APP=src/domd/adapters/api/flask_api.py
export FLASK_ENV=development
flask run --port=5000
