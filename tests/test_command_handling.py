import sys
from pathlib import Path

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domd.adapters.persistence.shell_command_executor import ShellCommandExecutor
from domd.core.command_detection.handlers.command_handler import CommandHandler


def test_commands(test_cases):
    handler = CommandHandler()
    executor = ShellCommandExecutor()

    for i, (test_input, expected_valid) in enumerate(test_cases, 1):
        # Test command validation
        is_valid, reason = handler.is_valid_command(test_input)

        # Test command parsing
        try:
            args, needs_shell = executor._parse_command(test_input)
            parse_success = True
            parse_result = f"args={args}, needs_shell={needs_shell}"
        except Exception as e:
            parse_success = False
            parse_result = f"ERROR: {str(e)}"

        # Print results
        print(f"\nTest {i}: {test_input!r}")
        print(f"  Validation: {'VALID' if is_valid else 'INVALID'} - {reason}")
        print(f"  Parse: {parse_result}")

        if is_valid == expected_valid:
            print("  STATUS: PASS")
        else:
            print(
                f"  STATUS: FAIL - Expected {'valid' if expected_valid else 'invalid'}"
            )

        if is_valid and parse_success:
            print("  Execution test:")
            try:
                result = executor.execute(test_input)
                print(f"  - Exit code: {result.returncode}")
                print(
                    f"  - Output: {result.stdout[:100]}..."
                    if result.stdout
                    else "  - No output"
                )
                if result.stderr:
                    print(f"  - Error: {result.stderr[:200]}...")
            except Exception as e:
                print(f"  - EXECUTION ERROR: {str(e)}")


if __name__ == "__main__":
    test_cases = [
        # Valid commands
        ("echo 'Hello World'", True),
        ("ls -la", True),
        ("pwd", True),
        ("cd /tmp && pwd", True),
        ("source .env", True),
        # Invalid commands
        ("# Header", False),
        ("## Documentation", False),
        ("- [ ] Task item", False),
        ("| Column 1 | Column 2 |", False),
        ("```bash", False),
        ("Some text with no command", False),
        ("/path/to/some/file.txt", False),
        ("https://example.com", False),
        ("user@example.com", False),
        ("Error: something went wrong", False),
        ("INFO: This is a log message", False),
        ("2023-01-01 12:00:00 [INFO] Starting process", False),
        ("$VARIABLE=value", False),
        ("export VAR=value", True),  # This is actually a valid command
        ("cd /nonexistent/directory", True),  # Valid command, will fail at runtime
        ("", False),
        ("   ", False),
        ("\t\n", False),
        # Edge cases
        ("echo 'Hello $USER'", True),
        ("ssh user@host", True),
        ("git commit -m 'Update'", True),
        ("docker-compose up -d", True),
        ("python3 -m http.server 8000", True),
        ("echo 'This is a test' > test.txt", True),
        ("cat /etc/passwd | grep root", True),
    ]

    test_commands(test_cases)
