# Successfully Executed Commands

## 1. Test inventory: .dodocker

**Command:** `ansible all -i .dodocker -m ping`
**Source:** /home/tom/github/wronai/domd/.dodocker
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.64s

**Error Output:**
```
[WARNING]: Skipping key (image) in group (pytest) as it is not a mapping, it is
a <class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]: Skipping key (description) in group (pytest) as it is not a mapping,
it is a <class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]: Skipping key (image) in group (black) as it is not a mapping, it is
a <class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]: Skipping key (description) in group (black) as it is not a mapping,
it is a ...
```

**Metadata:**
- **inventory_type:** static
- **file:** .dodocker

---

## 2. Test inventory: .pre-commit-config.yaml

**Command:** `ansible all -i .pre-commit-config.yaml -m ping`
**Source:** /home/tom/github/wronai/domd/.pre-commit-config.yaml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.61s

**Error Output:**
```
[WARNING]: Skipping 'repos' as this is not a valid group definition
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** .pre-commit-config.yaml

---

## 3. Test inventory: 2.pre-commit-config.yaml

**Command:** `ansible all -i 2.pre-commit-config.yaml -m ping`
**Source:** /home/tom/github/wronai/domd/2.pre-commit-config.yaml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.45s

**Error Output:**
```
[WARNING]: Skipping 'repos' as this is not a valid group definition
[WARNING]: Skipping 'default_stages' as this is not a valid group definition
[WARNING]: Skipping 'stages' as this is not a valid group definition
[WARNING]: Skipping key (autofix_commit_msg) in group (ci) as it is not a
mapping, it is a <class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]: Skipping key (autofix_prs) in group (ci) as it is not a mapping, it
is a <class 'bool'>
[WARNING]: Skipping key (autoupdate_branch...
```

**Metadata:**
- **inventory_type:** static
- **file:** 2.pre-commit-config.yaml

---

## 4. Test inventory: CHANGELOG.md

**Command:** `ansible all -i CHANGELOG.md -m ping`
**Source:** /home/tom/github/wronai/domd/CHANGELOG.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.35s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/CHANGELOG.md with
script plugin: problem running /home/tom/github/wronai/domd/CHANGELOG.md --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/CHANGELOG.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/CHANGELOG.md with
ini plugin: /home/tom/github/wronai/domd/CHANGELOG.md:3: Expected key=value
host variable assignment, got: notable
[WARNING]: Unable to parse /home/tom/github/wronai/domd/CHANGELOG.md as an
i...
```

**Metadata:**
- **inventory_type:** static
- **file:** CHANGELOG.md

---

## 5. Test inventory: DONE.md

**Command:** `ansible all -i DONE.md -m ping`
**Source:** /home/tom/github/wronai/domd/DONE.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.65s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/DONE.md with script
plugin: problem running /home/tom/github/wronai/domd/DONE.md --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/DONE.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/DONE.md with ini
plugin: /home/tom/github/wronai/domd/DONE.md:5: Expected key=value host
variable assignment, got: `ansible
[WARNING]: Unable to parse /home/tom/github/wronai/domd/DONE.md as an inventory
source
[WARNING]: No...
```

**Metadata:**
- **inventory_type:** static
- **file:** DONE.md

---

## 6. Test inventory: Dockerfile

**Command:** `ansible all -i Dockerfile -m ping`
**Source:** /home/tom/github/wronai/domd/Dockerfile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.52s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/Dockerfile with
script plugin: problem running /home/tom/github/wronai/domd/Dockerfile --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/Dockerfile')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/Dockerfile with yaml
plugin: We were unable to read either as JSON nor YAML, these are the errors we
got from each: JSON: Expecting value: line 1 column 1 (char 0)  Syntax Error
while loading YAML.   did not find ex...
```

**Metadata:**
- **inventory_type:** static
- **file:** Dockerfile

---

## 7. Test inventory: LICENSE

**Command:** `ansible all -i LICENSE -m ping`
**Source:** /home/tom/github/wronai/domd/LICENSE
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.08s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/LICENSE with script
plugin: problem running /home/tom/github/wronai/domd/LICENSE --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/LICENSE')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/LICENSE with yaml
plugin: We were unable to read either as JSON nor YAML, these are the errors we
got from each: JSON: Expecting value: line 1 column 34 (char 33)  Syntax Error
while loading YAML.   mapping values are not al...
```

**Metadata:**
- **inventory_type:** static
- **file:** LICENSE

---

## 8. Test inventory: Makefile

**Command:** `ansible all -i Makefile -m ping`
**Source:** /home/tom/github/wronai/domd/Makefile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.36s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/Makefile with script
plugin: problem running /home/tom/github/wronai/domd/Makefile --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/Makefile')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/Makefile with yaml
plugin: We were unable to read either as JSON nor YAML, these are the errors we
got from each: JSON: Expecting value: line 1 column 1 (char 0)  Syntax Error
while loading YAML.   found a tab character t...
```

**Metadata:**
- **inventory_type:** static
- **file:** Makefile

---

## 9. Test inventory: README.md

**Command:** `ansible all -i README.md -m ping`
**Source:** /home/tom/github/wronai/domd/README.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.61s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/README.md with
script plugin: problem running /home/tom/github/wronai/domd/README.md --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/README.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/README.md with ini
plugin: not enough values to unpack (expected 3, got 2)
[WARNING]: Unable to parse /home/tom/github/wronai/domd/README.md as an
inventory source
[WARNING]: No inventory was parsed, only implicit loca...
```

**Metadata:**
- **inventory_type:** static
- **file:** README.md

---

## 10. Test inventory: START.md

**Command:** `ansible all -i START.md -m ping`
**Source:** /home/tom/github/wronai/domd/START.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.60s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/START.md with script
plugin: problem running /home/tom/github/wronai/domd/START.md --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/START.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/START.md with ini
plugin: /home/tom/github/wronai/domd/START.md:3: Expected key=value host
variable assignment, got: domd
[WARNING]: Unable to parse /home/tom/github/wronai/domd/START.md as an
inventory source
[WARNING]: ...
```

**Metadata:**
- **inventory_type:** static
- **file:** START.md

---

## 11. Test inventory: TODO.md

**Command:** `ansible all -i TODO.md -m ping`
**Source:** /home/tom/github/wronai/domd/TODO.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.48s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/TODO.md with script
plugin: problem running /home/tom/github/wronai/domd/TODO.md --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/TODO.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/TODO.md with ini
plugin: /home/tom/github/wronai/domd/TODO.md:5: Expected key=value host
variable assignment, got: `ansible
[WARNING]: Unable to parse /home/tom/github/wronai/domd/TODO.md as an inventory
source
[WARNING]: No...
```

**Metadata:**
- **inventory_type:** static
- **file:** TODO.md

---

## 12. Test inventory: TODO.txt

**Command:** `ansible all -i TODO.txt -m ping`
**Source:** /home/tom/github/wronai/domd/TODO.txt
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.35s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/TODO.txt with script
plugin: problem running /home/tom/github/wronai/domd/TODO.txt --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/TODO.txt')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/TODO.txt with ini
plugin: /home/tom/github/wronai/domd/TODO.txt:4: Expected key=value host
variable assignment, got: [x]
[WARNING]: Unable to parse /home/tom/github/wronai/domd/TODO.txt as an
inventory source
[WARNING]: N...
```

**Metadata:**
- **inventory_type:** static
- **file:** TODO.txt

---

## 13. Test inventory: ansible/ansible.cfg

**Command:** `ansible all -i ansible/ansible.cfg -m ping`
**Source:** /home/tom/github/wronai/domd/ansible/ansible.cfg
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.42s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/ansible/ansible.cfg
with script plugin: problem running
/home/tom/github/wronai/domd/ansible/ansible.cfg --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/ansible/ansible.cfg')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/ansible/ansible.cfg
with ini plugin: /home/tom/github/wronai/domd/ansible/ansible.cfg:3: Expected
key=value host variable assignment, got: inventory/
[WARNING]: Unable to parse /home/tom/g...
```

**Metadata:**
- **inventory_type:** static
- **file:** ansible/ansible.cfg

---

## 14. Install Ansible roles/collections from: ansible/requirements.yml

**Command:** `ansible-galaxy install -r ansible/requirements.yml`
**Source:** /home/tom/github/wronai/domd/ansible/requirements.yml
**Type:** ansible_galaxy
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.87s

**Output:**
```
Starting galaxy collection install process
Nothing to do. All requested collections are already installed. If you want to reinstall them, consider using `--force`.

```

**Metadata:**
- **file_type:** requirements
- **requirements:** [{'name': 'community.general', 'version': '6.6.0'}, {'name': 'ansible.posix', 'version': '1.5.4'}, {'name': 'community.docker', 'version': '3.8.1'}]
- **file:** ansible/requirements.yml

---

## 15. Test inventory: ansible/site.yml

**Command:** `ansible all -i ansible/site.yml -m ping`
**Source:** /home/tom/github/wronai/domd/ansible/site.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.33s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/ansible/site.yml
with script plugin: problem running
/home/tom/github/wronai/domd/ansible/site.yml --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/ansible/site.yml')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/ansible/site.yml
with auto plugin: no root 'plugin' key found,
'/home/tom/github/wronai/domd/ansible/site.yml' is not a valid YAML inventory
plugin config file
[WARNING]:  * Failed to parse /home/t...
```

**Metadata:**
- **inventory_type:** static
- **file:** ansible/site.yml

---

## 16. Test inventory: docker-test/Dockerfile

**Command:** `ansible all -i docker-test/Dockerfile -m ping`
**Source:** /home/tom/github/wronai/domd/docker-test/Dockerfile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.33s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/Dockerfile with script plugin: problem running
/home/tom/github/wronai/domd/docker-test/Dockerfile --list ([Errno 8] Exec
format error: '/home/tom/github/wronai/domd/docker-test/Dockerfile')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/Dockerfile with yaml plugin: We were unable to read either as JSON nor
YAML, these are the errors we got from each: JSON: Expecting value: line 1
column 1 (char 0)  ...
```

**Metadata:**
- **inventory_type:** static
- **file:** docker-test/Dockerfile

---

## 17. Test inventory: docker-test/test_domd.py

**Command:** `ansible all -i docker-test/test_domd.py -m ping`
**Source:** /home/tom/github/wronai/domd/docker-test/test_domd.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.12s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/test_domd.py with script plugin: problem running
/home/tom/github/wronai/domd/docker-test/test_domd.py --list ([Errno 8] Exec
format error: '/home/tom/github/wronai/domd/docker-test/test_domd.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/test_domd.py with ini plugin: /home/tom/github/wronai/domd/docker-
test/test_domd.py:1: Expected key=value host variable assignment, got: os
[WARNING]: Unable ...
```

**Metadata:**
- **inventory_type:** static
- **file:** docker-test/test_domd.py

---

## 18. Dynamic inventory: docker-test/test_install.sh

**Command:** `ansible-inventory -i docker-test/test_install.sh --list`
**Source:** /home/tom/github/wronai/domd/docker-test/test_install.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 5.66s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/test_install.sh with script plugin: Inventory script
(/home/tom/github/wronai/domd/docker-test/test_install.sh) had an execution
error: Error: [Errno 13] Permission denied:
'/home/tom/github/wronai/domd/.venv/bin/Activate.ps1'
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docker-
test/test_install.sh with ini plugin: /home/tom/github/wronai/domd/docker-
test/test_install.sh:2: Expected key=value host variable as...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** docker-test/test_install.sh

---

## 19. Command from DOCUMENTATION_STRUCTURE.md

**Command:** `pip install mkdocs mkdocs-material mkdocstrings[python]`
**Source:** docs/DOCUMENTATION_STRUCTURE.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.25s

**Output:**
```
Requirement already satisfied: mkdocs in ./.venv/lib/python3.12/site-packages (1.6.1)
Requirement already satisfied: mkdocs-material in ./.venv/lib/python3.12/site-packages (9.6.14)
Requirement already satisfied: mkdocstrings[python] in ./.venv/lib/python3.12/site-packages (0.29.1)
Requirement already satisfied: click>=7.0 in ./.venv/lib/python3.12/site-packages (from mkdocs) (8.2.1)
Requirement already satisfied: ghp-import>=1.0 in ./.venv/lib/python3.12/site-packages (from mkdocs) (2.1.0)
Requ...
```

**Metadata:**
- **line_number:** 54
- **file:** docs/DOCUMENTATION_STRUCTURE.md

---

## 20. Test inventory: docs/api.md

**Command:** `ansible all -i docs/api.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/api.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.83s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** docs/api.md

---

## 21. Test inventory: docs/development/ansible-tests.md

**Command:** `ansible all -i docs/development/ansible-tests.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/development/ansible-tests.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.29s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/development/ansible-tests.md with script
plugin: problem running /home/tom/github/wronai/domd/docs/development/ansible-
tests.md --list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/docs/development/ansible-tests.md')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/development/ansible-tests.md with ini plugin:
/home/tom/github/wronai/domd/docs/development/ansible-tests.md:3: Expected
key=value host vari...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/development/ansible-tests.md

---

## 22. Command from contributing.md

**Command:** `cd domd`
**Source:** docs/development/contributing.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.00s

**Output:**
```
Changed directory to /home/tom/github/wronai/domd/domd
```

**Metadata:**
- **line_number:** 44
- **file:** docs/development/contributing.md

---

## 23. Command from contributing.md

**Command:** `source venv/bin/activate  # On Windows: venv\Scripts\activate`
**Source:** docs/development/contributing.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.00s

**Metadata:**
- **line_number:** 44
- **file:** docs/development/contributing.md

---

## 24. Command from contributing.md

**Command:** `pip install -e ".[dev]"`
**Source:** docs/development/contributing.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 15.30s

**Output:**
```
Obtaining file:///home/tom/github/wronai/domd
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyp...
```

**Metadata:**
- **line_number:** 44
- **file:** docs/development/contributing.md

---

## 25. Command from contributing.md

**Command:** `pre-commit install`
**Source:** docs/development/contributing.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.61s

**Output:**
```
pre-commit installed at .git/hooks/pre-commit

```

**Metadata:**
- **line_number:** 44
- **file:** docs/development/contributing.md

---

## 26. Test inventory: docs/development/testing.md

**Command:** `ansible all -i docs/development/testing.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/development/testing.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.34s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/development/testing.md with script plugin:
problem running /home/tom/github/wronai/domd/docs/development/testing.md --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/docs/development/testing.md')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/development/testing.md with ini plugin:
/home/tom/github/wronai/domd/docs/development/testing.md:3: Expected key=value
host variable assignment, got: document
...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/development/testing.md

---

## 27. Test inventory: docs/domdignore.md

**Command:** `ansible all -i docs/domdignore.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/domdignore.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.27s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/domdignore.md
with script plugin: problem running
/home/tom/github/wronai/domd/docs/domdignore.md --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/docs/domdignore.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/domdignore.md
with ini plugin: /home/tom/github/wronai/domd/docs/domdignore.md:5: Expected
key=value host variable assignment, got: kompletny
[WARNING]: Unable to parse /home/tom/github/...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/domdignore.md

---

## 28. Test inventory: docs/done.md

**Command:** `ansible all -i docs/done.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/done.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.66s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/done.md with
script plugin: problem running /home/tom/github/wronai/domd/docs/done.md --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/docs/done.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/done.md with
ini plugin: /home/tom/github/wronai/domd/docs/done.md:3: Expected key=value
host variable assignment, got: Generated
[WARNING]: Unable to parse /home/tom/github/wronai/domd/docs/done.md as an...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/done.md

---

## 29. Command from nodejs-example.md

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

## 30. Command from nodejs-example.md

**Command:** `npm init -y`
**Source:** docs/examples/basic/nodejs-example.md
**Type:** shell
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.20s

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

## 31. Test inventory: docs/features/ansible.md

**Command:** `ansible all -i docs/features/ansible.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/features/ansible.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.83s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/features/ansible.md with script plugin:
problem running /home/tom/github/wronai/domd/docs/features/ansible.md --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/docs/features/ansible.md')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/features/ansible.md with ini plugin:
/home/tom/github/wronai/domd/docs/features/ansible.md:3: Expected key=value
host variable assignment, got: provides
[WARNING]: Unab...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/features/ansible.md

---

## 32. Test inventory: docs/features/core.md

**Command:** `ansible all -i docs/features/core.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/features/core.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.68s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/features/core.md with script plugin: problem
running /home/tom/github/wronai/domd/docs/features/core.md --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/docs/features/core.md')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/docs/features/core.md with ini plugin:
/home/tom/github/wronai/domd/docs/features/core.md:3: Expected key=value host
variable assignment, got: provides
[WARNING]: Unable to parse /ho...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/features/core.md

---

## 33. Test inventory: docs/how-to-llm.md

**Command:** `ansible all -i docs/how-to-llm.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/how-to-llm.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.69s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/how-to-llm.md
with script plugin: problem running /home/tom/github/wronai/domd/docs/how-to-
llm.md --list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/docs/how-to-llm.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/how-to-llm.md
with ini plugin: /home/tom/github/wronai/domd/docs/how-to-llm.md:5: Expected
key=value host variable assignment, got: kompletny
[WARNING]: Unable to parse /home/tom/github...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/how-to-llm.md

---

## 34. Test inventory: docs/installation.md

**Command:** `ansible all -i docs/installation.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/installation.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.39s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/installation.md
with script plugin: problem running
/home/tom/github/wronai/domd/docs/installation.md --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/docs/installation.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/installation.md
with ini plugin: /home/tom/github/wronai/domd/docs/installation.md:5: Expected
key=value host variable assignment, got: Python
[WARNING]: Unable to parse /home/tom/...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/installation.md

---

## 35. Test inventory: docs/mkdocs.yml

**Command:** `ansible all -i docs/mkdocs.yml -m ping`
**Source:** /home/tom/github/wronai/domd/docs/mkdocs.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.61s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/mkdocs.yml with
script plugin: problem running /home/tom/github/wronai/domd/docs/mkdocs.yml
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/docs/mkdocs.yml')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/mkdocs.yml with
auto plugin: We were unable to read either as JSON nor YAML, these are the
errors we got from each: JSON: Expecting value: line 1 column 1 (char 0)
Syntax Error while loading YAML...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/mkdocs.yml

---

## 36. Test inventory: docs/todo.md

**Command:** `ansible all -i docs/todo.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/todo.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.58s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/todo.md with
script plugin: problem running /home/tom/github/wronai/domd/docs/todo.md --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/docs/todo.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/todo.md with
ini plugin: /home/tom/github/wronai/domd/docs/todo.md:3: Expected key=value
host variable assignment, got: INSTRUCTIONS
[WARNING]: Unable to parse /home/tom/github/wronai/domd/docs/todo.md as...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/todo.md

---

## 37. Test inventory: docs/usage.old.md

**Command:** `ansible all -i docs/usage.old.md -m ping`
**Source:** /home/tom/github/wronai/domd/docs/usage.old.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.71s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/usage.old.md
with script plugin: problem running
/home/tom/github/wronai/domd/docs/usage.old.md --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/docs/usage.old.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/docs/usage.old.md
with ini plugin: /home/tom/github/wronai/domd/docs/usage.old.md:5: Expected
key=value host variable assignment, got: na
[WARNING]: Unable to parse /home/tom/github/wronai/domd/...
```

**Metadata:**
- **inventory_type:** static
- **file:** docs/usage.old.md

---

## 38. Test inventory: dodocker.md

**Command:** `ansible all -i dodocker.md -m ping`
**Source:** /home/tom/github/wronai/domd/dodocker.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 4.13s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/dodocker.md with
script plugin: problem running /home/tom/github/wronai/domd/dodocker.md --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/dodocker.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/dodocker.md with ini
plugin: /home/tom/github/wronai/domd/dodocker.md:4: Expected key=value host
variable assignment, got: `.dodocker`
[WARNING]: Unable to parse /home/tom/github/wronai/domd/dodocker.md as an
inv...
```

**Metadata:**
- **inventory_type:** static
- **file:** dodocker.md

---

## 39. Test inventory: examples/DONE.md

**Command:** `ansible all -i examples/DONE.md -m ping`
**Source:** /home/tom/github/wronai/domd/examples/DONE.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.44s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/DONE.md
with script plugin: problem running
/home/tom/github/wronai/domd/examples/DONE.md --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/examples/DONE.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/DONE.md
with ini plugin: /home/tom/github/wronai/domd/examples/DONE.md:3: Expected
key=value host variable assignment, got: commands
[WARNING]: Unable to parse /home/tom/github/wronai/domd...
```

**Metadata:**
- **inventory_type:** static
- **file:** examples/DONE.md

---

## 40. Test inventory: examples/Makefile

**Command:** `ansible all -i examples/Makefile -m ping`
**Source:** /home/tom/github/wronai/domd/examples/Makefile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.05s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/Makefile
with script plugin: problem running
/home/tom/github/wronai/domd/examples/Makefile --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/examples/Makefile')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/Makefile
with yaml plugin: YAML inventory has invalid structure, it should be a
dictionary, got: <class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]:  * Failed to parse /hom...
```

**Metadata:**
- **inventory_type:** static
- **file:** examples/Makefile

---

## 41. Test inventory: examples/TODO.md

**Command:** `ansible all -i examples/TODO.md -m ping`
**Source:** /home/tom/github/wronai/domd/examples/TODO.md
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.36s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/TODO.md
with script plugin: problem running
/home/tom/github/wronai/domd/examples/TODO.md --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/examples/TODO.md')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/TODO.md
with ini plugin: /home/tom/github/wronai/domd/examples/TODO.md:5: Expected
key=value host variable assignment, got: `make
[WARNING]: Unable to parse /home/tom/github/wronai/domd/ex...
```

**Metadata:**
- **inventory_type:** static
- **file:** examples/TODO.md

---

## 42. Test inventory: examples/docker/Dockerfile

**Command:** `ansible all -i examples/docker/Dockerfile -m ping`
**Source:** /home/tom/github/wronai/domd/examples/docker/Dockerfile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.40s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/examples/docker/Dockerfile with script plugin:
problem running /home/tom/github/wronai/domd/examples/docker/Dockerfile --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/examples/docker/Dockerfile')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/examples/docker/Dockerfile with yaml plugin: YAML
inventory has invalid structure, it should be a dictionary, got: <class
'ansible.parsing.yaml.objects.AnsibleUnicode'...
```

**Metadata:**
- **inventory_type:** static
- **file:** examples/docker/Dockerfile

---

## 43. Test inventory: examples/javascript/package.json

**Command:** `ansible all -i examples/javascript/package.json -m ping`
**Source:** /home/tom/github/wronai/domd/examples/javascript/package.json
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.41s

**Error Output:**
```
[WARNING]: Skipping 'name' as this is not a valid group definition
[WARNING]: Skipping key (test) in group (scripts) as it is not a mapping, it is
a <class 'str'>
[WARNING]: Skipping key (build) in group (scripts) as it is not a mapping, it
is a <class 'str'>
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** examples/javascript/package.json

---

## 44. Test inventory: examples/package.json

**Command:** `ansible all -i examples/package.json -m ping`
**Source:** /home/tom/github/wronai/domd/examples/package.json
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.63s

**Error Output:**
```
[WARNING]: Skipping 'name' as this is not a valid group definition
[WARNING]: Skipping key (test) in group (scripts) as it is not a mapping, it is
a <class 'str'>
[WARNING]: Skipping key (build) in group (scripts) as it is not a mapping, it
is a <class 'str'>
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** examples/package.json

---

## 45. Dynamic inventory: examples/todo.sh

**Command:** `ansible-inventory -i examples/todo.sh --list`
**Source:** /home/tom/github/wronai/domd/examples/todo.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.94s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/todo.sh
with script plugin: failed to parse executable inventory script results from
/home/tom/github/wronai/domd/examples/todo.sh: Expecting value: line 1 column 1
(char 0). Expecting value: line 1 column 1 (char 0)
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/examples/todo.sh
with ini plugin: /home/tom/github/wronai/domd/examples/todo.sh:5: Expected
key=value host variable assignment, got: -e
[WARNING]: Unable to...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** examples/todo.sh

---

## 46. Test inventory: mkdocs.yml

**Command:** `ansible all -i mkdocs.yml -m ping`
**Source:** /home/tom/github/wronai/domd/mkdocs.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.51s

**Error Output:**
```
[WARNING]: Skipping 'site_name' as this is not a valid group definition
[WARNING]: Skipping 'site_description' as this is not a valid group definition
[WARNING]: Skipping 'site_author' as this is not a valid group definition
[WARNING]: Skipping key (name) in group (theme) as it is not a mapping, it is a
<class 'ansible.parsing.yaml.objects.AnsibleUnicode'>
[WARNING]: Skipping key (highlightjs) in group (theme) as it is not a mapping,
it is a <class 'bool'>
[WARNING]: Skipping key (include_search...
```

**Metadata:**
- **inventory_type:** static
- **file:** mkdocs.yml

---

## 47. Test inventory: poetry.lock

**Command:** `ansible all -i poetry.lock -m ping`
**Source:** /home/tom/github/wronai/domd/poetry.lock
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.84s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/poetry.lock with
script plugin: problem running /home/tom/github/wronai/domd/poetry.lock --list
([Errno 8] Exec format error: '/home/tom/github/wronai/domd/poetry.lock')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/poetry.lock with ini
plugin: /home/tom/github/wronai/domd/poetry.lock:3: Invalid section entry:
'[[package]]'. Please make sure that there are no spaces in the section entry,
and that there are no other invalid c...
```

**Metadata:**
- **inventory_type:** static
- **file:** poetry.lock

---

## 48. Test inventory: pyproject.toml

**Command:** `ansible all -i pyproject.toml -m ping`
**Source:** /home/tom/github/wronai/domd/pyproject.toml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.12s

**Error Output:**
```
[WARNING]: Invalid characters were found in group names but not replaced, use
-vvvv to see details
[WARNING]: Skipping unexpected key "poetry" in group "tool", only "vars",
"children" and "hosts" are valid
[WARNING]: Skipping unexpected key "black" in group "tool", only "vars",
"children" and "hosts" are valid
[WARNING]: Skipping unexpected key "isort" in group "tool", only "vars",
"children" and "hosts" are valid
[WARNING]: Skipping unexpected key "mypy" in group "tool", only "vars",
"children"...
```

**Metadata:**
- **inventory_type:** static
- **file:** pyproject.toml

---

## 49. Dynamic inventory: scripts/check_version.py

**Command:** `ansible-inventory -i scripts/check_version.py --list`
**Source:** /home/tom/github/wronai/domd/scripts/check_version.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.09s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/check_version.py with script plugin:
Inventory script (/home/tom/github/wronai/domd/scripts/check_version.py) had an
execution error: Traceback (most recent call last):   File
"/home/tom/github/wronai/domd/scripts/check_version.py", line 11, in <module>
import toml ModuleNotFoundError: No module named 'toml'
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/check_version.py with ini plugin:
/home/tom/github/wrona...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** scripts/check_version.py

---

## 50. Test inventory: scripts/publish.sh

**Command:** `ansible all -i scripts/publish.sh -m ping`
**Source:** /home/tom/github/wronai/domd/scripts/publish.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.05s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/scripts/publish.sh
with script plugin: problem running
/home/tom/github/wronai/domd/scripts/publish.sh --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/scripts/publish.sh')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/scripts/publish.sh
with ini plugin: /home/tom/github/wronai/domd/scripts/publish.sh:2: Expected
key=value host variable assignment, got: install
[WARNING]: Unable to parse /home/tom/github/wr...
```

**Metadata:**
- **inventory_type:** static
- **file:** scripts/publish.sh

---

## 51. Dynamic inventory: scripts/test_commands.sh

**Command:** `ansible-inventory -i scripts/test_commands.sh --list`
**Source:** /home/tom/github/wronai/domd/scripts/test_commands.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.25s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/test_commands.sh with script plugin:
failed to parse executable inventory script results from
/home/tom/github/wronai/domd/scripts/test_commands.sh: Expecting value: line 2
column 1 (char 1). Expecting value: line 2 column 1 (char 1)
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/test_commands.sh with ini plugin:
/home/tom/github/wronai/domd/scripts/test_commands.sh:5: Expected key=value
host variable assignme...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** scripts/test_commands.sh

---

## 52. Dynamic inventory: scripts/test_commands_in_docker.py

**Command:** `ansible-inventory -i scripts/test_commands_in_docker.py --list`
**Source:** /home/tom/github/wronai/domd/scripts/test_commands_in_docker.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.13s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/test_commands_in_docker.py with script
plugin: failed to parse executable inventory script results from
/home/tom/github/wronai/domd/scripts/test_commands_in_docker.py: Expecting
value: line 2 column 1 (char 1). Expecting value: line 2 column 1 (char 1)
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/scripts/test_commands_in_docker.py with ini
plugin: /home/tom/github/wronai/domd/scripts/test_commands_in_docker.py:2:
E...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** scripts/test_commands_in_docker.py

---

## 53. Test inventory: setup.cfg

**Command:** `ansible all -i setup.cfg -m ping`
**Source:** /home/tom/github/wronai/domd/setup.cfg
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.90s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/setup.cfg with ini
plugin: /home/tom/github/wronai/domd/setup.cfg:2: Expected key=value host
variable assignment, got: domd
[WARNING]: Unable to parse /home/tom/github/wronai/domd/setup.cfg as an
inventory source
[WARNING]: No inventory was parsed, only implicit localhost is available
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** setup.cfg

---

## 54. Test inventory: site/mkdocs.yml

**Command:** `ansible all -i site/mkdocs.yml -m ping`
**Source:** /home/tom/github/wronai/domd/site/mkdocs.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.91s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/site/mkdocs.yml with
auto plugin: We were unable to read either as JSON nor YAML, these are the
errors we got from each: JSON: Expecting value: line 1 column 1 (char 0)
Syntax Error while loading YAML.   could not determine a constructor for the
tag 'tag:yaml.org,2002:python/name:materialx.emoji.twemoji'. could not
determine a constructor for the tag
'tag:yaml.org,2002:python/name:materialx.emoji.twemoji'   in "<unicode
string>", line 16...
```

**Metadata:**
- **inventory_type:** static
- **file:** site/mkdocs.yml

---

## 55. Test inventory: src/domd/__init__.py

**Command:** `ansible all -i src/domd/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.91s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/__init__.py
with script plugin: problem running
/home/tom/github/wronai/domd/src/domd/__init__.py --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/src/domd/__init__.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/__init__.py
with ini plugin: /home/tom/github/wronai/domd/src/domd/__init__.py:1: Error
parsing host definition '"""': No closing quotation
[WARNING]: Unable to parse /home/tom...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/__init__.py

---

## 56. Test inventory: src/domd/adapters/__init__.py

**Command:** `ansible all -i src/domd/adapters/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.30s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/__init__.py

---

## 57. Test inventory: src/domd/adapters/api/__init__.py

**Command:** `ansible all -i src/domd/adapters/api/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/api/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.97s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/api/__init__.py

---

## 58. Test inventory: src/domd/adapters/api/flask_api.py

**Command:** `ansible all -i src/domd/adapters/api/flask_api.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.96s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/adapters/api/flask_api.py:1:
Error parsing host defin...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/api/flask_api.py

---

## 59. Test inventory: src/domd/adapters/cli/__init__.py

**Command:** `ansible all -i src/domd/adapters/cli/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/cli/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.21s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/cli/__init__.py

---

## 60. Test inventory: src/domd/adapters/cli/command_presenter.py

**Command:** `ansible all -i src/domd/adapters/cli/command_presenter.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/cli/command_presenter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.50s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/cli/command_presenter.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/adapters/cli/command_presenter.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/adapters/cli/command_presenter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/cli/command_presenter.py with
ini plugin:
/home/tom/github/wronai/domd/src/domd/adapters/cli/command_...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/cli/command_presenter.py

---

## 61. Test inventory: src/domd/adapters/formatters/__init__.py

**Command:** `ansible all -i src/domd/adapters/formatters/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/formatters/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.84s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/formatters/__init__.py

---

## 62. Test inventory: src/domd/adapters/formatters/markdown_formatter.py

**Command:** `ansible all -i src/domd/adapters/formatters/markdown_formatter.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/formatters/markdown_formatter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.15s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/formatters/markdown_formatter.py
with script plugin: problem running
/home/tom/github/wronai/domd/src/domd/adapters/formatters/markdown_formatter.py
--list ([Errno 8] Exec format error: '/home/tom/github/wronai/domd/src/domd/ada
pters/formatters/markdown_formatter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/adapters/formatters/markdown_formatter.py
with ini plugin: /home/tom/github/wronai/do...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/formatters/markdown_formatter.py

---

## 63. Test inventory: src/domd/adapters/persistence/__init__.py

**Command:** `ansible all -i src/domd/adapters/persistence/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/persistence/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.89s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/persistence/__init__.py

---

## 64. Test inventory: src/domd/adapters/persistence/in_memory_command_repository.py

**Command:** `ansible all -i src/domd/adapters/persistence/in_memory_command_repository.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/persistence/in_memory_command_repository.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.49s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/adapters/pe
rsistence/in_memory_command_repository.py with script plugin: problem running /
home/tom/github/wronai/domd/src/domd/adapters/persistence/in_memory_command_rep
ository.py --list ([Errno 8] Exec format error: '/home/tom/github/wronai/domd/s
rc/domd/adapters/persistence/in_memory_command_repository.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/adapters/pe
rsistence/in_memory_command_repositor...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/persistence/in_memory_command_repository.py

---

## 65. Test inventory: src/domd/adapters/persistence/shell_command_executor.py

**Command:** `ansible all -i src/domd/adapters/persistence/shell_command_executor.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/adapters/persistence/shell_command_executor.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.59s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/adapters/pe
rsistence/shell_command_executor.py with script plugin: problem running /home/t
om/github/wronai/domd/src/domd/adapters/persistence/shell_command_executor.py
--list ([Errno 8] Exec format error: '/home/tom/github/wronai/domd/src/domd/ada
pters/persistence/shell_command_executor.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/adapters/pe
rsistence/shell_command_executor.py with ini plugin: /ho...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/adapters/persistence/shell_command_executor.py

---

## 66. Dynamic inventory: src/domd/api.py

**Command:** `ansible-inventory -i src/domd/api.py --list`
**Source:** /home/tom/github/wronai/domd/src/domd/api.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.73s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/api.py with
script plugin: Inventory script (/home/tom/github/wronai/domd/src/domd/api.py)
had an execution error: Traceback (most recent call last):   File
"/home/tom/github/wronai/domd/src/domd/api.py", line 11, in <module>     from
.adapters.api.flask_api import DomdFlaskApi ImportError: attempted relative
import with no known parent package
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/api.py with
ini p...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** src/domd/api.py

---

## 67. Test inventory: src/domd/application/__init__.py

**Command:** `ansible all -i src/domd/application/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/application/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.90s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/application/__init__.py

---

## 68. Test inventory: src/domd/application/factory.py

**Command:** `ansible all -i src/domd/application/factory.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/application/factory.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.98s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/application/factory.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/application/factory.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/application/factory.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/application/factory.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/application/factory.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/application/factory.py

---

## 69. Dynamic inventory: src/domd/cli.py

**Command:** `ansible-inventory -i src/domd/cli.py --list`
**Source:** /home/tom/github/wronai/domd/src/domd/cli.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.86s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/cli.py with
script plugin: Inventory script (/home/tom/github/wronai/domd/src/domd/cli.py)
had an execution error: Traceback (most recent call last):   File
"/home/tom/github/wronai/domd/src/domd/cli.py", line 17, in <module>     from .
import __version__ ImportError: attempted relative import with no known parent
package
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/src/domd/cli.py with
ini plugin: /home/tom/github...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** src/domd/cli.py

---

## 70. Test inventory: src/domd/command_execution/__init__.py

**Command:** `ansible all -i src/domd/command_execution/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/command_execution/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.50s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/command_execution/__init__.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/command_execution/__init__.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/command_execution/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/command_execution/__init__.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/command_execution/__init__.py:1:
Erro...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/command_execution/__init__.py

---

## 71. Test inventory: src/domd/core/__init__.py

**Command:** `ansible all -i src/domd/core/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.17s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/__init__.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/core/__init__.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/__init__.py:1: Error parsing host
definition '"""': No closing quotation
[WARNING]: ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/__init__.py

---

## 72. Test inventory: src/domd/core/command_execution/__init__.py

**Command:** `ansible all -i src/domd/core/command_execution/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/command_execution/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.74s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/command_execution/__init__.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/command_execution/__init__.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/command_execution/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/command_execution/__init__.py with
ini plugin:
/home/tom/github/wronai/domd/src/domd/core/command_exec...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/command_execution/__init__.py

---

## 73. Test inventory: src/domd/core/detector.py

**Command:** `ansible all -i src/domd/core/detector.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/detector.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.03s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/detector.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/core/detector.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/detector.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/detector.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/detector.py:1: Error parsing host
definition '"""Project command detector for findin...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/detector.py

---

## 74. Test inventory: src/domd/core/domain/__init__.py

**Command:** `ansible all -i src/domd/core/domain/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/domain/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.60s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/domain/__init__.py

---

## 75. Test inventory: src/domd/core/domain/command.py

**Command:** `ansible all -i src/domd/core/domain/command.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/domain/command.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.42s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/domain/command.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/domain/command.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/domain/command.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/domain/command.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/domain/command.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/domain/command.py

---

## 76. Test inventory: src/domd/core/parsing/__init__.py

**Command:** `ansible all -i src/domd/core/parsing/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.74s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/parsing/__init__.py:1: Error parsing
host definition...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/parsing/__init__.py

---

## 77. Test inventory: src/domd/core/ports/__init__.py

**Command:** `ansible all -i src/domd/core/ports/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/ports/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.53s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/ports/__init__.py

---

## 78. Test inventory: src/domd/core/ports/command_executor.py

**Command:** `ansible all -i src/domd/core/ports/command_executor.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.59s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/core/ports/command_executor.py:1:...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/ports/command_executor.py

---

## 79. Test inventory: src/domd/core/ports/command_repository.py

**Command:** `ansible all -i src/domd/core/ports/command_repository.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/ports/command_repository.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.56s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/command_repository.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/ports/command_repository.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/ports/command_repository.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/command_repository.py with ini
plugin:
/home/tom/github/wronai/domd/src/domd/core/ports/command_reposi...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/ports/command_repository.py

---

## 80. Test inventory: src/domd/core/ports/report_formatter.py

**Command:** `ansible all -i src/domd/core/ports/report_formatter.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.75s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/core/ports/report_formatter.py:1:...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/ports/report_formatter.py

---

## 81. Test inventory: src/domd/core/reporting/__init__.py

**Command:** `ansible all -i src/domd/core/reporting/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.42s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/core/reporting/__init__.py:1:
Error parsing host ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/reporting/__init__.py

---

## 82. Test inventory: src/domd/core/services/__init__.py

**Command:** `ansible all -i src/domd/core/services/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/services/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.26s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/services/__init__.py

---

## 83. Test inventory: src/domd/core/services/command_service.py

**Command:** `ansible all -i src/domd/core/services/command_service.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/services/command_service.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.54s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/services/command_service.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/services/command_service.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/services/command_service.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/services/command_service.py with ini
plugin:
/home/tom/github/wronai/domd/src/domd/core/services/command_ser...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/services/command_service.py

---

## 84. Test inventory: src/domd/core/services/report_service.py

**Command:** `ansible all -i src/domd/core/services/report_service.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/services/report_service.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.43s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/services/report_service.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/services/report_service.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/services/report_service.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/services/report_service.py with ini
plugin:
/home/tom/github/wronai/domd/src/domd/core/services/report_service....
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/services/report_service.py

---

## 85. Test inventory: src/domd/core/utils/__init__.py

**Command:** `ansible all -i src/domd/core/utils/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/utils/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.29s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/__init__.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/utils/__init__.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/utils/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/utils/__init__.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/utils/__init__.py

---

## 86. Test inventory: src/domd/core/utils/command_utils.py

**Command:** `ansible all -i src/domd/core/utils/command_utils.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.23s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/core/utils/command_utils.py:1:
Error parsing ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/utils/command_utils.py

---

## 87. Test inventory: src/domd/core/utils/file_utils.py

**Command:** `ansible all -i src/domd/core/utils/file_utils.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.22s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/core/utils/file_utils.py:1: Error parsing
host definition...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/core/utils/file_utils.py

---

## 88. Test inventory: src/domd/parsers/__init__.py

**Command:** `ansible all -i src/domd/parsers/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.44s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/__init__.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/__init__.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/__init__.py:1: Error parsing host
definition '"""Parsers package for ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/__init__.py

---

## 89. Test inventory: src/domd/parsers/base.py

**Command:** `ansible all -i src/domd/parsers/base.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/base.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.04s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/base.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/base.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/base.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/base.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/base.py:2: Error parsing host
definition '"""': No closing quotation
[WARNING]: Unabl...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/base.py

---

## 90. Test inventory: src/domd/parsers/ci_cd.py

**Command:** `ansible all -i src/domd/parsers/ci_cd.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.04s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/ci_cd.py:1: Error parsing host
definition '"""CI/CD workflow parsers for backward...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/ci_cd.py

---

## 91. Test inventory: src/domd/parsers/docker.py

**Command:** `ansible all -i src/domd/parsers/docker.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/docker.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.51s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/docker.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/docker.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/docker.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/docker.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/docker.py:2: Error parsing host
definition '"""': No closing quotation
[WARNI...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/docker.py

---

## 92. Test inventory: src/domd/parsers/javascript.py

**Command:** `ansible all -i src/domd/parsers/javascript.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/javascript.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.34s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/javascript.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/javascript.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/javascript.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/javascript.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/javascript.py:2: Error parsing
host definition '"""': No clos...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/javascript.py

---

## 93. Test inventory: src/domd/parsers/test_ci_cd.py

**Command:** `ansible all -i src/domd/parsers/test_ci_cd.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.47s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/test_ci_cd.py:1: Error parsing
host definition '"""': No clos...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/test_ci_cd.py

---

## 94. Test inventory: src/domd/parsers/test_docker.py

**Command:** `ansible all -i src/domd/parsers/test_docker.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/test_docker.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.57s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_docker.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/parsers/test_docker.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/test_docker.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_docker.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/test_docker.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/test_docker.py

---

## 95. Test inventory: src/domd/parsers/test_javascript.py

**Command:** `ansible all -i src/domd/parsers/test_javascript.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.49s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/parsers/test_javascript.py:1:
Error parsing host ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/test_javascript.py

---

## 96. Test inventory: src/domd/parsers/test_python.py

**Command:** `ansible all -i src/domd/parsers/test_python.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsers/test_python.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.35s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_python.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/parsers/test_python.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsers/test_python.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsers/test_python.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsers/test_python.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsers/test_python.py

---

## 97. Test inventory: src/domd/parsing/__init__.py

**Command:** `ansible all -i src/domd/parsing/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/parsing/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.50s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsing/__init__.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/parsing/__init__.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/parsing/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/parsing/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/parsing/__init__.py:1: Error parsing host
definition '"""': No closing quotat...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/parsing/__init__.py

---

## 98. Test inventory: src/domd/reporters/console.py

**Command:** `ansible all -i src/domd/reporters/console.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/console.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.16s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/console.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/reporters/console.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/console.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/console.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/reporters/console.py:2: Error parsing
host definition '"""': No closing q...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/console.py

---

## 99. Test inventory: src/domd/reporters/json_reporter.py

**Command:** `ansible all -i src/domd/reporters/json_reporter.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.39s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/reporters/json_reporter.py:2:
Error parsing host ...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/json_reporter.py

---

## 100. Test inventory: src/domd/reporters/test_console.py

**Command:** `ansible all -i src/domd/reporters/test_console.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/test_console.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.43s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_console.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/reporters/test_console.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/test_console.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_console.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/reporters/test_console.py:1:
Error parsing host defin...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/test_console.py

---

## 101. Test inventory: src/domd/reporters/test_json_reporter.py

**Command:** `ansible all -i src/domd/reporters/test_json_reporter.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.92s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter.py with
script plugin: problem running
/home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter.py with ini
plugin:
/home/tom/github/wronai/domd/src/domd/reporters/test_json_reporter....
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/test_json_reporter.py

---

## 102. Test inventory: src/domd/reporters/test_todo_md.py

**Command:** `ansible all -i src/domd/reporters/test_todo_md.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.89s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/reporters/test_todo_md.py:1:
Error parsing host defin...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/test_todo_md.py

---

## 103. Test inventory: src/domd/reporters/todo_md.py

**Command:** `ansible all -i src/domd/reporters/todo_md.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporters/todo_md.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.26s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/todo_md.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/reporters/todo_md.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporters/todo_md.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporters/todo_md.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/reporters/todo_md.py:1: Error parsing
host definition '"""': No closing q...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporters/todo_md.py

---

## 104. Test inventory: src/domd/reporting/__init__.py

**Command:** `ansible all -i src/domd/reporting/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/reporting/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.06s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporting/__init__.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/reporting/__init__.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/reporting/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/reporting/__init__.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/reporting/__init__.py:1: Error parsing
host definition '"""': No clos...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/reporting/__init__.py

---

## 105. Test inventory: src/domd/utils/command_runner.py

**Command:** `ansible all -i src/domd/utils/command_runner.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/utils/command_runner.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.85s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/command_runner.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/utils/command_runner.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/src/domd/utils/command_runner.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/command_runner.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/utils/command_runner.py:2: Error parsing
host definition '"""...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/utils/command_runner.py

---

## 106. Test inventory: src/domd/utils/file_utils.py

**Command:** `ansible all -i src/domd/utils/file_utils.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/utils/file_utils.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.03s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/file_utils.py with script plugin:
problem running /home/tom/github/wronai/domd/src/domd/utils/file_utils.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/utils/file_utils.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/file_utils.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/utils/file_utils.py:2: Error parsing host
definition '"""': No closing quotat...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/utils/file_utils.py

---

## 107. Test inventory: src/domd/utils/test_command_runner.py

**Command:** `ansible all -i src/domd/utils/test_command_runner.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.89s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py with ini
plugin: /home/tom/github/wronai/domd/src/domd/utils/test_command_runner.py:1:
Error par...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/utils/test_command_runner.py

---

## 108. Test inventory: src/domd/utils/test_file_utils.py

**Command:** `ansible all -i src/domd/utils/test_file_utils.py -m ping`
**Source:** /home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.03s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py with script
plugin: problem running
/home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py with ini plugin:
/home/tom/github/wronai/domd/src/domd/utils/test_file_utils.py:1: Error parsing
host definition...
```

**Metadata:**
- **inventory_type:** static
- **file:** src/domd/utils/test_file_utils.py

---

## 109. Dynamic inventory: test_in_docker.sh

**Command:** `ansible-inventory -i test_in_docker.sh --list`
**Source:** /home/tom/github/wronai/domd/test_in_docker.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.41s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    },
    "ungrouped": {
        "hosts": [
            "IGNORE_FILE=.doignore"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/test_in_docker.sh
with script plugin: failed to parse executable inventory script results from
/home/tom/github/wronai/domd/test_in_docker.sh: Expecting value: line 1 column
1 (char 0). Expecting value: line 1 column 1 (char 0)
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/test_in_docker.sh
with ini plugin: /home/tom/github/wronai/domd/test_in_docker.sh:5: Expected
key=value host variable assignment, got: $IGNORE_FILE
[WARNI...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** test_in_docker.sh

---

## 110. Test inventory: tests/ansible/roles/login_test/tasks/main.yml

**Command:** `ansible all -i tests/ansible/roles/login_test/tasks/main.yml -m ping`
**Source:** /home/tom/github/wronai/domd/tests/ansible/roles/login_test/tasks/main.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.21s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/ansible/roles/login_test/tasks/main.yml with
auto plugin: no root 'plugin' key found,
'/home/tom/github/wronai/domd/tests/ansible/roles/login_test/tasks/main.yml' is
not a valid YAML inventory plugin config file
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/ansible/roles/login_test/tasks/main.yml with
yaml plugin: YAML inventory has invalid structure, it should be a dictionary,
got: <class 'ansible.parsing.yaml.o...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/ansible/roles/login_test/tasks/main.yml

---

## 111. Test inventory: tests/ansible/test_login.yml

**Command:** `ansible all -i tests/ansible/test_login.yml -m ping`
**Source:** /home/tom/github/wronai/domd/tests/ansible/test_login.yml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.90s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/ansible/test_login.yml with auto plugin: no
root 'plugin' key found,
'/home/tom/github/wronai/domd/tests/ansible/test_login.yml' is not a valid YAML
inventory plugin config file
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/ansible/test_login.yml with yaml plugin:
YAML inventory has invalid structure, it should be a dictionary, got: <class
'ansible.parsing.yaml.objects.AnsibleSequence'>
[WARNING]:  * Failed to pa...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/ansible/test_login.yml

---

## 112. Test inventory: tests/conftest.py

**Command:** `ansible all -i tests/conftest.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/conftest.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.76s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/conftest.py
with script plugin: problem running
/home/tom/github/wronai/domd/tests/conftest.py --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/tests/conftest.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/conftest.py
with ini plugin: /home/tom/github/wronai/domd/tests/conftest.py:1: Error
parsing host definition '"""': No closing quotation
[WARNING]: Unable to parse /home/tom/github/wronai/...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/conftest.py

---

## 113. Test inventory: tests/fixtures/__init__.py

**Command:** `ansible all -i tests/fixtures/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.92s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/fixtures/__init__.py with script plugin:
problem running /home/tom/github/wronai/domd/tests/fixtures/__init__.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/fixtures/__init__.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/fixtures/__init__.py with ini plugin:
/home/tom/github/wronai/domd/tests/fixtures/__init__.py:1: Error parsing host
definition '"""': No closing quotation
[WARNI...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/__init__.py

---

## 114. Test inventory: tests/fixtures/ansible_helpers.py

**Command:** `ansible all -i tests/fixtures/ansible_helpers.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.87s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py with script
plugin: problem running
/home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py --list ([Errno
8] Exec format error:
'/home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py with ini plugin:
/home/tom/github/wronai/domd/tests/fixtures/ansible_helpers.py:1: Error parsing
host definition...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/ansible_helpers.py

---

## 115. Test inventory: tests/fixtures/sample_dockerfile

**Command:** `ansible all -i tests/fixtures/sample_dockerfile -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/sample_dockerfile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.74s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/sample_dockerfile

---

## 116. Test inventory: tests/fixtures/sample_makefile

**Command:** `ansible all -i tests/fixtures/sample_makefile -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/sample_makefile
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.82s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/sample_makefile

---

## 117. Test inventory: tests/fixtures/sample_package.json

**Command:** `ansible all -i tests/fixtures/sample_package.json -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/sample_package.json
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.03s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/sample_package.json

---

## 118. Test inventory: tests/fixtures/sample_pyproject.toml

**Command:** `ansible all -i tests/fixtures/sample_pyproject.toml -m ping`
**Source:** /home/tom/github/wronai/domd/tests/fixtures/sample_pyproject.toml
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.21s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/fixtures/sample_pyproject.toml

---

## 119. Test inventory: tests/parsers/__init__.py

**Command:** `ansible all -i tests/parsers/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/parsers/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.04s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/parsers/__init__.py

---

## 120. Test inventory: tests/reporters/__init__.py

**Command:** `ansible all -i tests/reporters/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/reporters/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.97s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/reporters/__init__.py

---

## 121. Test inventory: tests/test_ansible.py

**Command:** `ansible all -i tests/test_ansible.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.98s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible.py with script plugin: problem
running /home/tom/github/wronai/domd/tests/test_ansible.py --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/tests/test_ansible.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible.py:1: Error parsing host
definition '"""': No closing quotation
[WARNING]: Unable to parse /hom...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible.py

---

## 122. Test inventory: tests/test_ansible_galaxy.py

**Command:** `ansible all -i tests/test_ansible_galaxy.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible_galaxy.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.89s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_galaxy.py with script plugin:
problem running /home/tom/github/wronai/domd/tests/test_ansible_galaxy.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/test_ansible_galaxy.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_galaxy.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible_galaxy.py:1: Error parsing host
definition '"""': No closing quotat...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible_galaxy.py

---

## 123. Test inventory: tests/test_ansible_inventory.py

**Command:** `ansible all -i tests/test_ansible_inventory.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible_inventory.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.22s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_inventory.py with script
plugin: problem running
/home/tom/github/wronai/domd/tests/test_ansible_inventory.py --list ([Errno 8]
Exec format error:
'/home/tom/github/wronai/domd/tests/test_ansible_inventory.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_inventory.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible_inventory.py:1: Error parsing
host definition '"""': No...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible_inventory.py

---

## 124. Test inventory: tests/test_ansible_playbook.py

**Command:** `ansible all -i tests/test_ansible_playbook.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible_playbook.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.50s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_playbook.py with script plugin:
problem running /home/tom/github/wronai/domd/tests/test_ansible_playbook.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/test_ansible_playbook.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_playbook.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible_playbook.py:1: Error parsing
host definition '"""': No clos...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible_playbook.py

---

## 125. Test inventory: tests/test_ansible_roles.py

**Command:** `ansible all -i tests/test_ansible_roles.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible_roles.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.03s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_roles.py with script plugin:
problem running /home/tom/github/wronai/domd/tests/test_ansible_roles.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/test_ansible_roles.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_roles.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible_roles.py:1: Error parsing host
definition '"""': No closing quotation
[...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible_roles.py

---

## 126. Test inventory: tests/test_ansible_vault.py

**Command:** `ansible all -i tests/test_ansible_vault.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_ansible_vault.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.80s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_vault.py with script plugin:
problem running /home/tom/github/wronai/domd/tests/test_ansible_vault.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/test_ansible_vault.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_ansible_vault.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_ansible_vault.py:1: Error parsing host
definition '"""': No closing quotation
[...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_ansible_vault.py

---

## 127. Test inventory: tests/test_cli.py

**Command:** `ansible all -i tests/test_cli.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_cli.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.12s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/test_cli.py
with script plugin: problem running
/home/tom/github/wronai/domd/tests/test_cli.py --list ([Errno 8] Exec format
error: '/home/tom/github/wronai/domd/tests/test_cli.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/test_cli.py
with ini plugin: /home/tom/github/wronai/domd/tests/test_cli.py:2: Error
parsing host definition '"""': No closing quotation
[WARNING]: Unable to parse /home/tom/github/wronai/...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_cli.py

---

## 128. Test inventory: tests/test_detector.py

**Command:** `ansible all -i tests/test_detector.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/test_detector.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.84s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_detector.py with script plugin: problem
running /home/tom/github/wronai/domd/tests/test_detector.py --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/tests/test_detector.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/test_detector.py with ini plugin:
/home/tom/github/wronai/domd/tests/test_detector.py:1: Error parsing host
definition '"""': No closing quotation
[WARNING]: Unable to parse...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/test_detector.py

---

## 129. Test inventory: tests/unit/core/detector/test_project_command_detector.py

**Command:** `ansible all -i tests/unit/core/detector/test_project_command_detector.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/unit/core/detector/test_project_command_detector.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.86s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/unit/core/dete
ctor/test_project_command_detector.py with script plugin: problem running /home
/tom/github/wronai/domd/tests/unit/core/detector/test_project_command_detector.
py --list ([Errno 8] Exec format error: '/home/tom/github/wronai/domd/tests/uni
t/core/detector/test_project_command_detector.py')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tests/unit/core/dete
ctor/test_project_command_detector.py with ini pl...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/unit/core/detector/test_project_command_detector.py

---

## 130. Test inventory: tests/unit/parsers/test_base_parser.py

**Command:** `ansible all -i tests/unit/parsers/test_base_parser.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.83s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py with script
plugin: problem running
/home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py with ini
plugin: /home/tom/github/wronai/domd/tests/unit/parsers/test_base_parser.py:1:
Erro...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/unit/parsers/test_base_parser.py

---

## 131. Test inventory: tests/unit/parsers/test_config_parsers.py

**Command:** `ansible all -i tests/unit/parsers/test_config_parsers.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/unit/parsers/test_config_parsers.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.94s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/parsers/test_config_parsers.py with
script plugin: problem running
/home/tom/github/wronai/domd/tests/unit/parsers/test_config_parsers.py --list
([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/unit/parsers/test_config_parsers.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/parsers/test_config_parsers.py with ini
plugin:
/home/tom/github/wronai/domd/tests/unit/parsers/test_config_par...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/unit/parsers/test_config_parsers.py

---

## 132. Test inventory: tests/unit/reporters/test_todo_md_reporter.py

**Command:** `ansible all -i tests/unit/reporters/test_todo_md_reporter.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/unit/reporters/test_todo_md_reporter.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.10s

**Error Output:**
```
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/reporters/test_todo_md_reporter.py with
script plugin: problem running
/home/tom/github/wronai/domd/tests/unit/reporters/test_todo_md_reporter.py
--list ([Errno 8] Exec format error:
'/home/tom/github/wronai/domd/tests/unit/reporters/test_todo_md_reporter.py')
[WARNING]:  * Failed to parse
/home/tom/github/wronai/domd/tests/unit/reporters/test_todo_md_reporter.py with
ini plugin:
/home/tom/github/wronai/domd/tests/unit/reporte...
```

**Metadata:**
- **inventory_type:** static
- **file:** tests/unit/reporters/test_todo_md_reporter.py

---

## 133. Test inventory: tests/utils/__init__.py

**Command:** `ansible all -i tests/utils/__init__.py -m ping`
**Source:** /home/tom/github/wronai/domd/tests/utils/__init__.py
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.57s

**Error Output:**
```
[WARNING]: provided hosts list is empty, only localhost is available. Note that
the implicit localhost does not match 'all'

```

**Metadata:**
- **inventory_type:** static
- **file:** tests/utils/__init__.py

---

## 134. Dynamic inventory: todo.sh

**Command:** `ansible-inventory -i todo.sh --list`
**Source:** /home/tom/github/wronai/domd/todo.sh
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.35s

**Output:**
```
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    }
}

```

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/todo.sh with script
plugin: failed to parse executable inventory script results from
/home/tom/github/wronai/domd/todo.sh: Expecting value: line 1 column 1 (char
0). Expecting value: line 1 column 1 (char 0)
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/todo.sh with ini
plugin: /home/tom/github/wronai/domd/todo.sh:5: Expected key=value host
variable assignment, got: -e
[WARNING]: Unable to parse /home/tom/github/wronai/domd/...
```

**Metadata:**
- **inventory_type:** dynamic
- **file:** todo.sh

---

## 135. Test inventory: tox.ini

**Command:** `ansible all -i tox.ini -m ping`
**Source:** /home/tom/github/wronai/domd/tox.ini
**Type:** ansible_inventory
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.32s

**Error Output:**
```
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tox.ini with script
plugin: problem running /home/tom/github/wronai/domd/tox.ini --list ([Errno 8]
Exec format error: '/home/tom/github/wronai/domd/tox.ini')
[WARNING]:  * Failed to parse /home/tom/github/wronai/domd/tox.ini with ini
plugin: /home/tom/github/wronai/domd/tox.ini:6: Expected key=value host
variable assignment, got: true
[WARNING]: Unable to parse /home/tom/github/wronai/domd/tox.ini as an inventory
source
[WARNING]: No inv...
```

**Metadata:**
- **inventory_type:** static
- **file:** tox.ini

---
