"""Pytest configuration"""

import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_package_json():
    """Sample package.json content."""
    return {
        "name": "test-project",
        "version": "1.0.0",
        "scripts": {
            "test": "jest",
            "build": "webpack",
            "start": "node server.js"
        }
    }
