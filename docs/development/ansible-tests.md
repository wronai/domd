# Ansible Test Suite

This document provides detailed information about the Ansible test suite in DoMD, including how to write and run tests for Ansible-related functionality.

## Test Structure

The Ansible tests are organized into several modules, each focusing on different aspects of Ansible functionality:

- `test_ansible_playbook.py`: Tests for Ansible playbook detection and execution
- `test_ansible_roles.py`: Tests for Ansible role structure and functionality
- `test_ansible_galaxy.py`: Tests for Ansible Galaxy integration
- `test_ansible_vault.py`: Tests for Ansible Vault functionality
- `test_ansible_inventory.py`: Tests for Ansible inventory handling

## Writing Tests

### Test Fixtures

Use the following fixtures for Ansible testing:

- `ansible_playbook`: Creates a sample Ansible playbook with inventory
- `ansible_role`: Sets up a basic Ansible role structure
- `ansible_requirements`: Creates a sample `requirements.yml` file

### Example Test

```python
def test_playbook_execution(ansible_playbook):
    """Test execution of an Ansible playbook."""
    detector = ProjectCommandDetector(str(ansible_playbook.parent))
    commands = detector.scan_project()

    # Verify playbook was detected
    playbook_cmds = [c for c in commands if c.get('type') == 'ansible_playbook']
    assert len(playbook_cmds) > 0
```

## Running Tests

### Run All Ansible Tests

```bash
make test-ansible
```

### Run Specific Test Modules

```bash
# Test playbooks
make test-playbooks

# Test roles
make test-roles

# Test Galaxy integration
make test-galaxy

# Test Vault functionality
make test-vault

# Test inventory handling
make test-inventory
```

### Run with Coverage

```bash
pytest --cov=domd tests/test_ansible_*.py
```

## Test Dependencies

Ansible tests require:
- `ansible-core` >= 2.12.0
- `ansible-lint` >= 6.0.0
- `molecule` >= 4.0.0 (for integration tests)

## Debugging Tests

To debug test failures:

1. Run tests with `-v` for verbose output:
   ```bash
   pytest tests/test_ansible_playbook.py -v
   ```

2. Use `pdb` for interactive debugging:
   ```bash
   pytest tests/test_ansible_playbook.py -v --pdb
   ```

3. Check the test log in `test-results/ansible-tests.log`

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Mocks**: Mock external calls for unit tests
3. **Test Edge Cases**: Include tests for error conditions
4. **Keep Tests Fast**: Use appropriate test scopes
5. **Document Tests**: Include clear docstrings and comments
