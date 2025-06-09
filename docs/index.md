# DoMD - Project Command Detector

<div align="center">

![DoMD Logo](assets/logo.png)

**Automated Project Command Detection and Testing with Advanced Ansible Support**

[![PyPI version](https://badge.fury.io/py/domd.svg)](https://badge.fury.io/py/domd)
[![Python Support](https://img.shields.io/pypi/pyversions/domd.svg)](https://pypi.org/project/domd/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/wronai/domd/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/wronai/domd/actions)
[![Coverage](https://codecov.io/gh/wronai/domd/branch/main/graph/badge.svg)](https://codecov.io/gh/wronai/domd)
[![Ansible](https://img.shields.io/badge/Ansible-Compatible-EE0000?logo=ansible)](https://www.ansible.com/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://domd.readthedocs.io/)

## 🚀 Enhanced Ansible Support

DoMD now includes comprehensive support for Ansible projects, with specialized handling for:

- **Playbooks**: Full detection and testing of complex playbook structures
- **Roles**: Complete role structure analysis and dependency resolution
- **Inventories**: Support for both static and dynamic inventories
- **Vault**: Secure handling of encrypted content
- **Galaxy**: Role and collection management

### Key Features

✅ **Comprehensive Test Coverage** - Unit and integration tests for all Ansible components
✅ **Intelligent Command Detection** - Accurate parsing of complex Ansible commands
✅ **Performance Optimized** - Caching and parallel execution for faster testing
✅ **Developer Friendly** - Detailed error reporting and debugging information

### Quick Start

```bash
# Install with Ansible support
pip install domd[ansible]

# Run Ansible tests
make test-ansible
```

Check out the [Ansible Integration](features/ansible.md) documentation for more details.

## 📚 Documentation

[![Documentation](https://readthedocs.org/projects/domd/
