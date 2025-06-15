# Login API Tests with Ansible

This directory contains Ansible playbooks for testing the login functionality of the application.

## Prerequisites

- Python 3.6+
- Ansible 2.9+
- Running instance of the application

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update the `api_base_url` in `test_login.yml` to match your application's URL.

3. Update the test credentials in `test_login.yml` if needed:
   ```yaml
   test_username: "your_test_username"
   test_password: "your_test_password"
   ```

## Running the Tests

To run all login tests:

```bash
ansible-playbook test_login.yml -v
```

## Test Cases

The following test cases are included:

1. **Valid Login**
   - Tests successful authentication with valid credentials
   - Verifies that an access token is returned

2. **Invalid Credentials**
   - Tests authentication with invalid credentials
   - Verifies that a 401 Unauthorized response is received

3. **Missing Fields**
   - Tests authentication with missing required fields
   - Verifies that a 422 Unprocessable Entity response is received

## Debugging

To see detailed output, run the playbook with increased verbosity:

```bash
ansible-playbook test_login.yml -vvv
```

## Adding More Tests

To add more test cases, edit the `roles/login_test/tasks/main.yml` file and add additional tasks as needed.
