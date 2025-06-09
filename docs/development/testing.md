# Testing DoMD

This document provides information about running and writing tests for the DoMD project.

## Running Tests

### Run All Tests

```bash
make test
```

### Run Specific Test Types

```bash
# Unit tests only
make test-unit

# Integration tests
make test-integration

# Ansible tests
make test-ansible

# With coverage report
make test-cov
```

### Run with Tox

```bash
# Run all environments
tox

# Run specific environment
tox -e py310
```

## Writing Tests

### Test Organization

Tests are organized by functionality:

```
tests/
  ├── __init__.py
  ├── conftest.py
  ├── fixtures/
  ├── test_detector.py
  ├── test_cli.py
  └── test_ansible_*.py  # Ansible test modules
```

### Test Guidelines

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test interactions between components
3. **Ansible Tests**: Test Ansible-specific functionality
4. **Fixtures**: Use fixtures for common test data
5. **Mocks**: Use mocks for external dependencies

### Example Test

```python
def test_example():
    """Test example with assertions."""
    result = 1 + 1
    assert result == 2, "1 + 1 should equal 2"
```

## Continuous Integration

Tests are automatically run on:
- Push to any branch
- Pull requests
- Tags

## Test Coverage

To generate a coverage report:

```bash
make test-cov
```

This will generate an HTML report in `htmlcov/`.

## Debugging Tests

To debug test failures:

1. Run with `-v` for verbose output
2. Use `--pdb` to drop into debugger on failure
3. Check test logs in `test-results/`

## Best Practices

- Keep tests focused and fast
- Use descriptive test names
- Test edge cases and error conditions
- Keep test data minimal and focused
- Update tests when changing functionality
