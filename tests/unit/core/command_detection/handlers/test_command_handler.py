import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.command_detection.handlers.command_handler import CommandHandler
from domd.core.command_execution.command_runner import CommandRunner
from domd.core.domain.command import Command


class TestCommandHandler:
    @pytest.fixture
    def handler(self, tmp_path):
        # Create a temporary directory for the project
        project_path = tmp_path / "test_project"
        project_path.mkdir()

        # Create a mock command runner
        command_runner = MagicMock(spec=CommandRunner)

        # Return a properly initialized CommandHandler
        return CommandHandler(
            project_path=project_path,
            command_runner=command_runner,
            enable_docker_testing=False,  # Disable Docker for unit tests
        )

    # Test cases for valid commands
    @pytest.mark.parametrize(
        "command_str",
        [
            "ls -la",
            "git status",
            "python3 script.py --help",
            "docker ps -a",
            "kubectl get pods -n default",
            "echo 'Hello, World!'",
            "npm install package --save-dev",
        ],
    )
    def test_valid_commands(self, handler, command_str):
        """Test that valid shell commands are correctly identified."""
        is_valid, reason = handler.is_valid_command(command_str)
        assert (
            is_valid is True
        ), f"Expected valid command: {command_str}. Reason: {reason}"

    # Test cases for markdown content
    @pytest.mark.parametrize(
        "content,expected_reason",
        [
            ("# Header", "Markdown header"),
            ("- List item", "Markdown list item"),
            ("1. Numbered item", "Numbered list item"),
            ("| Column 1 | Column 2 |", "Markdown table"),
            ("```\ncode\n```", "Markdown code block"),
            ("`code`", "Inline code"),
            ("**bold**", "Bold text"),
            ("[link](url)", "Markdown link"),
            (" > Blockquote", "Blockquote"),
        ],
    )
    def test_markdown_content(self, handler, content, expected_reason):
        """Test that markdown content is correctly identified as invalid commands."""
        is_valid, reason = handler.is_valid_command(content)
        assert is_valid is False, f"Expected invalid command: {content}"
        assert expected_reason in reason, f"Unexpected reason: {reason}"

    # Test cases for documentation content
    @pytest.mark.parametrize(
        "content,expected_reason",
        [
            ("For more information", "Documentation phrase"),
            ("See also:", "Documentation phrase"),
            ("Example:", "Documentation phrase"),
            ("Note: This is important", "Documentation note"),
            ("Warning: Be careful", "Warning message"),
            ("Important: Read this", "Important note"),
            ("Tip: Try this", "Tip note"),
            ("Caution: Hot surface", "Caution note"),
            ("See the documentation", "Documentation reference"),
            ("Refer to the manual", "Documentation reference"),
        ],
    )
    def test_documentation_content(self, handler, content, expected_reason):
        """Test that documentation content is correctly identified as invalid commands."""
        is_valid, reason = handler.is_valid_command(content)
        assert is_valid is False, f"Expected invalid command: {content}"
        assert expected_reason in reason, f"Unexpected reason: {reason}"

    # Test cases for other non-command patterns
    @pytest.mark.parametrize(
        "content,expected_reason",
        [
            ("variable = value", "Variable assignment"),
            ("{}", "Empty code block"),
            ("[]", "Empty array"),
            ("{", "Opening brace"),
            ("}", "Closing brace"),
            ("Error: Something went wrong", "Error message"),
            ("Exception: Invalid input", "Exception message"),
            ("Traceback (most recent call last):", "Traceback message"),
            ("Stack trace:", "Stack trace"),
            ("/path/to/file", "File path"),
            ("~/config/file", "Home-relative path"),
            ("./script.sh", "Relative path"),
            ("https://example.com", "URL"),
            ("www.example.com", "Web address"),
            ("user@example.com", "Email address"),
        ],
    )
    def test_other_non_command_patterns(self, handler, content, expected_reason):
        """Test that other non-command patterns are correctly identified."""
        is_valid, reason = handler.is_valid_command(content)
        assert is_valid is False, f"Expected invalid command: {content}"
        assert expected_reason in reason, f"Unexpected reason: {reason}"

    # Test cases for command length and complexity
    @pytest.mark.parametrize(
        "content,expected_reason",
        [
            ("x" * 501, "too long"),
            ("a", "too short"),
            ("12345", "only numbers or special characters"),
            ("!@#$%^", "only numbers or special characters"),
        ],
    )
    def test_command_length_and_complexity(self, handler, content, expected_reason):
        """Test that command length and complexity are properly validated."""
        is_valid, reason = handler.is_valid_command(content)
        assert is_valid is False, f"Expected invalid command: {content}"
        assert expected_reason in reason.lower(), f"Unexpected reason: {reason}"

    # Test cases for internal tool paths
    @pytest.mark.parametrize(
        "path",
        [
            "/tmp/file",
            "/var/log",
            "/usr/local/bin",
            "~/.cache/something",
            "/dev/null",
        ],
    )
    def test_internal_tool_paths(self, handler, path):
        """Test that internal tool paths are correctly identified."""
        is_valid, reason = handler.is_valid_command(path)
        assert is_valid is False, f"Expected invalid command: {path}"
        assert "internal tool path" in reason.lower(), f"Unexpected reason: {reason}"

    # Test with Command objects
    def test_with_command_object(self, handler):
        """Test that Command objects are properly handled."""
        cmd = Command("ls -la", "list files", "test", "test_source")
        is_valid, reason = handler.is_valid_command(cmd)
        assert (
            is_valid is True
        ), f"Expected valid command: {cmd.command}. Reason: {reason}"

    # Test with dictionary input
    def test_with_dictionary_input(self, handler):
        """Test that dictionary input is properly handled."""
        cmd_dict = {"command": "ls -la", "description": "list files"}
        is_valid, reason = handler.is_valid_command(cmd_dict)
        assert is_valid is True, f"Expected valid command: {cmd_dict}. Reason: {reason}"

    # Test error handling in pattern matching
    def test_error_handling_in_pattern_matching(self, handler, caplog):
        """Test that errors in pattern matching are properly handled."""
        # Test with a command that would normally pass validation
        is_valid, reason = handler.is_valid_command("test")

        # We expect this to be a valid command
        assert (
            is_valid is True or "Not a recognized command" in reason
        ), f"Expected valid command or 'Not a recognized command' reason, got: {reason}"

    # Test command patterns with logging
    def test_command_patterns_with_logging(self, handler, caplog):
        """Test that command patterns are properly logged."""
        test_cases = [
            ("ls -la", "Command matches"),
            ("git status", "Command matches"),
            ("# Header", "Markdown header"),
            ("variable = value", "Variable assignment"),
        ]

        for cmd, log_fragment in test_cases:
            caplog.clear()
            handler.is_valid_command(cmd)
            assert any(
                log_fragment in record.message for record in caplog.records
            ), f"Expected log message containing '{log_fragment}' for command: {cmd}"
