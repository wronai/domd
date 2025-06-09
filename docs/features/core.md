# Core Features

DoMD provides a comprehensive set of features for detecting and managing project commands across various technologies.

## Supported Technologies

### Build Systems
- Make
- NPM/Yarn
- Python (setup.py, pyproject.toml, requirements.txt)
- Composer (PHP)
- Cargo (Rust)

### Containerization
- Docker
- Docker Compose

### Configuration Management
- **Ansible** (Playbooks, Roles, Inventories, Vault)
- Terraform (coming soon)

### Other
- Shell scripts
- Generic YAML/JSON/TOML/INI files

## Key Features

### Command Detection
- Automatic detection of executable commands in project files
- Support for multiple command formats and patterns
- Custom command pattern matching

### Command Execution
- Configurable timeouts
- Environment variable support
- Working directory handling
- Output capture and processing

### Error Handling
- Detailed error reporting
- Stack traces for debugging
- Suggestions for common issues

### Output Formats
- Markdown (default)
- JSON
- Plain text
- Custom templates

### Integration
- CI/CD pipeline ready
- Docker support
- Plugin system for extensibility

## Ansible Integration

DoMD provides first-class support for Ansible projects, including:

- Playbook detection and validation
- Role structure analysis
- Inventory parsing
- Vault integration
- Galaxy requirements management

See the [Ansible Integration](ansible.md) documentation for more details.

## Configuration

DoMD can be configured using:

1. Command-line arguments
2. Configuration files (`.domdrc`, `pyproject.toml`)
3. Environment variables

Example configuration in `pyproject.toml`:

```toml
[tool.domd]
timeout = 30
output = "markdown"
verbose = true

[tool.domd.ignore]
patterns = ["*test*", "*dev*"]

[tool.domd.ansible]
inventory = "inventory/production"
vault_password_file = ".vault_pass.txt"
```

## Best Practices

1. **Keep commands simple**: Each command should do one thing well
2. **Use meaningful names**: Make command purposes clear
3. **Document requirements**: Note any dependencies or prerequisites
4. **Test commands**: Verify commands work as expected
5. **Handle errors**: Provide helpful error messages
6. **Use configuration**: Leverage config files for project-specific settings
