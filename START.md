# 🚀 TodoMD - Quick Start Guide

**Get TodoMD running in your project in under 5 minutes!**

## ⚡ Super Quick Start

```bash
# 1. Clone and setup (automated)
git clone https://github.com/yourusername/todomd.git
cd todomd
chmod +x scripts/setup_project.sh
./scripts/setup_project.sh

# 2. Test on example project
poetry run todomd --path examples --dry-run

# 3. Test on current project (dogfooding!)
poetry run todomd --verbose
```

## 📦 Installation Options

### Option 1: From PyPI (when published)
```bash
pip install todomd
todomd --help
```

### Option 2: From Source (recommended for development)
```bash
# Clone repository
git clone https://github.com/yourusername/todomd.git
cd todomd

# Quick setup with Poetry
poetry install
poetry run todomd --version
```

### Option 3: Development Setup
```bash
# Full development environment
poetry install --with dev,docs,testing,lint
poetry run pre-commit install
make dev  # Runs format, lint, test
```

## 🎯 First Run

### 1. Preview Mode (Safe)
```bash
# See what commands TodoMD would test
todomd --dry-run
```

**Example output:**
```
TodoMD v0.1.0
Scanning project: /home/user/my-project

Found 8 commands to test

🔍 DRY RUN MODE - Commands found:
  1. NPM script: test
     Command: npm run test
     Source:  package.json

  2. NPM script: build
     Command: npm run build
     Source:  package.json

  3. Make target: install
     Command: make install
     Source:  Makefile
     
  4. Docker build
     Command: docker build -t my-project .
     Source:  Dockerfile
```

### 2. Verbose Mode (Detailed Info)
```bash
# Detailed scanning and execution info
todomd --verbose
```

### 3. Actual Testing
```bash
# Test all commands and generate TODO.md for failures
todomd
```

## 📊 Understanding Output

### Success Case
```
==================================================
EXECUTION SUMMARY
==================================================
✅ Successful: 6/8
❌ Failed: 2/8
📊 Success rate: 75.0%
📝 Check TODO.md for failed command details
```

### Generated TODO.md
```markdown
# TODO - Failed Project Commands

Found **2** commands that require fixing:

## Task 1: NPM script - test

**Source:** `package.json`
**Return Code:** 1

### Command to fix:
```bash
npm run test
```

### Error:
```
Error: Cannot find module 'jest'
```

### Suggested Actions:
- [ ] Install missing dependencies: `npm install`
- [ ] Check if jest is in devDependencies
```

## 🔧 Common Use Cases

### CI/CD Health Check
```bash
# Add to your pipeline
todomd --quiet && echo "All commands working!" || echo "Some commands failed"
```

### Pre-deployment Validation
```bash
# Check before deploying
todomd --timeout 120 --format json --output health-check.json
```

### New Developer Onboarding
```bash
# Help new team members identify setup issues
todomd --verbose --output SETUP_ISSUES.md
```

### Legacy Project Analysis
```bash
# Analyze old projects
todomd --path /path/to/legacy/project --dry-run
```

## 🎛️ Essential Options

| Option | Purpose | Example |
|--------|---------|---------|
| `--dry-run` | Preview without execution | `todomd --dry-run` |
| `--verbose` | Detailed output | `todomd --verbose` |
| `--quiet` | Errors only | `todomd --quiet` |
| `--path` | Different project | `todomd --path ./frontend` |
| `--timeout` | Custom timeout | `todomd --timeout 30` |
| `--format` | Output format | `todomd --format json` |
| `--output` | Custom file | `todomd --output ISSUES.md` |

## 🏗️ Project Types Detected

### ✅ **Automatically Detected:**

**JavaScript/Node.js:**
- `package.json` → npm scripts
- `yarn.lock` → yarn install
- `pnpm-lock.yaml` → pnpm install

**Python:**
- `pyproject.toml` → Poetry scripts, pytest
- `requirements.txt` → pip install
- `tox.ini` → test environments
- `setup.py` → installation

**Build Systems:**
- `Makefile` → make targets
- `CMakeLists.txt` → cmake build
- `build.gradle` → gradle tasks
- `pom.xml` → maven goals

**Containers:**
- `Dockerfile` → docker build
- `docker-compose.yml` → services

**Other:**
- `composer.json` (PHP)
- `Gemfile` (Ruby)
- `Cargo.toml` (Rust)
- `go.mod` (Go)

## 🔧 Advanced Usage

### Pattern Filtering
```bash
# Exclude test files and build artifacts
todomd --exclude "*.test.*" --exclude "node_modules/*" --exclude "build/*"

# Only check specific files
todomd --include-only "Makefile" --include-only "package.json"
```

