# Documentation Structure

This file outlines the structure and organization of the DoMD documentation.

## Main Documentation Sections

1. **Getting Started**
   - Introduction
   - Installation
   - Quick Start
   - Basic Configuration

2. **User Guide**
   - Command Line Interface
   - Configuration Files
   - Command Detection
   - Command Execution
   - Report Generation
   - .doignore Management

3. **API Reference**
   - Core Modules
   - Command Handlers
   - Services
   - Adapters
   - Models

4. **Development**
   - Setup Development Environment
   - Architecture
   - Adding New Features
   - Testing
   - Contributing

5. **Examples**
   - Basic Usage
   - Advanced Scenarios
   - Integration Examples
   - CI/CD Integration

## Documentation Standards

- All documentation should be in Markdown format
- Use consistent heading levels
- Include code examples where applicable
- Link to related documentation
- Keep lines under 100 characters
- Use relative links for internal documentation

## Building the Documentation

To build the documentation locally:

```bash
# Install mkdocs and required extensions
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve the documentation locally
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.
