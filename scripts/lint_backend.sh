#!/bin/bash
# Script to lint backend code

echo "Linting backend code..."
poetry run black --check .
poetry run isort --check-only .
poetry run flake8 .
