# To-DoMD - Project Command Detector

[![PyPI version](https://badge.fury.io/py/domd.svg)](https://badge.fury.io/py/domd)
[![Python Support](https://img.shields.io/pypi/pyversions/domd.svg)](https://pypi.org/project/domd/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/wronai/domd/workflows/Tests/badge.svg)](https://github.com/wronai/domd/actions)

**DoMD** automatically detects and tests project commands from various configuration files, then generates a detailed `TODO.md` file for failed commands with error reports and suggested fixes.

## 🚀 Features

- **Universal Detection**: Supports 15+ project types and build systems
- **Smart Testing**: Executes commands with configurable timeouts and error handling
- **Detailed Reports**: Generates formatted TODO.md with error analysis and fix suggestions
- **Multiple Formats**: Output in Markdown, JSON, or plain text
- **CI/CD Ready**: Perfect for automated project health checks
- **Zero Configuration**: Works out of the box with sensible defaults
- **Command Filtering**: Skip specific commands using `.doignore`
- **Docker Integration**: Run commands in isolated Docker containers using `.dodocker`

## 🔍 Supported Project Types

DoMD supports a wide range of project types and build systems, including:

- **JavaScript/TypeScript**: `package.json` (npm, yarn)
- **Python**: `setup.py`, `pyproject.toml`, `requirements.txt`
- **Make**: `Makefile`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Ansible**: Playbooks, roles, inventories, and Galaxy requirements
- **PHP**: `composer.json`
- **Rust**: `Cargo.toml`
- **TOML**: Generic TOML file support
- **YAML**: Generic YAML file support
- **INI**: Generic INI file support

### 🎭 Ansible Support

DoMD provides comprehensive support for Ansible projects, including:

- **Playbooks**: Detection and testing of Ansible playbooks with support for multiple plays and variable files
- **Roles**: Full support for Ansible role structure, dependencies, and metadata
- **Inventories**: Both static and dynamic inventory detection with proper host and group variable resolution
- **Vault**: Secure handling of encrypted content with vault password file support
- **Galaxy**: Role and collection management through requirements files

### Example Commands

```bash
# Playbook execution
ansible-playbook site.yml -i inventory/production

# Role installation
ansible-galaxy install -r requirements.yml

# Vault operations
ansible-vault encrypt group_vars/secrets.yml

# Running tests
make test-ansible        # Run all Ansible tests
make test-playbooks      # Test playbook functionality
make test-roles          # Test role functionality
make test-galaxy         # Test Galaxy integration
make test-vault          # Test Vault operations
make test-inventory      # Test inventory handling
```

### Testing Strategy

Our Ansible integration includes comprehensive test coverage with:

- Unit tests for individual components
- Integration tests for playbook and role execution
- Mocked tests for external dependencies
- Fixtures for common Ansible structures

To run the full test suite:

```bash
# Install development dependencies
make dev-install

# Run all tests
make test

# Run Ansible-specific tests
make test-ansible
```

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

## 🛠 Installation

### Using pip
```bash
pip install domd
```

### Using Poetry
```bash
poetry add domd
```

### From source
```bash
git clone https://github.com/wronai/domd.git
cd domd
poetry install
```

## 📖 Usage

### Basic Usage
```bash
# Scan current directory
domd

# Scan specific project
domd --path /path/to/project

# Preview commands without executing
domd --dry-run

# Custom output file
domd --output FAILED_COMMANDS.md
```

### Advanced Options
```bash
# Verbose output with detailed logging
domd --verbose

# Quiet mode (errors only)
domd --quiet

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
