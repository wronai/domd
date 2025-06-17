import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Mock the CommandRunner to avoid executing actual commands
class MockCommandRunner:
    def __init__(self, *args, **kwargs):
        self.executor = MagicMock()
        self.max_retries = 0
        self.retry_delay = 1.0
        self.retry_backoff = 2.0
        self._result_handlers = []

    def add_result_handler(self, handler):
        self._result_handlers.append(handler)

    def run(self, command, cwd=None, env=None, timeout=None, check=False):
        class Result:
            def __init__(self):
                self.returncode = 0
                self.stdout = f"Mock output for: {command}"
                self.stderr = ""

        return Result()


# Import the modules after setting up the mock
with patch(
    "domd.core.command_execution.command_runner.CommandRunner", MockCommandRunner
):
    from domd.adapters.persistence.shell_command_executor import ShellCommandExecutor
    from domd.core.command_detection.handlers.command_handler import CommandHandler


def test_commands(test_cases):
    # Create a mock command runner
    command_runner = MockCommandRunner()

    # Initialize CommandHandler with required parameters
    project_path = Path.cwd()  # Use current working directory for testing
    handler = CommandHandler(
        project_path=project_path,
        command_runner=command_runner,
        timeout=30,  # 30 second timeout for tests
        ignore_patterns=[
            r"^#",  # Comments
            r"^\s*$",  # Empty lines
        ],
    )

    # Create a shell command executor for testing command parsing
    executor = ShellCommandExecutor()

    # Patch the actual command execution to prevent real commands from running
    def mock_execute(command_str, cwd=None, env=None, timeout=None):
        class Result:
            def __init__(self):
                self.returncode = 0
                self.stdout = f"Mock output for: {command_str}"
                self.stderr = ""

        return Result()

    # Track test results
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []

    # Test each test case
    for test_case in test_cases:
        if len(test_case) == 3:
            test_input, expected_valid, description = test_case
        else:
            test_input, expected_valid = test_case
            description = ""

        print(f"\n{'='*80}")
        print(f"TEST: {test_input}")
        if description:
            print(f"DESC: {description}")

        # Test command validation
        is_valid, reason = handler.is_valid_command(test_input)
        print(f"\nVALIDATION: {'VALID' if is_valid else 'INVALID'}")
        if not is_valid:
            print(f"REASON: {reason}")

        # Test command parsing (only for commands marked as valid)
        parse_success = False
        parse_details = ""
        if is_valid:
            try:
                # This will raise an exception if the command can't be parsed
                args, needs_shell = executor._parse_command(test_input)
                parse_success = True
                parse_details = f"ARGS: {args}\nNEEDS SHELL: {needs_shell}"
                print("PARSE: SUCCESS")
                print(parse_details)
            except Exception as e:
                parse_success = False
                parse_details = f"PARSE ERROR: {str(e)}"
                print(parse_details)

        # Check if the result matches expectations
        test_passed = is_valid == expected_valid
        if test_passed:
            passed_tests += 1
            print("STATUS: \033[92mPASS\033[0m")
        else:
            expected_status = "valid" if expected_valid else "invalid"
            print(f"STATUS: \033[91mFAIL\033[0m (Expected {expected_status})")
            failed_tests.append(
                {
                    "input": test_input,
                    "description": description,
                    "expected": expected_valid,
                    "actual": is_valid,
                    "reason": reason if not is_valid else "",
                    "parse_details": parse_details,
                }
            )

        # Only attempt execution for valid, parseable commands
        if is_valid and parse_success and expected_valid:
            print("\nEXECUTION TEST:")
            try:
                # Use the mock executor to avoid real command execution
                result = mock_execute(test_input)
                print(f"- Exit code: {result.returncode}")
                if result.stdout:
                    print(
                        f"- Output: {result.stdout[:200]}"
                        + ("..." if len(result.stdout) > 200 else "")
                    )
                if result.stderr:
                    print(
                        f"- Error: {result.stderr[:200]}"
                        + ("..." if len(result.stderr) > 200 else "")
                    )
            except Exception as e:
                print(f"- EXECUTION ERROR: {str(e)}")

    # Print summary
    print("\n" + "=" * 80)
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    if failed_tests:
        print("\nFAILED TESTS:")
        for i, failed in enumerate(failed_tests, 1):
            print(f"\n{i}. Input: {failed['input']}")
            if failed["description"]:
                print(f"   Description: {failed['description']}")
            print(f"   Expected: {'valid' if failed['expected'] else 'invalid'}")
            print(f"   Actual: {'valid' if failed['actual'] else 'invalid'}")
            if failed["reason"]:
                print(f"   Reason: {failed['reason']}")
            if "parse_details" in failed and failed["parse_details"]:
                print(f"   {failed['parse_details']}")

    # Return non-zero exit code if any tests failed
    return 0 if len(failed_tests) == 0 else 1


