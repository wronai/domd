# DoMD - Instrukcja Instalacji i Użycia

## 🚀 Szybka Instalacja

### 1. Przygotowanie środowiska

```bash
# Sprawdź Python (wymagane 3.8+)
python --version

# Zainstaluj Poetry (jeśli nie masz)
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Klonowanie i budowanie

```bash
# Sklonuj repozytorium
git clone https://github.com/wronai/domd.git
cd domd

# Automatyczna konfiguracja (uruchom skrypt setup)
chmod +x scripts/setup_project.sh
./scripts/setup_project.sh
```

### 3. Alternatywnie - manualna instalacja

```bash
# Zainstaluj zależności
poetry install --with dev,docs,testing,lint

# Zainstaluj pre-commit hooks
poetry run pre-commit install

# Formatuj kod
poetry run black src/ tests/
poetry run isort src/ tests/

# Uruchom testy
poetry run pytest

# Zbuduj paczkę
poetry build
```

## 📦 Instalacja z PyPI (gdy będzie opublikowane)

```bash
# Podstawowa instalacja
pip install domd

# Z dodatkowymi funkcjami
pip install domd[all]

# Przy użyciu Poetry
poetry add domd
```

## 🔧 Podstawowe użycie

### Skanowanie bieżącego projektu

```bash
# Podstawowe skanowanie
domd

# Tryb podglądu (bez wykonywania komend)
domd --dry-run

# Szczegółowe informacje
domd --verbose
```

### Przykład wyjścia

```
DoMD v0.1.0
Scanning project: /home/user/my-project

Found 5 configuration files:
  - package.json
  - Makefile
  - pyproject.toml
  - docker-compose.yml
  - tox.ini

Found 12 commands to test

Testing commands...

[1/12] Testing: NPM script - test
Command: npm run test
Source: package.json
✅ SUKCES

[2/12] Testing: NPM script - build
Command: npm run build
Source: package.json
❌ BŁĄD

[3/12] Testing: Make target - install
Command: make install
Source: Makefile
✅ SUKCES

...

==================================================
EXECUTION SUMMARY
==================================================
✅ Successful: 9/12
❌ Failed: 3/12
📊 Success rate: 75.0%
📝 Check output file for failed command details
```

## 🎯 Zaawansowane opcje

### Kustomizacja skanowania

```bash
# Skanowanie konkretnego projektu
domd --path /ścieżka/do/projektu

# Własny plik wyjściowy
domd --output FAILED_TASKS.md

# Różne formaty wyjścia
domd --format json      # JSON
domd --format text      # Zwykły tekst
domd --format markdown  # Markdown (domyślny)

# Timeout dla komend (domyślnie 60s)
domd --timeout 120

# Wykluczanie plików
domd --exclude "*.test.js" --exclude "node_modules/*"

# Tylko konkretne pliki
domd --include-only "Makefile" --include-only "package.json"
```

### Tryby działania

```bash
# Tryb cichy (tylko błędy)
domd --quiet

# Tryb szczegółowy
domd --verbose

# Kombinacje
domd --path ./frontend --dry-run --verbose
domd --quiet --format json --output results.json
```

## 📊 Przykłady generowanych raportów

### TODO.md (Markdown)

```markdown
# TODO - Failed Project Commands

Automatically generated by DoMD
Date: 2025-06-06 10:30:15
Project: /home/user/my-project

Found **2** commands that require fixing:

## Task 1: NPM script - build

**Source:** `package.json`
**Return Code:** 1
**Execution Time:** 3.45s

### Command to fix:
```bash
npm run build
```

### Error:
```
Error: Cannot find module 'webpack'
npm ERR! missing script: build
```

### Suggested Actions:
- [ ] Check if all dependencies are installed
- [ ] Verify command syntax and arguments
- [ ] Check file permissions and access rights
- [ ] Review error logs for specific issues
- [ ] Ensure required tools/binaries are available

---
```

### Results.json (JSON)

```json
{
  "generated_at": "2025-06-06T10:30:15.123456",
  "project_path": "/home/user/my-project",
  "total_failed": 2,
  "failed_commands": [
    {
      "command": "npm run build",
      "description": "NPM script - build",
      "source": "package.json",
      "type": "npm_script",
      "return_code": 1,
      "execution_time": 3.45,
      "error": "Error: Cannot find module 'webpack'"
    }
  ]
}
```

## 🔗 Integracja z narzędziami

### GitHub Actions

```yaml
name: Project Health Check
on: [push, pull_request]

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install DoMD
      run: pip install domd
    - name: Health Check
      run: domd --verbose
    - name: Upload TODO if failed
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: failed-commands
        path: TODO.md
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: domd-check
        name: Project Health Check
        entry: domd
        language: system
        pass_filenames: false
        always_run: true
