# Ansible Integration

DoMD provides comprehensive support for testing and validating Ansible projects. This includes detection and testing of playbooks, roles, inventories, and more.

## Supported Ansible Features

### Playbooks
- Detection of `*.yml` and `*.yaml` playbook files
- Support for playbooks with multiple plays
- Variable file detection and validation

### Roles
- Automatic role structure detection
- Role dependency resolution
- Task and handler validation

### Inventories
- Static inventory file parsing
- Dynamic inventory script support
- Group and host variable resolution

### Ansible Vault
- Detection of vault-encrypted files
- Integration with vault password files
- Support for `ansible-vault` commands

### Ansible Galaxy
- `requirements.yml` file parsing
- Role installation and management
- Collection support

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
