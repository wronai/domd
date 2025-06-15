#!/usr/bin/env python3
"""
Run the DoMD web application (Flask API + React frontend).
"""
import os
import subprocess
import sys
from pathlib import Path

from src.domd.adapters.api.flask_api import DomdFlaskApi


def run_flask():
    """Run the Flask API server."""
    print("Starting Flask API server...")
    api = DomdFlaskApi()
    api.run(host="127.0.0.1", port=5000, debug=True)


def run_react():
    """Run the React frontend development server."""
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print(f"Error: Frontend directory not found at {frontend_dir}")
        return

    print("Starting React development server...")
    os.chdir(frontend_dir)
    subprocess.run(["npm", "start"], check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--frontend-only":
        run_react()
    else:
        # In a real deployment, you would run these in separate terminals
        # For simplicity, we'll just run the Flask backend here
        print("Starting DoMD Web Application")
        print(
            "Note: For development, you should run the frontend separately with 'npm start' in the frontend directory"
        )
        run_flask()
