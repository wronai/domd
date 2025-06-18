#!/bin/bash
# Script to clean backend artifacts

echo "Cleaning backend artifacts..."
rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
