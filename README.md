# DoMD - Project Command Detector

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/wronai/domd/workflows/Tests/badge.svg)](https://github.com/wronai/domd/actions)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](https://www.docker.com/)
[![Documentation](https://img.shields.io/badge/Docs-Read%20the%20Docs-blue)](https://wronai.github.io/domd/)

**DoMD** (DoM Detector) is a powerful tool for automatically detecting, executing, and managing commands in development projects. It intelligently identifies available commands from various configuration files (e.g., `package.json`, `Makefile`, `pyproject.toml`) and provides a unified interface to run them.

## ✨ Key Features

- **Automatic Command Detection** - Discovers commands from various project files
- **Docker Integration** - Run commands in isolated containers
- **Smart Command Filtering** - Skip specific commands using `.doingore`
- **Cross-Platform** - Works on Linux, macOS, and Windows
- **Extensible** - Add support for new command types and tools

## 🚀 Quick Start

### Installation

```bash
# Install using pip
pip install domd

# Or using Docker
docker run -v $(pwd):/app ghcr.io/wronai/domd domd
```

### Basic Usage

1. **List available commands** in your project:
   ```bash
   domd --list
   ```

2. **Run a command**:
   ```bash
   domd run test
   ```

3. **Generate a report** of available commands:
   ```bash
   domd report
   ```

## 📖 Documentation

For detailed documentation, please visit our [documentation site](https://wronai.github.io/domd/) or check the [docs](./docs) directory.

- [Installation Guide](./docs/installation.md)
- [Usage Guide](./docs/usage.md)
- [Docker Integration](./docs/docker.md)
- [Advanced Configuration](./docs/features/core.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 💡 Need Help?

Open an [issue](https://github.com/wronai/domd/issues) if you need help or have questions.
   # Will run in Docker if configured in .dodocker
   domd run pytest
   ```

3. **Force local execution**

   ```bash
   domd run --no-docker pytest
   ```


## 🔧 Command Filtering with .doignore

Skip specific commands by creating a `.doignore` file:

```text
# .doignore
*test*
*serve*
*deploy*
```


## 📊 Example Workflow

```bash
# Initialize a new project
domd init

# Scan for available commands
domd scan

# Run tests (in Docker if configured)
domd run test

# Generate a report
domd report --output report.html
```


## 📚 Documentation

Full documentation is available in the [docs/](docs/) directory:

- [Installation](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Configuration](docs/configuration.md)
- [Docker Integration](docs/docker.md) - Complete guide to using Docker with DoMD
- [API Reference](docs/api.md)
- [Development](docs/development/)
- [Contributing](docs/CONTRIBUTING.md)

### Quick Links

- [Docker Configuration](docs/docker.md#configuration)
- [Volume Mounting](docs/docker.md#volume-mounting)
- [Environment Variables](docs/docker.md#environment-variables)
- [Troubleshooting](docs/troubleshooting.md)

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOMD_CONFIG` | Path to config file | `~/.config/domd/config.yaml` |
| `DOMD_LOG_LEVEL` | Logging level | `INFO` |
| `DOCKER_HOST` | Docker daemon URL | `unix:///var/run/docker.sock` |


### Configuration File

Example `~/.config/domd/config.yaml`:

```yaml
defaults:
  docker_image: python:3.9-slim
  timeout: 300
  workdir: /app

commands:
  test:
    description: Run tests
    docker: true
    image: python:3.9-slim
    volumes:
      - ~/.cache/pip:/.cache/pip

  lint:
    description: Run linters
    docker: true
    image: node:16-slim
```


## 🌟 Features in Detail

### Smart Command Detection

- Automatically discovers commands from:
  - `package.json` (npm, yarn, pnpm)
  - `Makefile`
  - `pyproject.toml` (Poetry, PDM)
  - `setup.py`
  - `docker-compose.yml`
  - And many more...

### Advanced Docker Integration

- Automatic container creation and management
- Volume mounting for persistent data
- Environment variable support
- Custom Docker network configuration
- Resource limits and constraints

### Extensible Architecture

- Plugin system for adding custom command detectors
- Hooks for pre/post command execution
- Custom formatters for output
- Event system for extensibility


## 🚀 Getting Started Guide

### Prerequisites
- Python 3.8+
- Docker (optional but recommended)
- Git

### Installation Options

#### From PyPI
```bash
pip install domd
```

#### From Source
```bash
git clone https://github.com/wronai/domd.git
cd domd
pip install -e .
```

#### Using Docker
```bash
docker run --rm -v $(pwd):/app ghcr.io/wronai/domd:latest domd
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

[Apache 2.0](LICENSE) © 2023 WronAI

## 📚 Resources

- [Documentation](https://wronai.github.io/domd/)
- [Issue Tracker](https://github.com/wronai/domd/issues)
- [Changelog](CHANGELOG.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 🔧 Zaawansowane użycie

### REST API

DoMD now provides a REST API for programmatic access to all functionality:

```bash
# Start the API server
domd-api --port 8080 --path /path/to/project
```

Available endpoints:

- `GET /health` - Check server status
- `GET /api/commands` - Get all commands
- `POST /api/commands/scan` - Scan project for commands
- `POST /api/commands/test` - Test commands
- `GET /api/reports` - Get information about reports
- `POST /api/reports/generate` - Generate reports
- `GET /api/stats` - Get statistics

Example API usage:

```bash
# Scan a project
curl -X POST http://localhost:8080/api/commands/scan \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/project"}'

# Test commands
curl -X POST http://localhost:8080/api/commands/test

# Generate reports
curl -X POST http://localhost:8080/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"todo_file": "TODO.md", "done_file": "DONE.md"}'
```

### Architecture

DoMD now uses a clean, layered architecture:

- **Domain Layer**: Core business entities and logic
- **Application Layer**: Use cases and application services
- **Interface Layer**: CLI, API, and other interfaces
- **Infrastructure Layer**: External services and implementations

This modular design makes it easy to extend DoMD with new features and adapters.

## 🔧 Command Filtering with .doignore

Easily skip specific commands during testing by creating a `.doignore` file in your project root. This is perfect for excluding long-running services, deployment scripts, or commands that require special handling.

### Example `.doignore`:
```
# Skip specific commands
npm run dev
npm run start

# Skip patterns
*serve*
*deploy*
*release*

# Skip test commands
*test*
*e2e*
```

### Usage:
```bash
# Generate a template .doignore file
domd --generate-ignore

# Show which commands would be ignored
domd --show-ignored

# Use a custom ignore file
domd --ignore-file custom.ignore
```

## 🐳 Docker Integration with .dodocker

Run commands in isolated Docker containers by creating a `.dodocker` file in your project root. This is great for ensuring consistent environments and avoiding local system dependencies.

### Example `.dodocker`:
```
# Install dependencies
pip install -e .

# Run tests
pytest -v

# Run linters
black --check .
isort --check-only .
flake8 .
```

### Usage:
```bash
# Commands will be executed in a Docker container
domd

# Specify a different Docker image
domd --docker-image python:3.9
```

## 📦 Supported Project Types

### JavaScript/Node.js
- `package.json` - npm scripts
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` - dependency installation

### Python
- `pyproject.toml` - Poetry scripts, pytest configuration
- `setup.py` - installation and testing
- `requirements.txt` - pip installations
- `tox.ini` - test environments
- `pytest.ini` - test configuration

### Build Systems
- `Makefile` - make targets
- `CMakeLists.txt` - cmake builds
- `build.gradle` - gradle tasks
- `pom.xml` - maven goals

### Docker & Containers
- `Dockerfile` - image builds
- `docker-compose.yml` - service orchestration

### CI/CD
- `.github/workflows/*.yml` - GitHub Actions
- `.gitlab-ci.yml` - GitLab CI
- `Jenkinsfile` - Jenkins pipelines

### Other Languages
- `composer.json` (PHP)
- `Gemfile` (Ruby)
- `Cargo.toml` (Rust)
- `go.mod` (Go)

## 🤓 Installation

### Using pip
```bash
# Install from PyPI
pip install domd

# Install with all optional dependencies
pip install domd[all]

# Install with REST API support
pip install domd[api]
```

### Basic Usage
```bash
# Scan current directory and test commands
domd

# Specify a project directory
domd --path /path/to/project

# Only create files without testing commands
domd --init-only

# Generate .doignore template
domd --generate-ignore

# Show what commands would be ignored
domd --show-ignored

# Start the REST API server
domd-api --port 8080
```

# Custom timeout (default: 60 seconds)
domd --timeout 120

# Different output formats
domd --format json
domd --format text

# Exclude specific patterns
domd --exclude "*.test.js" --exclude "node_modules/*"

# Include only specific patterns
domd --include-only "Makefile" --include-only "package.json"
```

### Example Output

When commands fail, DoMD generates a structured TODO.md:

```markdown
# TODO - Failed Project Commands

Automatically generated by DoMD v0.1.0
Date: 2025-06-06 10:30:15
Project: /home/user/my-project

Found **2** commands that require fixing:

## Task 1: NPM script - test

**Source:** `package.json`
**Return Code:** 1

### Command to fix:
```bash
npm run test
```

### Error:
```
Error: Cannot find module 'jest'
npm ERR! Test failed. See above for more details.
```

### Suggested Actions:
- [ ] Install missing dependencies: `npm install`
- [ ] Check if jest is in devDependencies
- [ ] Verify test configuration
- [ ] Run `npm install --save-dev jest` if missing

---

## Task 2: Make target - build

**Source:** `Makefile`
**Return Code:** 2

### Command to fix:
```bash
make build
```

### Error:
```
make: *** No rule to make target 'src/main.c', needed by 'build'. Stop.
```

### Suggested Actions:
- [ ] Check if source files exist
- [ ] Verify Makefile paths and dependencies
- [ ] Review build configuration
- [ ] Ensure all required files are present
```

## 🔧 Configuration

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path`, `-p` | Project directory path | `.` (current) |
| `--dry-run`, `-d` | Preview mode (no execution) | `False` |
| `--verbose`, `-v` | Detailed output | `False` |
| `--quiet`, `-q` | Suppress output except errors | `False` |
| `--output`, `-o` | Output file path | `TODO.md` |
| `--format` | Output format (markdown/json/text) | `markdown` |
| `--timeout` | Command timeout in seconds | `60` |
| `--exclude` | Exclude file patterns | `None` |
| `--include-only` | Include only specific patterns | `None` |
| `--ignore-file` | Path to custom ignore file | `.doignore` |

### 🔒 Ignoring Commands with `.doignore`

DoMD allows you to specify commands that should be ignored during execution using a `.doignore` file. This is useful for skipping known problematic or interactive commands.

#### `.doignore` File Format

```
# Ignore specific commands (exact match)
npm run dev
python manage.py runserver

# Ignore using patterns (supports glob patterns)
*serve*
*test*
*debug*

# Comments start with #
# This line is ignored
```

#### How It Works
- Each line in the file represents a pattern to match against commands
- Lines starting with `#` are treated as comments
- Blank lines are ignored
- Patterns support glob-style wildcards (`*` matches any sequence of characters)
- Matches are case-insensitive

### 🐳 Running Commands in Docker with `.dodocker`

For better isolation and consistency, you can specify commands that should be executed inside a Docker container using a `.dodocker` file.

#### `.dodocker` File Format

```
# Commands to run in Docker container
pytest
black --check .
flake8
mypy .
```

#### How It Works
- Each line specifies a command that should be run in a Docker container
- Commands are executed in the `python:3.9` container by default
- The project directory is mounted to `/app` in the container
- The working directory is set to `/app`
- The container is automatically removed after execution

#### Customizing Docker Configuration

You can customize the Docker configuration by creating a `Dockerfile` in your project root. For example:

```dockerfile
FROM python:3.9

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi
```

DoMD will automatically detect and use this `Dockerfile` when running commands in a container.

## 🤖 Programmatic Usage

```python
from domd import ProjectCommandDetector

# Initialize detector
detector = ProjectCommandDetector(
    project_path="./my-project",
    timeout=60,
    exclude_patterns=["*.pyc", "__pycache__/*"]
)

# Scan for commands
commands = detector.scan_project()
print(f"Found {len(commands)} commands")

# Test commands
detector.test_commands(commands)

# Generate report
detector.generate_output_file("RESULTS.md", "markdown")

# Access results
failed_commands = detector.failed_commands
success_rate = (len(commands) - len(failed_commands)) / len(commands) * 100
print(f"Success rate: {success_rate:.1f}%")
```

## 🧪 Development

### Setup Development Environment
```bash
git clone https://github.com/wronai/domd.git
cd domd
poetry install --with dev,docs,testing

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=domd --cov-report=html

# Run specific test categories
poetry run pytest -m "unit"
poetry run pytest -m "integration"
```

### Code Quality
```bash
# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Linting
poetry run flake8 src/ tests/
poetry run mypy src/

# All quality checks
make lint
```

### Building Documentation
```bash
# Serve locally
poetry run mkdocs serve

# Build static site
poetry run mkdocs build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Adding New Parsers

To add support for a new project type:

1. Create a parser in `src/domd/parsers/`
2. Implement the parser interface
3. Add tests in `tests/parsers/`
4. Update documentation

Example parser structure:
```python
from .base import BaseParser

class NewProjectParser(BaseParser):
    def can_parse(self, file_path: Path) -> bool:
        return file_path.name == "config.yaml"

    def parse_commands(self, file_path: Path) -> List[Dict]:
        # Implementation here
        pass
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for automated project health monitoring
- Built with [Poetry](https://python-poetry.org/) for dependency management
- Uses [pytest](https://pytest.org/) for testing framework
- Documentation powered by [MkDocs](https://www.mkdocs.org/)

## 📊 Project Stats

- **Languages Supported**: 10+
- **File Types Detected**: 20+
- **Command Types**: 50+
- **Python Versions**: 3.8+

## 🔗 Links

- [Documentation](https://domd.readthedocs.io)
- [PyPI Package](https://pypi.org/project/domd/)
- [GitHub Repository](https://github.com/wronai/domd)
- [Issue Tracker](https://github.com/wronai/domd/issues)
- [Changelog](https://github.com/wronai/domd/blob/main/CHANGELOG.md)

## 💡 Use Cases

- **Pre-deployment Checks**: Verify all project commands work before deployment
- **CI/CD Integration**: Add as a quality gate in your pipeline
- **Onboarding**: Help new developers identify setup issues
- **Project Maintenance**: Regular health checks for legacy projects
- **Documentation**: Generate comprehensive command documentation

## ⚡ Quick Examples

### CI/CD Integration (GitHub Actions)
```yaml
name: Project Health Check
on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install DoMD
      run: pip install domd
    - name: Run Project Health Check
      run: domd --verbose
    - name: Upload TODO.md if failures
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: failed-commands
        path: TODO.md
```

### Make Integration
```makefile
.PHONY: health-check
health-check:
	@echo "Running project health check..."
	@domd --quiet || (echo "❌ Some commands failed. Check TODO.md" && exit 1)
	@echo "✅ All project commands working!"

.PHONY: health-report
health-report:
	@domd --dry-run --verbose
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: domd-check
        name: Project Command Health Check
        entry: domd
        language: system
        pass_filenames: false
        always_run: true
```
