# Docker Integration

DoMD provides seamless Docker integration, allowing you to run commands in isolated containers with automatic environment detection. This document covers all aspects of using Docker with DoMD.

## Table of Contents
- [Basic Configuration](#basic-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Volume Mounting](#volume-mounting)
- [Environment Variables](#environment-variables)
- [Debugging](#debugging)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Basic Configuration

### The .dodocker File

Create a `.dodocker` file in your project root to configure Docker execution:

```yaml
# .dodocker
test:
  image: python:3.9-slim  # Base image to use
  description: Run Python tests  # Optional description
  workdir: /app  # Working directory in container
  volumes:  # Volume mappings
    ~/.cache/pip:/.cache/pip  # Cache directory
    .:/app  # Mount current directory
  environment:  # Environment variables
    PYTHONPATH: /app
```

### Running Commands

Run commands with Docker (automatically detected from .dodocker):

```bash
# Run tests in Docker
poetry run domd run test

# Force local execution (bypass Docker)
poetry run domd run --no-docker test

# List available Docker commands
poetry run domd list --docker
```

## Advanced Configuration

### Multiple Command Configurations

You can configure multiple commands with different settings:

```yaml
# .dodocker
format:
  image: python:3.9-slim
  description: Format Python code
  volumes:
    .:/app
  command: "black ."  # Override default command

test:
  image: node:16-slim
  description: Run JavaScript tests
  volumes:
    .:/app
    /app/node_modules  # Anonymous volume for dependencies
  environment:
    NODE_ENV: test
```

### Using Docker Compose

For more complex setups, you can use Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
    working_dir: /app
```

Then reference it in your `.dodocker` file:

```yaml
test:
  compose: docker-compose.yml
  service: app
  command: pytest tests/
```

## Volume Mounting

DoMD handles volume mounting with smart defaults:

- Current directory is mounted to `/app` by default
- Common cache directories are automatically mounted
- Environment-specific paths are preserved

### Custom Volume Mounts

```yaml
test:
  image: python:3.9-slim
  volumes:
    .:/app  # Mount current directory
    ~/.cache/pip:/.cache/pip  # Cache directory
    /tmp:/tmp  # Mount system temp
    /data  # Anonymous volume
```

## Environment Variables

### Passing Environment Variables

You can pass environment variables to Docker containers:

```bash
# Pass environment variables from host
DOMD_ENV=production poetry run domd run test

# Or define them in .dodocker
test:
  environment:
    NODE_ENV: test
    DEBUG: 1
    DATABASE_URL: postgres://user:pass@db:5432/mydb
```

### Environment File

For sensitive data, use an environment file:

```yaml
test:
  env_file: .env.test
  environment:
    - NODE_ENV=test
```

## Debugging

### Debug Mode

To debug Docker-related issues:

```bash
# Show Docker commands being executed
DOMD_DEBUG=1 poetry run domd run test

# Get shell in container with the same environment
poetry run domd shell test
```

### Logs and Inspection

```bash
# View container logs
docker logs <container_id>

# Inspect container configuration
docker inspect <container_id>

# View running processes
docker top <container_id>
```

## Best Practices

1. **Use Specific Image Tags**
   - Prefer specific version tags over `latest`
   - Example: `python:3.9-slim` instead of just `python`

2. **Minimize Image Size**
   - Use `-slim` or `-alpine` variants when possible
   - Clean up package caches in the same RUN instruction

3. **Cache Dependencies**
   - Mount package caches as volumes
   - Use multi-stage builds for production images

4. **Security**
   - Never run as root in containers
   - Use `.dockerignore` to exclude sensitive files
   - Keep images updated with security patches

## Troubleshooting

### Common Issues

#### Permission Denied Errors

If you see permission errors with mounted volumes:

1. Make sure the container user has proper permissions
2. Set the correct user/group in your Dockerfile:

```dockerfile
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID appuser && \
    useradd -u $USER_ID -g appuser -m appuser

USER appuser
```

#### Missing Dependencies

If a command works locally but fails in Docker:

1. Check if all required system packages are installed in the image
2. Verify the working directory is set correctly
3. Ensure environment variables are properly passed

#### Network Issues

For network-related problems:

```bash
# Check network connectivity inside container
docker run --rm --network host busybox ping google.com

# Inspect container network
docker network inspect bridge
```

### Getting Help

If you encounter issues:

1. Run with `DOMD_DEBUG=1` for verbose output
2. Check the [GitHub Issues](https://github.com/wronai/domd/issues)
3. Join our [Discord Community](https://discord.gg/your-community) for support
