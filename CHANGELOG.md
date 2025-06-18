# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keep-a-changelog],
and this project adheres to [Semantic Versioning][semver].

[keep-a-changelog]: https://keepachangelog.com/en/1.0.0/
[semver]: https://semver.org/spec/v2.0.0.html

## [Unreleased] - YYYY-MM-DD

### Added

- Placeholder for upcoming features

### Changed

- Placeholder for changes in upcoming release

### Deprecated

- Placeholder for soon-to-be removed features

### Removed

- Placeholder for removed features

### Fixed

- Placeholder for bug fixes

### Security

- Placeholder for security-related fixes

## [2.2.41] - 2025-06-18

### Added

- Web interface for interactive command management
- Comprehensive documentation for web interface usage
- Support for custom ports and host binding in web interface

### Changed

- Updated version to 2.2.41 for PyPI publication
- Improved error handling in command detection
- Enhanced documentation structure and readability

### Fixed

- Resolved version mismatch in build artifacts
- Fixed markdown linting issues in documentation
- Addressed various code quality and test issues

## [0.1.0] - 2025-06-06

### Features Added in 0.1.0

- Initial release of DoMD
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

### Example Commands

- `domd` - Basic project scanning
- `domd --dry-run` - Preview mode
- `domd --verbose` - Detailed output
- `domd --format json` - JSON output
- `domd --timeout 120` - Custom timeout
- `domd --exclude "*.test.*"` - Pattern exclusion

### Supported Parsers

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

### Added in 0.0.1

- Project initialization
- Basic project structure
- Initial documentation outline

---

## Version History

- **2.2.41** - Web interface and documentation improvements
- **0.1.0** - Full initial release with comprehensive project support
- **0.0.1** - Project setup and structure

## Migration Guide

### From Manual Command Testing to DoMD

If you're currently manually testing project commands:

1. Install DoMD: `pip install domd`
2. Run in your project: `domd`
3. Review generated TODO.md for failed commands
4. Fix issues using provided suggestions

### Integration with Existing Workflows

#### 1. CI/CD Integration

Add to your pipeline:

```yaml
- name: Project Health Check
  run: domd --quiet || echo "Some commands failed"
```

#### 2. Pre-commit Integration

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: domd
      name: DoMD Health Check
      entry: domd
      language: system
```

#### 3. Makefile Integration

Add to your Makefile:

```makefile
health-check:
    domd --verbose
```

## Roadmap

### Upcoming Features (v0.2.0)

- Configuration file support (`.domd.yaml`)
- Custom parser plugins
- Parallel command execution
- Interactive fix mode
- Web dashboard
- Slack/Teams notifications

### Future Enhancements (v0.3.0)

- Machine learning suggestions
- Historical trend analysis
- Integration with issue trackers
- Command dependency mapping
- Performance benchmarking

### Long-term Goals (v1.0.0+)

- Stable API
- Enterprise features
- Advanced analytics
- Plugin ecosystem
- Community contributions
- Advanced reporting
- Multi-project support
- Cloud service integration

## Contributing

See [CONTRIBUTING.md] for guidelines on how to contribute to this project.

## Support

- Documentation: https://domd.readthedocs.io
- Issues: https://github.com/wronai/domd/issues
- Discussions: https://github.com/wronai/domd/discussions
