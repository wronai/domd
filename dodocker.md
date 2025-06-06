# .dodocker - Docker Command Configuration

## Overview
The `.dodocker` file is a configuration file that specifies commands to be executed inside a Docker container during the testing and validation process. It works in conjunction with taskguard to ensure consistent testing environments.

## File Format
The `.dodocker` file is a simple text file where each line represents a shell command to be executed in sequence within the Docker container. Comments start with `#`.

## How It Works

1. **Environment Setup**
   - taskguard automatically creates a clean Docker container
   - The container is based on the specified Docker image (default: `python:3.13-slim`)
   - The project directory is mounted into the container

2. **Command Execution**
   - Each non-comment line in `.dodocker` is executed as a shell command
   - Commands are executed in the order they appear
   - The working directory is set to the project root
   - If any command fails (non-zero exit code), execution stops immediately

3. **Environment Variables**
   - All environment variables from the host are available in the container
   - Additional container-specific variables are set:
     - `CONTAINER_WORKDIR`: Path to the project directory in the container
     - `CONTAINER_ID`: The ID of the running container

## Example `.dodocker` File
```
# Install dependencies
pip install -e .

# Run tests
pytest -v

# Run linters
black --check .
isort --check-only .
flake8
mypy .

# Test the CLI
python -m domd --help
python -m domd --version
```

## Best Practices

1. **Order of Commands**
   - Install dependencies first
   - Run tests before linters
   - Keep related commands together

2. **Error Handling**
   - Each command should be idempotent when possible
   - Include error handling within complex commands
   - Use `|| true` to allow specific commands to fail without stopping execution

3. **Performance**
   - Group similar commands together
   - Cache dependencies between runs when possible
   - Avoid unnecessary package installations

## Integration with taskguard

taskguard automatically detects the `.dodocker` file and executes its contents in a Docker container. The process is:

1. taskguard starts and detects the `.dodocker` file
2. A Docker container is created with the project directory mounted
3. Each command in `.dodocker` is executed in sequence
4. Output is captured and displayed in the taskguard interface
5. The container is automatically cleaned up after execution

## Customization

### Using a Custom Docker Image
Specify a custom Docker image by adding a comment at the top of the file:
```
# DOCKER_IMAGE=python:3.13-slim
```

### Environment Variables
Set environment variables for the container:
```
# ENV PYTHONPATH=/app
# ENV DEBUG=true
```

## Troubleshooting

### Common Issues
1. **Permission Denied**
   - Ensure the container user has write permissions to mounted volumes

2. **Command Not Found**
   - Make sure all required binaries are installed in the container
   - Consider using absolute paths to binaries

3. **Network Issues**
   - Check if the container has network access
   - Ensure any required ports are exposed

### Debugging
- Add `set -x` at the top of your commands to enable verbose output
- Use `echo` statements to log progress
- Check taskguard logs for detailed error messages
