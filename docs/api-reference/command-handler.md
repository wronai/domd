# Command Handler

## Overview

The `CommandHandler` class is responsible for validating and executing shell commands. It includes features for:

- Command validation
- Command execution
- Path resolution
- Built-in command detection
- Command caching

## Class Reference

### `CommandHandler`

Main class for handling command operations.

#### Methods

##### `is_valid_command(cmd: Union[str, Dict, Command]) -> Tuple[bool, str]`

Validates if a command is a valid shell command.

**Parameters:**
- `cmd`: The command to validate (can be string, dict, or Command object)

**Returns:**
- Tuple of (is_valid: bool, reason: str)

**Example:**
```python
handler = CommandHandler()
is_valid, reason = handler.is_valid_command("ls -la")
```

##### `command_exists(cmd: str) -> bool`

Checks if a command exists in the system PATH.

**Parameters:**
- `cmd`: The command to check

**Returns:**
- bool: True if command exists, False otherwise

**Example:**
```python
exists = command_exists("python3")
```

## Usage Examples

### Basic Command Validation

```python
from domd.core.command_detection.handlers.command_handler import CommandHandler

handler = CommandHandler()

# Check if a command is valid
is_valid, reason = handler.is_valid_command("echo 'Hello, World!'")
print(f"Is valid: {is_valid}, Reason: {reason}")

# Check if a command exists in PATH
exists = command_exists("python3")
print(f"Python3 exists: {exists}")
```

### Integration with Command Execution

```python
from domd.core.command_detection.handlers.command_handler import CommandHandler
from domd.core.domain.command import Command

handler = CommandHandler()

# Create a command object
cmd = Command("echo 'Hello, World!'", "Test command")

# Validate and execute
if handler.is_valid_command(cmd)[0]:
    result = handler.execute_command(cmd)
    print(f"Command output: {result.output}")
    print(f"Exit code: {result.returncode}")
else:
    print(f"Invalid command: {handler.is_valid_command(cmd)[1]}")
```

## Related Components

- [Command Model](../api-reference/command-model.md)
- [Command Service](../api-reference/command-service.md)
- [Docker Integration](../user-guide/docker-integration.md)

## Source Code

[CommandHandler Source](https://github.com/wronai/domd/blob/main/src/domd/core/command_detection/handlers/command_handler.py)
