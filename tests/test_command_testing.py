"""Tests for command testing functionality."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from domd.core.command_detection.handlers.command_handler import CommandHandler
from domd.core.command_execution.command_runner import CommandRunner


class TestCommandTesting(unittest.TestCase):
    """Test command testing functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.dodocker_path = self.temp_dir / ".dodocker"
        self.doignore_path = self.temp_dir / ".doignore"
        
        # Create a simple .dodocker file
        self.dodocker_path.write_text(
            """# Test .dodocker file
python:
  image: python:3.9-slim
  description: Python interpreter
  workdir: /app

# This is a test command
echo:
  image: alpine:latest
  description: Simple echo command
"""
        )
        
        # Create an empty .doignore file
        self.doignore_path.touch()
        
        # Create a mock command runner
        self.command_runner = MagicMock(spec=CommandRunner)
        
        # Initialize command handler
        self.handler = CommandHandler(
            project_path=self.temp_dir,
            command_runner=self.command_runner,
            enable_docker_testing=True,
            dodocker_path=str(self.dodocker_path),
            doignore_path=str(self.doignore_path),
        )

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch("domd.core.command_detection.handlers.command_handler.DockerTester")
    def test_validate_commands(self, mock_docker_tester):
        """Test command validation with Docker testing."""
        # Setup mock Docker tester
        mock_tester = MagicMock()
        mock_tester.test_command_in_docker.return_value = (True, "Success")
        mock_docker_tester.return_value = mock_tester
        
        # Test with valid and invalid commands
        commands = ["echo test", "invalid-command", "ls -la"]
        results = self.handler.validate_commands(commands, test_in_docker=True)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertTrue(results["echo test"][0])  # Valid command
        self.assertFalse(results["invalid-command"][0])  # Invalid command
        
        # Verify Docker tester was called for valid commands
        mock_tester.test_command_in_docker.assert_called()
        
        # Verify .doignore was not updated (no failures in Docker)
        self.assertEqual(len(self.handler.invalid_commands), 1)
        self.assertEqual(len(self.handler.untested_commands), 2)

    @patch("domd.core.command_detection.handlers.command_handler.DockerTester")
    def test_update_doignore(self, mock_docker_tester):
        """Test updating .doignore with failing commands."""
        # Setup mock Docker tester to fail specific commands
        mock_tester = MagicMock()
        
        def mock_test_command(cmd):
            return (False, "Command failed") if "fail" in cmd else (True, "Success")
            
        mock_tester.test_command_in_docker.side_effect = mock_test_command
        mock_docker_tester.return_value = mock_tester
        
        # Test with commands that will fail in Docker
        commands = ["fail-command-1", "should-pass", "fail-command-2"]
        self.handler.validate_commands(commands, test_in_docker=True)
        
        # Update .doignore
        failed_commands = ["fail-command-1", "fail-command-2"]
        updated_count = self.handler.update_doignore(failed_commands)
        
        # Verify .doignore was updated
        self.assertEqual(updated_count, 2)
        self.assertTrue(self.doignore_path.exists())
        
        # Verify content
        with open(self.doignore_path, "r") as f:
            content = f.read()
            
        self.assertIn("fail-command-1", content)
        self.assertIn("fail-command-2", content)
        self.assertNotIn("should-pass", content)

    def test_command_validation(self):
        """Test basic command validation."""
        # Test valid commands
        self.assertTrue(self.handler.is_valid_command("echo test")[0])
        self.assertTrue(self.handler.is_valid_command("ls -la")[0])
        self.assertTrue(self.handler.is_valid_command("cd /tmp && ls")[0])
        
        # Test invalid commands
        self.assertFalse(self.handler.is_valid_command("This is just text")[0])
        self.assertFalse(self.handler.is_valid_command("# This is a comment")[0])
        self.assertFalse(self.handler.is_valid_command("   ")[0])

    @patch("domd.core.command_detection.handlers.command_handler.DockerTester")
    def test_auto_update_doignore(self, mock_docker_tester):
        """Test automatic .doignore updates when most commands fail."""
        # Setup mock Docker tester to fail most commands
        mock_tester = MagicMock()
        mock_tester.test_command_in_docker.return_value = (False, "Command failed")
        mock_docker_tester.return_value = mock_tester
        
        # Test with mostly failing commands
        commands = [f"failing-{i}" for i in range(6)]  # 6 failing commands
        commands.extend(["valid-1", "valid-2"])  # 2 valid commands
        
        # This should trigger auto-update of .doignore
        results = self.handler.validate_commands(
            commands, 
            test_in_docker=True
        )
        
        # Verify .doignore was updated with failing commands
        self.assertTrue(self.doignore_path.exists())
        with open(self.doignore_path, "r") as f:
            content = f.read()
            
        for cmd in commands[:6]:  # First 6 should be in .doignore
            self.assertIn(cmd, content)
            
        # Last 2 should not be in .doignore (they're valid)
        self.assertNotIn("valid-1", content)
        self.assertNotIn("valid-2", content)


if __name__ == "__main__":
    unittest.main()
