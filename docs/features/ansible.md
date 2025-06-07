# Ansible Integration

DoMD provides comprehensive support for testing and validating Ansible projects. This includes detection and testing of playbooks, roles, inventories, and other Ansible components.

## Supported Ansible Features

### Playbooks
- Detection of `*.yml` and `*.yaml` playbook files
- Support for playbooks with multiple plays and complex structures
- Variable file detection and validation
- Playbook execution with proper environment handling

### Roles
- Automatic role structure detection
- Role metadata parsing from `meta/main.yml`
- Role dependency resolution and validation
- Task and handler file processing
- Default and custom role variables support

### Inventories
- Static inventory file parsing (INI and YAML formats)
- Dynamic inventory script execution and parsing
- Group and host variable resolution
- Support for inventory directories with `host_vars` and `group_vars`

### Ansible Vault
- Detection of vault-encrypted files
- Integration with vault password files
- Support for `ansible-vault` commands (encrypt, decrypt, view, etc.)
- Secure handling of sensitive data during testing

### Ansible Galaxy
- `requirements.yml` file parsing
- Role and collection dependency management
- Support for multiple Galaxy servers
- Version constraint handling

## Recent Improvements

### Enhanced Testing Framework
- Added comprehensive test coverage for all Ansible components
- Implemented mock-based testing for external dependencies
- Added fixtures for common Ansible project structures
- Improved error handling and reporting

### Command Detection
- More accurate detection of Ansible commands in project files
- Better handling of command arguments and options
- Support for custom Ansible configuration files
- Improved detection of playbook and role structures

### Performance Optimizations
- Caching of parsed Ansible content
- Parallel execution of independent tests
- Reduced overhead in command detection
- Memory usage optimizations for large projects

## Example Commands

```bash
# Run all Ansible tests
make test-ansible

# Test playbooks specifically
make test-playbooks

# Test role functionality
make test-roles

# Test Galaxy integration
make test-galaxy

# Test Vault functionality
make test-vault

# Test inventory handling
make test-inventory
```

## Configuration

Ansible testing can be configured using the following environment variables:

- `ANSIBLE_CONFIG`: Path to ansible.cfg (default: `./ansible.cfg`)
- `ANSIBLE_INVENTORY`: Path to inventory file (default: `inventory/`)
- `ANSIBLE_VAULT_PASSWORD_FILE`: Path to vault password file

## Best Practices

1. **Organize your tests**: Keep your test files organized by functionality
2. **Use fixtures**: Leverage the provided test fixtures for common Ansible structures
3. **Mock external calls**: Use mocking for external dependencies in unit tests
4. **Test different scenarios**: Include tests for error cases and edge conditions
5. **Keep tests fast**: Use appropriate test scopes and mocks to keep tests fast
