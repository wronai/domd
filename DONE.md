# Successfully Executed Commands

## 1. Command from nodejs-example.md

**Command:** `cd my-node-app`
**Source:** docs/examples/basic/nodejs-example.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.00s

**Output:**
```
Changed directory to /home/tom/github/wronai/domd/my-node-app
```

**Metadata:**
- **line_number:** 19
- **file:** docs/examples/basic/nodejs-example.md

---

## 2. Command from nodejs-example.md

**Command:** `npm init -y`
**Source:** docs/examples/basic/nodejs-example.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.37s

**Output:**
```
Wrote to /home/tom/github/wronai/domd/package.json:

{
  "name": "domd",
  "version": "1.0.0",
  "description": "[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Tests](https://github.com/wronai/dom...
```

**Error Output:**
```
npm warn Unknown global config "python". This will stop working in the next major version of npm.

```

**Metadata:**
- **line_number:** 19
- **file:** docs/examples/basic/nodejs-example.md

---

## 3. Command from usage.md

**Command:** `pytest -xvs`
**Source:** docs/usage.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.84s

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.3, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/tom/github/wronai/domd
configfile: pyproject.toml
testpaths: tests
plugins: mock-3.14.1, cov-4.1.0, docker-2.2.0
collected 123 items

tests/test_ansible.py ...
tests/test_ansible_galaxy.py .....
tests/test_ansible_inventory.py ..s
tests/test_ansible_playbook.py ...
tests/test_ansible_roles.py ..
tests/test_ansible_vault.py ...
tests/test_dete...
```

**Error Output:**
```
DEBUG:domd.parsers:Parser modules to load: ['domd.parsers.ansible', 'domd.parsers.build_systems', 'domd.parsers.ci_cd', 'domd.parsers.docker', 'domd.parsers.javascript', 'domd.parsers.python', 'domd.parsers.markdown_parser']
DEBUG:docker.utils.config:Trying paths: ['/home/tom/.docker/config.json', '/home/tom/.dockercfg']
DEBUG:docker.utils.config:No config file found
DEBUG:docker.utils.config:Trying paths: ['/home/tom/.docker/config.json', '/home/tom/.dockercfg']
DEBUG:docker.utils.config:No con...
```

**Metadata:**
- **line_number:** 66
- **file:** docs/usage.md

---
