import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Import after path setup
from src.domd.cli import create_parser, main, validate_args
from src.domd.core.domain.command import Command


class TestCLI:
    @pytest.fixture
    def setup_test_environment(self):
        """Set up a test environment with temporary directory and sample files."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        test_dir = Path(temp_dir) / "test_project"
        test_dir.mkdir()

        # Create a sample .doignore file
        (test_dir / ".doignore").write_text("# Sample ignore file\n*.log\n*.tmp\n")

        # Create a sample Python file
        (test_dir / "test.py").write_text("print('Hello, World!')\n")

        # Create a sample TODO.md
        (test_dir / "TODO.md").write_text("# TODO\n\n- [ ] Test task\n")

        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)

        yield test_dir

        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_validate_args_with_valid_args(self):
        """Test that validate_args returns None for valid arguments."""
        parser = create_parser()
        args = parser.parse_args(["scan", "--path", ".", "--ignore-file", ".doignore"])
        assert validate_args(args) is None

    def test_validate_args_with_missing_path(self):
        """Test that validate_args returns an error for missing path."""
        parser = create_parser()
        args = parser.parse_args(["scan"])
        args.path = "/nonexistent/path"
        assert "does not exist" in validate_args(args)

    def test_scan_command_with_defaults(self, setup_test_environment, capsys):
        """Test the scan command with default arguments."""
        _ = setup_test_environment  # Unused variable

        # Mock the ProjectCommandDetector to avoid actual command execution
        with patch("src.domd.cli.ProjectCommandDetector") as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.scan_project.return_value = []

            # Run the CLI with scan command
            with patch("sys.argv", ["domd", "scan"]):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "TodoMD" in captured.out
        assert "Project:" in captured.out

    def test_scan_command_with_ignore_file(self, setup_test_environment, capsys):
        """Test the scan command with a custom ignore file."""
        test_dir = setup_test_environment
        custom_ignore = test_dir / ".customignore"
        custom_ignore.write_text("*.py\n")

        # Mock the ProjectCommandDetector
        with patch("src.domd.cli.ProjectCommandDetector") as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.scan_project.return_value = []

            # Run the CLI with custom ignore file
            with patch(
                "sys.argv", ["domd", "scan", "--ignore-file", str(custom_ignore)]
            ):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert str(custom_ignore) in captured.out

    def test_generate_ignore_option(self, setup_test_environment, capsys):
        """Test the --generate-ignore option."""
        _ = setup_test_environment  # Unused variable
        ignore_file = Path(".domdignore")

        # Run the CLI with --generate-ignore
        with patch(
            "sys.argv",
            ["domd", "scan", "--generate-ignore", "--ignore-file", str(ignore_file)],
        ):
            result = main()

        assert result == 0
        assert ignore_file.exists()
        captured = capsys.readouterr()
        assert "Generated ignore file" in captured.out

    def test_show_ignored_option(self, setup_test_environment, capsys):
        """Test the --show-ignored option."""
        _ = setup_test_environment  # Unused variable

        # Mock the command service and repository
        with patch("src.domd.cli.ApplicationFactory") as mock_factory:
            mock_service = MagicMock()
            mock_repo = MagicMock()
            mock_factory.create_command_service.return_value = mock_service
            mock_factory.create_command_repository.return_value = mock_repo
            mock_factory.create_command_presenter.return_value = MagicMock()

            # Run the CLI with --show-ignored
            with patch("sys.argv", ["domd", "scan", "--show-ignored"]):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "Ignored commands" in captured.out

    def test_dry_run_option(self, setup_test_environment, capsys):
        """Test the --dry-run option."""
        _ = setup_test_environment  # Unused variable

        # Mock the ProjectCommandDetector
        with patch("src.domd.cli.ProjectCommandDetector") as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.scan_project.return_value = [
                Command("echo 'test'", "Test command")
            ]

            # Run the CLI with --dry-run
            with patch("sys.argv", ["domd", "scan", "--dry-run"]):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "Test command" in captured.out

    def test_init_only_option(self, setup_test_environment, capsys):
        """Test the --init-only option."""
        _ = setup_test_environment  # Unused variable

        # Run the CLI with --init-only
        with patch("sys.argv", ["domd", "scan", "--init-only"]):
            result = main()

        assert result == 0
        assert (test_dir / ".doignore").exists()
        captured = capsys.readouterr()
        assert "Initialized project" in captured.out

    def test_web_command(self, capsys):
        """Test the web command."""
        # Mock the start_web_interface function
        with patch("src.domd.cli.start_web_interface") as mock_web:
            mock_web.return_value = 0

            # Run the CLI with web command
            with patch("sys.argv", ["domd", "web"]):
                result = main()

        assert result == 0
        mock_web.assert_called_once()

    def test_missing_command_shows_help(self, capsys):
        """Test that running without a command shows help."""
        # Run the CLI without a command
        with patch("sys.argv", ["domd"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()
        assert "scan" in captured.out.lower()
        assert "web" in captured.out.lower()

    def test_error_handling(self, setup_test_environment, capsys):
        """Test error handling in the CLI."""
        test_dir = setup_test_environment

        # Mock ProjectCommandDetector to raise an exception
        with patch("src.domd.cli.ProjectCommandDetector") as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.scan_project.side_effect = Exception("Test error")

            # Run the CLI with scan command
            with patch("sys.argv", ["domd", "scan"]):
                result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err


if __name__ == "__main__":
    pytest.main([__file__])
