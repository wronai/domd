# 📥 DoMD Installation Guide

## Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- Git (optional, for installation from repository)
- Docker (optional, for containerized execution)

## Installation Methods

### 1. Using pip (Recommended)

The easiest way to install DoMD:

```bash
pip install domd
```

### 2. From Source (for latest development version)

If you want to use the latest development version:

```bash
# Clone the repository
git clone https://github.com/wronai/domd.git
cd domd

# Install in development mode
pip install -e .
```

### 3. With Optional Dependencies

DoMD supports optional dependencies for extended functionality:

```bash
# With Ansible support
pip install "domd[ansible]"

# With development tools
pip install "domd[dev]"

# All optional dependencies
pip install "domd[all]"

# Using Poetry (optional)
poetry add domd
```

### 4. Using Docker

You can also use DoMD via Docker without installing it locally:

```bash
docker run --rm -v $(pwd):/app ghcr.io/wronai/domd domd
```

## Verifying Installation

Check if DoMD is installed correctly:

```bash
domd --version
```

You should see the version number, e.g., `domd 1.0.0`.

## Updating

To update DoMD to the latest version:

```bash
pip install --upgrade domd
```

## Uninstalling

To uninstall DoMD:

```bash
pip uninstall domd
```

## Troubleshooting

### Permission Errors

If you encounter permission errors during installation:

```bash
pip install --user domd
```
Or on Linux/macOS:
```bash
sudo pip install domd
```

### Dependency Issues

If you have dependency conflicts:

```bash
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir domd
```

### Common Issues

#### 1. Błąd: "Command not found"

```bash
# Sprawdź czy narzędzie jest zainstalowane
which npm  # lub yarn, make, docker, itp.

# Zainstaluj brakujące narzędzia
sudo apt install make  # Ubuntu/Debian
brew install make      # macOS
```

#### 2. Błąd: "Permission denied"

```bash
# Sprawdź uprawnienia
ls -la Makefile
chmod +x scripts/build.sh

# Może wymagane sudo dla niektórych komend
```

#### 3. Błędy timeout

```bash
# Zwiększ timeout dla wolnych komend
domd --timeout 300  # 5 minut
```

#### 4. Problemy z kodowaniem

```bash
# Ustaw poprawne kodowanie
export LANG=pl_PL.UTF-8
export LC_ALL=pl_PL.UTF-8
```

### Tryb debugowania

```bash
# Szczegółowe informacje o wykonaniu
domd --verbose

# Tylko podgląd bez wykonywania komend
domd --dry-run
```

## Aktualizacja do nowszej wersji

### Sprawdzanie wersji

```bash
domd --version
poetry show domd  # jeśli zainstalowane przez Poetry
pip show domd     # jeśli zainstalowane przez pip
```

### Aktualizacja

```bash
# Aktualizacja przez pip
pip install --upgrade domd

# Aktualizacja z repozytorium (dla instalacji deweloperskiej)
git pull origin main
pip install -e .
```

## 📞 Wsparcie

- **Dokumentacja**: https://domd.readthedocs.io
- **Zgłoszenia błędów**: https://github.com/wronai/domd/issues
- **Dyskusje**: https://github.com/wronai/domd/discussions

## 🎯 Następne kroki

Po zainstalowaniu:

1. [Przejdź do przewodnika użytkownika](usage.md) aby poznać możliwości DoMD
2. Sprawdź [dokumentację funkcji](features/) aby poznać wszystkie opcje
3. Dołącz do społeczności na [GitHub Discussions](https://github.com/wronai/domd/discussions)

**Gotowe do użycia! 🚀**
