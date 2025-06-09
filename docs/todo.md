# 🤖 TODO - LLM Task List for Command Fixes

**📋 INSTRUCTIONS FOR LLM:**
This file contains a list of broken commands that need to be fixed.
Each task is a separate command that failed during testing.

**🎯 YOUR MISSION:**
1. **Analyze each failed command** and its error output
2. **Identify the root cause** of the failure
3. **Implement the fix** by modifying source code, config files, or dependencies
4. **Test the fix** by running the command manually
5. **Update progress** - when a command starts working, it will be moved to DONE.md automatically

**📝 TASK FORMAT:**
Each task has:
- ❌ **Command** that failed
- 📁 **Source file** where the command is defined
- 🔴 **Error output** with full details
- 💡 **Suggested actions** for fixing

**🔄 WORKFLOW:**
1. Pick a task from the list below
2. Read the error details carefully
3. Implement the fix
4. Run `domd` to retest all commands
5. Fixed commands will automatically move to DONE.md

---

**📊 Current Status:**
- **Failed Commands:** 6
- **Working Commands:** 18 (see DONE.md)
- **Last Updated:** 2025-06-06 16:45:23

---

## 🔧 Tasks to Fix (6 commands)

Each section below is a separate task. Fix them one by one:

### [ ] Task 1: NPM script - build

**📋 Command:** `npm run build`
**📁 Source:** `package.json`
**⏱️ Timeout:** 60s
**🔴 Return Code:** 1
**⚡ Execution Time:** 3.45s

#### 🔴 Error Output:

```bash
# Command that failed:
npm run build

# Error output:
npm ERR! missing script: build
npm ERR!
npm ERR! To see a list of scripts, run:
npm ERR!   npm run
npm ERR!
npm ERR! A complete log of this run can be found in:
npm ERR!     /home/user/.npm/_logs/2025-06-06T16_45_20_123Z-debug.log
```

#### 💡 Suggested Fix Actions:

- [ ] Run `npm install` to ensure all dependencies are installed
- [ ] Check package.json for script definition errors
- [ ] Verify Node.js and npm versions are compatible
- [ ] Check package.json for script definition errors
- [ ] Check if referenced files exist in the project
- [ ] Verify file paths in package.json are correct

#### 🔍 Investigation Steps:

1. **Check source file:** Open `package.json` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `npm run build` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `npm run build` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

### [ ] Task 2: Make target - build

**📋 Command:** `make build`
**📁 Source:** `Makefile`
**⏱️ Timeout:** 60s
**🔴 Return Code:** 2
**⚡ Execution Time:** 0.12s

#### 🔴 Error Output:

```bash
# Command that failed:
make build

# Error output:
make: *** No rule to make target 'src/main.c', needed by 'build'. Stop.
```

#### 💡 Suggested Fix Actions:

- [ ] Check Makefile syntax and dependencies
- [ ] Verify all required tools are installed (gcc, etc.)
- [ ] Check if target dependencies exist
- [ ] Check if referenced files exist in the project
- [ ] Verify file paths in Makefile are correct
- [ ] Create missing files or update paths

#### 🔍 Investigation Steps:

1. **Check source file:** Open `Makefile` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `make build` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `make build` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

### [ ] Task 3: Docker build

**📋 Command:** `docker build -t my-project .`
**📁 Source:** `Dockerfile`
**⏱️ Timeout:** 60s
**🔴 Return Code:** 1
**⚡ Execution Time:** 15.67s

#### 🔴 Error Output:

```bash
# Command that failed:
docker build -t my-project .

# Error output:
Sending build context to Docker daemon  2.048kB
Step 1/3 : FROM python:3.9-slim
 ---> 2b5a8a4e89cc
Step 2/3 : COPY requirements.txt .
COPY failed: file not found in build context or excluded by .dockerignore: stat requirements.txt: file does not exist
```

#### 💡 Suggested Fix Actions:

- [ ] Check if Docker is running: `docker --version`
- [ ] Verify Dockerfile syntax
- [ ] Check Docker permissions for current user
- [ ] Check if referenced files exist in the project
- [ ] Verify file paths in Dockerfile are correct
- [ ] Create missing files or update paths

#### 🔍 Investigation Steps:

