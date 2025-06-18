#!/bin/bash
set -e

echo "Starting React frontend..."
cd "$(dirname "$0")/../frontend"  # Move to frontend directory

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the React development server
npm start
