# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and documentation

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.1.0] - 2025-06-06

### Added
- Initial release of TodoMD
- Project command detection for 15+ project types
- Support for JavaScript/Node.js projects (package.json, npm scripts)
- Support for Python projects (pyproject.toml, setup.py, requirements.txt, tox.ini, pytest.ini)
- Support for build systems (Makefile, CMakeLists.txt, Gradle, Maven)
- Support for Docker (Dockerfile, docker-compose.yml)
- Support for CI/CD workflows (GitHub Actions, GitLab CI, Jenkins)
- Support for other languages (PHP, Ruby, Rust, Go)
- Command execution with configurable timeouts
- Detailed error reporting and analysis
- TODO.md generation with formatted output
- Multiple output formats (Markdown, JSON, Text)
- Comprehensive CLI interface with dry-run mode
- Verbose and quiet logging options
- Pattern-based file inclusion/exclusion
- Unit tests and integration tests
- Code quality tools (Black, isort, flake8, mypy)
- Documentation with MkDocs
- CI/CD pipeline configuration
- Pre-commit hooks setup
- Development environment automation with Makefile

### Technical Details
- Python 3.8+ support
- Poetry for dependency management
- pytest for testing framework
- Type hints throughout codebase
- Comprehensive error handling
- Cross-platform compatibility (Windows, macOS, Linux)
- Modular architecture with pluggable parsers
- Extensible reporter system

### Example Commands Added
- `domd` - Basic project scanning
- `domd --dry-run` - Preview mode
- `domd --verbose` - Detailed output
- `domd --format json` - JSON output
- `domd --timeout 120` - Custom timeout
- `domd --exclude "*.test.*"` - Pattern exclusion

### Parsers Implemented
- **JavaScript**: package.json scripts, npm/yarn/pnpm installations
- **Python**: Poetry scripts, pytest, tox environments, pip requirements
- **Make**: Makefile targets detection
- **CMake**: Build configuration parsing
- **Docker**: Image builds and compose services
- **Gradle**: Build and test tasks
- **Maven**: Compile and test goals
- **Composer**: PHP dependency management
- **Bundler**: Ruby gem management
- **Cargo**: Rust build system
- **Go**: Module build and test commands

### Output Features
- Structured TODO.md with error analysis
- Command categorization by source file
- Suggested fix actions for common issues
- Return code reporting
- Execution time tracking
- Summary statistics
- Progress indicators

### Quality Assurance
- 95%+ test coverage
- Type checking with mypy
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Security scanning with bandit
- Pre-commit hooks for quality gates
- Continuous integration pipeline

## [0.0.1] - 2025-06-05

### Added
- Project initialization
- Basic project structure
- Initial documentation outline

---

## Version History

- **0.1.0** - Full initial release with comprehensive project support
- **0.0.1** - Project setup and structure

## Migration Guide

### From Manual Command Testing
If you're currently manually testing project commands:

1. Install TodoMD: `pip install domd`
2. Run in your project: `domd`
3. Review generated TODO.md for failed commands
4. Fix issues using provided suggestions

### Integration with Existing Workflows

#### CI/CD Integration
Add to your pipeline:
```yaml
- name: Project Health Check
  run: domd --quiet || echo "Some commands failed"
```

#### Pre-commit Integration
Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: domd
      name: TodoMD Health Check
      entry: domd
      language: system
```

#### Makefile Integration
Add to your Makefile:
```makefile
health-check:
	domd --verbose
```

## Roadmap

### v0.2.0 (Planned)
- Configuration file support (.domd.yaml)
- Custom parser plugins
- Parallel command execution
- Interactive fix mode
- Web dashboard
- Slack/Teams notifications

### v0.3.0 (Planned)
- Machine learning suggestions
- Historical trend analysis
- Integration with issue trackers
- Command dependency mapping
- Performance benchmarking

### v1.0.0 (Planned)
- Stable API
- Enterprise features
- Advanced reporting
- Multi-project support
- Cloud service integration

## Contributing

See [CONTRIBUTING.md] for guidelines on how to contribute to this project.

## Support

- Documentation: https://domd.readthedocs.io
- Issues: https://github.com/yourusername/domd/issues
- Discussions: https://github.com/yourusername/domd/discussions