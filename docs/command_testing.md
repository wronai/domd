# Command Testing in Docker

DoMD includes a powerful command testing system that can validate and test shell commands in isolated Docker containers. This helps ensure that commands work as expected across different environments.

## Features

- **Command Validation**: Automatically detect valid shell commands and filter out documentation, logs, and other non-command text
- **Docker Testing**: Test commands in isolated Docker containers to verify they work as expected
- **Automatic .doignore Updates**: Automatically update `.doignore` with commands that fail in Docker
- **CLI & REST API**: Full support for both command-line and programmatic access

## CLI Usage

### Test Commands

```bash
# Test individual commands
domd test-commands "ls -la" "pwd" "echo Hello"

# Test commands from a file
domd test-commands -f commands.txt

# Test commands and update .doignore
domd test-commands --update-doignore -f commands.txt

# Skip Docker testing (only validate commands)
domd test-commands --no-docker -f commands.txt

# Specify custom .dodocker and .doignore paths
domd test-commands --dodocker custom.dodocker --doignore .customignore -f commands.txt
```

### Options

- `-f, --file`: Read commands from a file (one per line)
- `--update-doignore`: Update .doignore with commands that fail in Docker
- `--dodocker`: Path to .dodocker configuration file (default: .dodocker)
- `--doignore`: Path to .doignore file (default: .doignore)
- `--no-docker`: Skip Docker testing and only validate commands
- `-v, --verbose`: Enable verbose output

## REST API

### Validate Commands

```http
POST /api/commands/validate
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "commands": ["ls -la", "pwd", "echo Hello"],
  "test_in_docker": true,
  "update_doignore": true
}
```

### Test Commands in Docker

```http
POST /api/commands/test-docker
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "commands": ["ls -la", "pwd", "echo Hello"],
  "update_doignore": true
}
```

### Add Commands to .doignore

```http
POST /api/commands/ignore
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "commands": ["invalid_command"],
  "comment": "These commands don't work in our environment"
}
```

## .dodocker Configuration

The `.dodocker` file specifies how commands should be executed in Docker. Here's an example:

```yaml
# Run Python commands in Python container
python:
  image: python:3.9-slim
  description: Python interpreter
  workdir: /app

# Run Node.js commands in Node container
node:
  image: node:16
  description: Node.js runtime
  workdir: /app
  volumes:
    ./:/app

# Commands with specific requirements
"npm install":
  image: node:16
  description: Install Node.js dependencies
  workdir: /app
  volumes:
    ./:/app
    ~/.npm:/root/.npm
```

## Best Practices

1. **Start with validation**: Use `--no-docker` first to validate commands before Docker testing
2. **Update .doignore**: Regularly update `.doignore` with commands that are known to fail
3. **Customize .dodocker**: Create specific configurations for different types of commands
4. **Use in CI**: Integrate command testing into your CI/CD pipeline to catch issues early

## Troubleshooting

### Common Issues

1. **Docker not available**:
   - Ensure Docker is installed and running
   - Run `docker ps` to verify Docker is working

2. **Permission denied**:
   - Run with `sudo` or add your user to the `docker` group
   - `sudo usermod -aG docker $USER`

3. **Command not found in container**:
   - Update the container image in `.dodocker` to include required tools
   - Use a more complete base image like `ubuntu:latest` for testing

4. **Network issues**:
   - Ensure the container has network access if commands need to download files
   - Add `--network host` to Docker run options in `.dodocker` if needed
