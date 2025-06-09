# 📥 Instalacja DoMD

## Wymagania wstępne

- Python 3.8 lub nowszy
- pip (menedżer pakietów Pythona)
- Git (opcjonalnie, do instalacji z repozytorium)

## Metody instalacji

### 1. Instalacja przez pip (zalecane)

Najprostszy sposób na zainstalowanie DoMD:

```bash
pip install domd
```

### 2. Instalacja z repozytorium (dla najnowszej wersji)

Jeśli chcesz korzystać z najnowszych zmian:

```bash
# Sklonuj repozytorium
git clone https://github.com/wronai/domd.git
cd domd

# Zainstaluj w trybie edytowalnym
pip install -e .
```

### 3. Instalacja z dodatkowymi zależnościami

DoMD obsługuje dodatkowe zależności dla rozszerzonej funkcjonalności:

```bash
# Z obsługą Ansible
pip install "domd[ansible]"

# Z dodatkami developerskimi
pip install "domd[dev]"

# Wszystkie dodatki
pip install "domd[all]"

# Z użyciem Poetry (opcjonalnie)
poetry add domd
```

## Weryfikacja instalacji

Sprawdź, czy DoMD został poprawnie zainstalowany:

```bash
domd --version
```

Powinieneś zobaczyć numer wersji, np. `domd 1.0.0`.

## Aktualizacja

Aby zaktualizować DoMD do najnowszej wersji:

```bash
pip install --upgrade domd
```

## Odinstalowywanie

Jeśli chcesz odinstalować DoMD:

```bash
pip uninstall domd
```

## Rozwiązywanie problemów

### Błąd braku uprawnień

Jeśli wystąpi błąd uprawnień podczas instalacji, spróbuj:

```bash
pip install --user domd
```
lub
```bash
sudo pip install domd  # Tylko na Linux/macOS
```

### Błędy zależności

Jeśli napotkasz problemy z zależnościami, spróbuj:

```bash
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir domd
```

## Następne kroki

- [Przejdź do przewodnika użytkownika](usage.md) aby dowiedzieć się, jak korzystać z DoMD
- [Zapoznaj się z funkcjami](features/) aby poznać wszystkie możliwości narzędzia

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
