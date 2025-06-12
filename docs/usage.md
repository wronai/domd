# 🚀 DoMD User Guide

## Table of Contents
1. [Basic Usage](#-basic-usage)
2. [Project Scanning](#-project-scanning)
3. [Configuration](#-configuration)
4. [Advanced Features](#-advanced-features)
5. [CI/CD Integration](#-cicd-integration)
6. [Usage Examples](#-usage-examples)
7. [Troubleshooting](#-troubleshooting)

## 🏁 Basic Usage

The simplest way to run DoMD in your project:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Run domd
domd
```

By default, DoMD will:
1. Scan the current directory for configuration files
2. Identify available commands (e.g., from `package.json`, `Makefile`, `pyproject.toml`)
3. Execute the found commands
4. Generate a report in `TODO.md`

## 🔍 Project Scanning

### Supported Configuration Files

DoMD automatically detects and analyzes the following file types:

- **JavaScript/TypeScript**: `package.json` (npm, yarn)
- **Python**: `setup.py`, `pyproject.toml`, `requirements.txt`
- **Make**: `Makefile`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Ansible**: Playbooks, roles, inventory
- **PHP**: `composer.json`
- **Rust**: `Cargo.toml`
- **TOML**: General TOML file support
- **YAML**: General YAML file support
- **INI**: General INI file support

### Scanning Options

```bash
# Scan a specific directory
domd --path /path/to/project

# Exclude specific files/directories
domd --exclude "*.test.js" --exclude "node_modules/*"

# Scan only specific files
domd --include-only "Makefile" --include-only "package.json"
```

## ⚙️ Configuration

### .domdignore File

Create a `.domdignore` file in your project root to exclude specific commands:

```
# Ignore specific commands
npm run test:coverage
pytest -xvs

# Ignore using patterns
*coverage*
*test*
```

### .dodocker File

To run commands in a Docker container, create a `.dodocker` file:

```yaml
image: python:3.9
volumes:
  - .:/app
working_dir: /app
environment:
  - PYTHONPATH=/app
```

## 🚀 Advanced Features

### Dry Run Mode

```bash
# Show what commands would be executed without actually running them
domd --dry-run
```

### Output Formats

```bash
# Format JSON
domd --format json

# Format tekstowy
domd --format text

# Format Markdown (domyślny)
domd --format markdown

# Własna ścieżka wyjściowa
domd --output raport.md
```

### Ustawienie limitu czasu

```bash
# Ustawienie limitu czasu na wykonanie komendy (domyślnie 60s)
domd --timeout 120
```

## 🤖 Integracja z CI/CD

### GitHub Actions

Przykładowy plik workflow dla GitHub Actions:

```yaml
name: DoMD Health Check

on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install DoMD
        run: pip install domd

      - name: Run health check
        run: domd --output health-report.md

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: health-report
          path: health-report.md
```

## 💡 Przykłady użycia

### Przykład 1: Podstawowe użycie

```bash
# Przejdź do katalogu projektu
cd moj-projekt

# Uruchom domd
domd

# Sprawdź wygenerowany raport
cat TODO.md
```

### Przykład 2: Integracja z Makefile

Dodaj do swojego `Makefile`:

```makefile
health-check:
	domd --output HEALTH.md

.PHONY: health-check
```

## ❓ Rozwiązywanie problemów

### Błędy wykonania komend

Jeśli napotkasz błędy podczas wykonywania komend:

1. Sprawdź, czy wszystkie wymagane narzędzia są zainstalowane
2. Upewnij się, że wszystkie zmienne środowiskowe są ustawione poprawnie
3. Spróbuj uruchomić problematyczną komendę ręcznie
4. Użyj flagi `--verbose`, aby uzyskać więcej informacji

### Zgłaszanie błędów

Jeśli znajdziesz błąd lub masz sugestię:

1. Sprawdź, czy problem nie został już zgłoszony w [issues](https://github.com/wronai/domd/issues)
2. Jeśli nie, utwórz nowe zgłoszenie z:
   - Krótkim opisem problemu
   - Krokami do odtworzenia błędu
   - Oczekiwanym i faktycznym zachowaniem
   - Wersją DoMD (`domd --version`)
   - Środowiskiem (system operacyjny, wersja Pythona itp.)

---

Masz dodatkowe pytania? Sprawdź [dokumentację](https://domd.readthedocs.io/) lub [zgłoś problem](https://github.com/wronai/domd/issues).
