# Command Reference

This document provides a comprehensive reference for all DoMD CLI commands and their options.

## Main Commands

### `domd scan`

Scan the project for commands and generate reports.

**Usage:**
```bash
domd scan [OPTIONS] [PATH]
```

**Options:**
- `--todo-file FILE`       Path to the TODO output file (default: TODO.md)
- `--script-file FILE`     Path to the shell script output file (default: todo.sh)
- `--ignore-file FILE`     Path to the ignore file (default: .doignore)
- `--timeout SECONDS`      Command execution timeout in seconds (default: 30)
- `--include-only PATTERN` Only include files matching pattern
- `--exclude PATTERN`      Exclude files/directories matching pattern
- `--dry-run`              Show what would be done without making changes
- `--init-only`            Only initialize project files
- `--show-ignored`         Show ignored commands
- `--generate-ignore`      Generate a .doignore file
- `--verbose, -v`          Enable verbose output
- `--quiet, -q`            Suppress non-essential output

**Examples:**
```bash
# Basic scan
$ domd scan

# Scan with custom paths
$ domd scan --todo-file MY_TODO.md --script-file run.sh

# Dry run to see what would be done
$ domd scan --dry-run
```

### `domd web`

Start the web interface.

**Usage:**
```bash
domd web [OPTIONS]
```

**Options:**
- `--host TEXT`     Host to bind to (default: 127.0.0.1)
- `--port INTEGER`  Port to listen on (default: 8000)
- `--no-browser`    Do not open the browser automatically
- `--debug`         Enable debug mode

**Examples:**
```bash
# Start web interface
$ domd web

# Start on a specific port
$ domd web --port 8080
```

### `domd test-commands`

Test commands in Docker containers.

**Usage:**
```bash
domd test-commands [OPTIONS] [COMMANDS]...
```

**Options:**
- `-f, --file FILE`        Read commands from file
- `-u, --update-doignore`  Update .doignore with failing commands
- `--no-docker`            Skip Docker testing (only validate commands)
- `--verbose, -v`          Enable verbose output
- `--quiet, -q`            Suppress non-essential output

**Examples:**
```bash
# Test individual commands
$ domd test-commands "ls -la" "pwd"

# Test commands from file
$ domd test-commands -f commands.txt

# Update .doignore with failing commands
$ domd test-commands -f commands.txt --update-doignore
```

## Global Options

These options can be used with any command:

- `--version`       Show the version and exit
- `--help, -h`      Show help message and exit
- `--config FILE`   Specify a config file (default: .domd.yaml)

## Configuration File

DoMD can be configured using a YAML configuration file (`.domd.yaml` by default). Example:

```yaml
# .domd.yaml
scan:
  todo_file: TODO.md
  script_file: todo.sh
  ignore_file: .doignore
  timeout: 30
  include_only:
    - "*.md"
    - "*.sh"
  exclude:
    - "node_modules/**"
    - ".git/**"

web:
  host: 127.0.0.1
  port: 8000
  debug: false

testing:
  update_doignore: true
  use_docker: true
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Command execution failed
- `4`: File I/O error
- `5`: Configuration error

## See Also

- [Getting Started](../getting-started/quick-start.md)
- [Configuration Guide](../user-guide/configuration.md)
- [Docker Integration](../user-guide/docker-integration.md)
