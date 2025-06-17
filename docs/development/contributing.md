# Contributing to DoMD

Thank you for your interest in contributing to DoMD! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes
6. Run tests
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- pip
- Git
- (Optional) Docker for testing

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/wronai/domd.git
   cd domd
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Project Structure

```
src/domd/
├── __init__.py
├── cli.py                   # Command-line interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── command_detection/   # Command detection logic
│   ├── command_execution/   # Command execution logic
│   ├── domain/             # Domain models
│   ├── ports/              # Interface definitions
│   └── services/           # Business logic
├── adapters/               # External service adapters
│   ├── cli/                # CLI adapters
│   └── api/                # Web API adapters
└── utils/                  # Utility functions

tests/                      # Test suite
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── fixtures/               # Test fixtures

docs/                       # Documentation
```

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function signatures
- Keep functions small and focused
- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Keep lines under 100 characters

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/unit/test_command_handler.py
```

Run with coverage:
```bash
pytest --cov=domd --cov-report=term-missing
```

### Writing Tests

- Write tests for all new functionality
- Follow the Arrange-Act-Assert pattern
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies

## Documentation

### Building Documentation

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

### Documentation Guidelines

- Keep documentation up-to-date
- Include examples in code blocks
- Use consistent formatting
- Link to related documentation
- Document public API changes in CHANGELOG.md

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Update documentation as needed
6. Submit a pull request

### Pull Request Guidelines

- Keep PRs focused and small
- Include a clear description
- Reference related issues
- Update documentation
- Ensure tests pass

## Reporting Issues

When reporting issues, please include:

1. A clear title and description
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details
5. Any relevant logs or screenshots

## Feature Requests

For feature requests, please:

1. Check if a similar feature already exists
2. Explain the problem it solves
3. Describe the proposed solution
4. Include any relevant examples

## Getting Help

If you need help or have questions:

1. Check the documentation
2. Search existing issues
3. Open a new issue if needed

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