if __name__ == "__main__":
    test_cases = [
        # Basic commands
        ("echo 'Hello World'", True, "Simple echo command"),
        ("ls -la", True, "ls with flags"),
        ("pwd", True, "Print working directory"),
        ("cd /tmp && pwd", True, "Command with chaining"),
        ("source .env", True, "Source command"),
        # Commands with various syntax
        ('echo "Hello $USER"', True, "Variable expansion in double quotes"),
        ("echo 'Hello $USER'", True, "Single quotes prevent expansion"),
        ('echo "Current dir: $(pwd)"', True, "Command substitution"),
        ("echo {1..5}", True, "Brace expansion"),
        ("echo file_{a..c}.txt", True, "Brace expansion with letters"),
        # Redirections and pipes
        ('echo "test" > output.txt', True, "Output redirection"),
        ("cat file.txt 2> error.log", True, "Error redirection"),
        (
            "cat file.txt >> output.log 2>&1",
            True,
            "Append and redirect stderr to stdout",
        ),
        ("cat /etc/passwd | grep root", True, "Simple pipe"),
        ("ps aux | grep python | head -n 5", True, "Multiple pipes"),
        # Environment variables and assignments
        ("export VAR=value", True, "Export variable"),
        ("VAR=value command", True, "Temporary environment variable"),
        ("echo $HOME", True, "Environment variable expansion"),
        ('echo "Current PATH: $PATH"', True, "PATH variable in string"),
        # Control operators
        ("command1 && command2", True, "AND operator"),
        ("command1 || command2", True, "OR operator"),
        ("command1; command2", True, "Command separator"),
        ("(cd /tmp && pwd)", True, "Subshell"),
        ('{ echo "start"; command1; command2; } > log.txt', True, "Command group"),
        # Common tools and commands
        ('git commit -m "Update"', True, "Git commit"),
        ("docker-compose up -d", True, "Docker Compose"),
        ("python3 -m http.server 8000", True, "Python HTTP server"),
        ('ssh user@host "command"', True, "SSH remote command"),
        ('find . -name "*.py" | xargs grep -l "import"', True, "Find and grep"),
        # Edge cases with special characters
        ('echo "File with spaces.txt"', True, "Filename with spaces"),
        (r'echo "Special chars: \"\'\`\$\\"', True, "Special characters in string"),
        ('echo "Line 1\nLine 2"', True, "Newlines in string"),
        (
            'echo "Current dir: $(pwd) and time: $(date)"',
            True,
            "Multiple command substitutions",
        ),
        # Invalid commands (should be filtered out)
        ("# Header", False, "Markdown header"),
        ("## Documentation", False, "Markdown subheader"),
        ("- [ ] Task item", False, "Markdown task item"),
        ("| Column 1 | Column 2 |", False, "Markdown table"),
        ("```bash", False, "Code block start"),
        ("Some text with no command", False, "Plain text"),
        ("/path/to/some/file.txt", False, "File path"),
        ("https://example.com", False, "URL"),
        ("user@example.com", False, "Email"),
        ("Error: something went wrong", False, "Error message"),
        ("INFO: This is a log message", False, "Log message"),
        ("2023-01-01 12:00:00 [INFO] Starting process", False, "Timestamped log"),
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("\t\n", False, "Whitespace characters"),
        (
            "This is a paragraph of text that explains something.",
            False,
            "Documentation text",
        ),
        (
            "For more information, see the documentation.",
            False,
            "Documentation reference",
        ),
    ]

    test_commands(test_cases)
