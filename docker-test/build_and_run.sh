#!/bin/bash
set -e

# Create a clean build context
echo "Preparing build context..."
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

# Copy only necessary files
mkdir -p "$BUILD_DIR/src"
cp -r ../src/domd "$BUILD_DIR/src/"
cp ../pyproject.toml ../poetry.lock ../README.md "$BUILD_DIR/"
cp Dockerfile "$BUILD_DIR/"

# Build the Docker image
echo "Building Docker image..."
docker build -t domd-test "$BUILD_DIR"

# Run the container
echo -e "\nRunning tests in Docker container..."
docker run --rm domd-test

echo -e "\nDocker test completed!"