### Output Formats
```bash
# Markdown (default)
todomd --output TODO.md

# JSON for processing
todomd --format json --output results.json

# Plain text
todomd --format text --output summary.txt
```

### Timeout Control
```bash
# Quick check (30s timeout)
todomd --timeout 30 --quiet

# Patient check (5 min timeout)
todomd --timeout 300 --verbose
```

## 🔗 Integration Examples

### Makefile Integration
```makefile
# Add to your Makefile
.PHONY: health-check
health-check:
	@todomd --quiet || (echo "❌ Failed commands in TODO.md" && exit 1)
	@echo "✅ All project commands working!"

.PHONY: health-report
health-report:
	@todomd --verbose --format json --output health-report.json
	@echo "📊 Health report: health-report.json"
```

### GitHub Actions
```yaml
- name: Project Health Check
  run: |
    pip install todomd
    todomd --verbose
- name: Upload failed commands
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: todo-md
    path: TODO.md
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: todomd
        name: TodoMD Health Check
        entry: todomd --quiet
        language: system
        pass_filenames: false
```

## 🐛 Troubleshooting

### Common Issues

**"No commands found"**
```bash
# Check if config files exist
ls -la | grep -E "(package\.json|Makefile|pyproject\.toml|Dockerfile)"

# Run with verbose to see scanning process
todomd --dry-run --verbose
```

**"Command not found" errors**
```bash
# Check if tools are installed
which npm node python pip make docker

# Install missing tools
sudo apt install make          # Ubuntu/Debian
brew install make node python  # macOS
```

**Timeout issues**
```bash
# Increase timeout for slow commands
todomd --timeout 180

# Or exclude slow commands
todomd --exclude "*integration*" --exclude "*e2e*"
```

**Permission denied**
```bash
# Check file permissions
ls -la Makefile package.json

# Make scripts executable
chmod +x scripts/*.sh
```

## 📈 Performance Tips

### For Large Projects
```bash
# Quick scan (exclude heavy directories)
todomd --exclude "node_modules/*" --exclude ".git/*" --exclude "build/*"

# Focus on main configs only
todomd --include-only "package.json" --include-only "Makefile" --include-only "pyproject.toml"

# Shorter timeout for CI
todomd --timeout 30 --quiet
```

### Parallel Projects
```bash
# Check multiple projects
for project in frontend backend mobile; do
    echo "=== Checking $project ==="
    todomd --path ./$project --quiet
done
```

## 🎓 Learning Path

### Beginner (5 minutes)
1. `todomd --dry-run` - See what would be tested
2. `todomd --verbose` - Run with detailed output
3. Review generated `TODO.md`

### Intermediate (15 minutes)
1. Try different formats: `--format json`
2. Use filtering: `--exclude` and `--include-only`
3. Integrate with your `Makefile`

### Advanced (30 minutes)
1. Set up CI/CD integration
2. Create custom pre-commit hooks
3. Use programmatic API in Python scripts

## 🚀 Next Steps

### After First Success
1. **Add to CI/CD**: Automate health checks
2. **Team Integration**: Add to project documentation
3. **Custom Patterns**: Configure exclude/include for your workflow

### Customize for Your Project
```bash
# Create project-specific alias
alias project-health="todomd --exclude 'test/*' --timeout 60 --verbose"

# Add to package.json scripts
{
  "scripts": {
    "health-check": "todomd --quiet",
    "health-report": "todomd --format json --output health.json"
  }
}
```

### Extend TodoMD
- **Custom Parsers**: Add support for new project types
- **Integration Scripts**: Connect with monitoring tools
- **Team Workflows**: Build project-specific health dashboards

## ✅ Quick Checklist

- [ ] Install TodoMD (`poetry install` or `pip install todomd`)
- [ ] Run preview: `todomd --dry-run`
- [ ] First test: `todomd --verbose`
- [ ] Review `TODO.md` for any failures
- [ ] Fix failed commands using suggestions
- [ ] Add to project workflow (Makefile, CI/CD, etc.)
- [ ] Share with team!

## 🆘 Need Help?

**Documentation**: [Full docs](https://todomd.readthedocs.io)
**Issues**: [GitHub Issues](https://github.com/yourusername/todomd/issues)
**Examples**: Check `examples/` directory
**API Reference**: [Python API docs](https://todomd.readthedocs.io/api/)

---

## 🎉 You're Ready!

TodoMD is now monitoring your project health. Every run helps ensure your commands work for the entire team!

**Pro tip**: Run `todomd --dry-run` regularly to catch issues early, and use `todomd` before important deployments.

**Happy coding!** 🚀