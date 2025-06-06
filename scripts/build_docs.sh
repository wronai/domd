#!/bin/bash
# Documentation build script

echo "Building DoMD documentation..."

# Install docs dependencies
poetry install --with docs

# Build documentation
poetry run mkdocs build

echo "Documentation built successfully!"
echo "Open: site/index.html"
