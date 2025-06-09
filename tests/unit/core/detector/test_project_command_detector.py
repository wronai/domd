"""
Unit tests for ProjectCommandDetector class.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.project_detection.detector import ProjectCommandDetector


class TestProjectCommandDetector:
    """Test cases for ProjectCommandDetector class."""

    @pytest.mark.unit
    def test_detector_initialization(self, temp_project):
        """Test detector initialization with various parameters."""
        detector = ProjectCommandDetector(
            project_path=str(temp_project),
            timeout=30,
            exclude_patterns=["*.pyc"],
            include_patterns=["Makefile"],
            todo_file="CUSTOM_TODO.md",
            done_file="CUSTOM_DONE.md",
            script_file="custom_todo.sh",
            ignore_file=".customignore",
        )

        assert detector.project_path == temp_project
        assert detector.timeout == 30
        assert detector.exclude_patterns == ["*.pyc"]
        assert detector.include_patterns == ["Makefile"]
        assert detector.todo_file == temp_project / "CUSTOM_TODO.md"
        assert detector.done_file == temp_project / "CUSTOM_DONE.md"
        assert detector.script_file == temp_project / "custom_todo.sh"
        assert detector.ignore_file == ".customignore"

    @pytest.mark.unit
    def test_detector_default_initialization(self):
        """Test detector initialization with default parameters."""
        detector = ProjectCommandDetector()

        assert detector.project_path == Path(".").resolve()
        assert detector.timeout == 60
        assert detector.exclude_patterns == []
        assert detector.include_patterns == []
        assert detector.todo_file == Path("TODO.md").resolve()
        assert detector.done_file == Path("DONE.md").resolve()
        assert detector.script_file == Path("todo.sh").resolve()
        assert detector.ignore_file == ".doignore"

    @pytest.mark.unit
    def test_scan_project_with_config_files(self, temp_project):
        """Test scanning a project with configuration files."""
        # Create a mock config file handler
        with patch(
            "domd.core.project_detection.detector.ConfigFileHandler"
        ) as mock_handler:
            # Set up the mock
            mock_instance = mock_handler.return_value
            mock_instance.find_config_files.return_value = []

            detector = ProjectCommandDetector(str(temp_project))
            commands = detector.scan_project()

            assert commands == []
            mock_instance.find_config_files.assert_called_once()
