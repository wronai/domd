"""Test detector module"""

import pytest
from domd.detector import ProjectCommandDetector

def test_detector_init():
    """Test detector initialization."""
    detector = ProjectCommandDetector()
    assert detector.project_path.exists()
    assert detector.timeout == 60
    assert detector.failed_commands == []

def test_scan_project_empty(temp_project):
    """Test scanning empty project."""
    detector = ProjectCommandDetector(str(temp_project))
    commands = detector.scan_project()
    assert commands == []