1. **Check source file:** Open `Dockerfile` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `docker build -t my-project .` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `docker build -t my-project .` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

### [ ] Task 4: Poetry script - mypy

**📋 Command:** `poetry run mypy`
**📁 Source:** `pyproject.toml`
**⏱️ Timeout:** 60s
**🔴 Return Code:** 1
**⚡ Execution Time:** 2.89s

#### 🔴 Error Output:

```bash
# Command that failed:
poetry run mypy

# Error output:
/bin/sh: 1: mypy: not found
```

#### 💡 Suggested Fix Actions:

- [ ] Run `poetry install` to install dependencies
- [ ] Check pyproject.toml for script configuration
- [ ] Verify poetry is installed and accessible
- [ ] Install missing tool/command: Look for installation instructions
- [ ] Check if command is in PATH: `which mypy`
- [ ] Verify spelling of command in pyproject.toml

#### 🔍 Investigation Steps:

1. **Check source file:** Open `pyproject.toml` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `poetry run mypy` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `poetry run mypy` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

### [ ] Task 5: Install pip dependencies from requirements.txt

**📋 Command:** `pip install -r requirements.txt`
**📁 Source:** `requirements.txt`
**⏱️ Timeout:** 60s
**🔴 Return Code:** 1
**⚡ Execution Time:** 1.23s

#### 🔴 Error Output:

```bash
# Command that failed:
pip install -r requirements.txt

# Error output:
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

#### 💡 Suggested Fix Actions:

- [ ] Check if referenced files exist in the project
- [ ] Verify file paths in requirements.txt are correct
- [ ] Create missing files or update paths
- [ ] Read the error output carefully for specific clues
- [ ] Check requirements.txt for command definition and syntax
- [ ] Manually run the command to reproduce and debug the issue

#### 🔍 Investigation Steps:

1. **Check source file:** Open `requirements.txt` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `pip install -r requirements.txt` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `pip install -r requirements.txt` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

### [ ] Task 6: Make target - publish

**📋 Command:** `make publish`
**📁 Source:** `Makefile`
**⏱️ Timeout:** 60s
**🔴 Return Code:** -1
**⚡ Execution Time:** 60.00s

#### 🔴 Error Output:

```bash
# Command that failed:
make publish

# Error output:
Command timed out after 60 seconds
```

#### 💡 Suggested Fix Actions:

- [ ] Command took longer than 60s - consider increasing timeout
- [ ] Check if command is hanging or waiting for input
- [ ] Add to .doignore if this is a long-running service command
- [ ] Check Makefile syntax and dependencies
- [ ] Verify all required tools are installed (gcc, etc.)
- [ ] Check if target dependencies exist

#### 🔍 Investigation Steps:

1. **Check source file:** Open `Makefile` and locate the command definition
2. **Analyze error:** Read the error output above for clues
3. **Check dependencies:** Verify all required tools/packages are installed
4. **Test manually:** Run `make publish` in terminal to reproduce the issue
5. **Implement fix:** Based on error analysis, modify files as needed
6. **Verify fix:** Run the command again to confirm it works

#### ✅ Completion Criteria:

This task is complete when `make publish` runs without errors.
The command will then automatically appear in DONE.md on the next test run.

---

## 🔄 After Making Fixes

When you've fixed one or more commands:

1. **Test your fixes:**
   ```bash
   # Test specific command manually:
   cd /home/user/my-project
   [your-fixed-command]

   # Or test all commands:
   domd
   ```

2. **Check results:**
   - Fixed commands → will appear in DONE.md
   - Still broken commands → remain in this TODO.md
   - New failures → will be added to this TODO.md

3. **Iterate:**
   - Continue fixing remaining tasks
   - Re-run `domd` after each fix
   - Monitor progress in both files

## 📚 Common Fix Patterns

### Missing Dependencies
```bash
# Python
pip install missing-package
poetry add missing-package

# Node.js
npm install missing-package
yarn add missing-package

# System
sudo apt install missing-tool
brew install missing-tool
```

### Configuration Issues
```bash
# Check config files for typos
# Verify paths and settings
# Update outdated configurations
```

### Permission Issues
```bash
chmod +x script-file
sudo chown user:group file
```

### Version Compatibility
```bash
# Update to compatible versions
# Check tool documentation
# Use version-specific commands
```
