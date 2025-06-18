#!/bin/bash
set -e

echo "Stopping all services..."

# Stop Flask server (port 5000)
echo "Stopping Flask server..."
pkill -f "flask run" || true

# Stop React development server (port 3000)
echo "Stopping React development server..."
pkill -f "react-scripts start" || true

# Kill any processes on ports 3000 and 5000
for port in 3000 5000; do
    if lsof -ti :$port >/dev/null; then
        echo "Killing process on port $port..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
    fi
done

# Kill any remaining Python processes started by our scripts
pkill -f "python.*(flask_api|run_web)" || true

echo "All services stopped."
