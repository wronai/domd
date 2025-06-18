#!/bin/bash
# Script to format backend code

echo "Formatting backend code..."
poetry run black .
poetry run isort .