```

### Makefile Integration

```makefile
# Dodaj do swojego Makefile
.PHONY: health-check
health-check:
	@echo "🔍 Checking project health..."
	@domd --quiet || (echo "❌ Some commands failed. Check TODO.md" && exit 1)
	@echo "✅ All project commands working!"

.PHONY: health-report
health-report:
	@domd --dry-run --verbose

.PHONY: health-full
health-full:
	@domd --verbose --format json --output health-report.json
	@echo "📊 Full health report saved to health-report.json"
```

## 🧪 Programmatic API

### Python API

```python
from domd import ProjectCommandDetector

# Podstawowe użycie
detector = ProjectCommandDetector("./my-project")
commands = detector.scan_project()
print(f"Found {len(commands)} commands")

# Testowanie komend
detector.test_commands(commands)

# Generowanie raportu
detector.generate_output_file("RESULTS.md", "markdown")

# Statystyki
stats = detector.get_statistics()
print(f"Success rate: {stats['success_rate']:.1f}%")

# Eksport szczegółowych wyników
detector.export_results("detailed_results.json")
```

### Zaawansowane konfiguracje

```python
# Z wykluczeniami i timeout
detector = ProjectCommandDetector(
    project_path="./big-project",
    timeout=120,
    exclude_patterns=["*.pyc", "__pycache__/*", "node_modules/*"],
    include_patterns=["Makefile", "package.json", "pyproject.toml"]
)

# Skanowanie i analiza
commands = detector.scan_project()
detector.test_commands(commands)

# Różne formaty wyjścia
detector.generate_output_file("TODO.md", "markdown")
detector.generate_output_file("results.json", "json")
detector.generate_output_file("summary.txt", "text")

# Wyświetl podsumowanie
detector.print_summary()

# Dostęp do nieudanych komend
for cmd in detector.failed_commands:
    print(f"Failed: {cmd['description']}")
    print(f"Error: {cmd.get('error', 'N/A')}")
    print(f"Source: {cmd['source']}")
    print("---")
```

## 🐛 Rozwiązywanie problemów

### Częste problemy

**1. Błąd: "Command not found"**
```bash
# Sprawdź czy narzędzie jest zainstalowane
which npm  # lub yarn, make, docker, itp.

# Zainstaluj brakujące narzędzia
sudo apt install make  # Ubuntu/Debian
brew install make      # macOS
```

**2. Błąd: "Permission denied"**
```bash
# Sprawdź uprawnienia
ls -la Makefile
chmod +x scripts/build.sh

# Może wymagane sudo dla niektórych komend
```

**3. Timeout errors**
```bash
# Zwiększ timeout dla wolnych komend
domd --timeout 300  # 5 minut
```

**4. Problemy z encoding**
```bash
# Ustaw poprawne kodowanie
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### Debug mode

```bash
# Maksymalnie szczegółowe informacje
domd --verbose --dry-run

# Python debug
PYTHONPATH=src python -m domd.detector --verbose --path .
```

### Logi

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from domd import ProjectCommandDetector
detector = ProjectCommandDetector(".")
# Teraz zobaczysz wszystkie debug informacje
```

## 📈 Wydajność i optymalizacja

### Dla dużych projektów

```bash
# Wykluczenie ciężkich folderów
domd --exclude "node_modules/*" --exclude ".git/*" --exclude "build/*"

# Tylko najważniejsze pliki
domd --include-only "Makefile" --include-only "package.json" --include-only "pyproject.toml"

# Krótszy timeout dla szybszego skanowania
domd --timeout 30 --quiet
```

### Równoległe uruchamianie

DoMD obecnie uruchamia komendy sekwencyjnie dla bezpieczeństwa. W przyszłych wersjach planowane jest równoległe wykonywanie.

## 🔄 Aktualizacje

### Sprawdzanie wersji

```bash
domd --version
poetry show domd  # jeśli zainstalowane przez Poetry
pip show domd     # jeśli zainstalowane przez pip
```

### Aktualizacja

```bash
# Pip
pip install --upgrade domd

# Poetry
poetry update domd

# Development version
git pull
poetry install
```

## 📞 Wsparcie

- **Dokumentacja**: https://domd.readthedocs.io
- **Issues**: https://github.com/wronai/domd/issues
- **Discussions**: https://github.com/wronai/domd/discussions

## 🎯 Następne kroki

Po zainstalowaniu:

1. **Uruchom na swoim projekcie**: `domd --dry-run`
2. **Sprawdź co znaleziono**: przejrzyj listę wykrytych komend
3. **Przetestuj**: `domd --verbose`
4. **Napraw błędy**: użyj wygenerowanego TODO.md
5. **Zintegruj z workflow**: dodaj do CI/CD, pre-commit, Makefile

**Gotowe do użycia! 🚀**
