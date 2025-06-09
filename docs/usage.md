# 🚀 Przewodnik użytkownika DoMD

## Spis treści
1. [Podstawowe użycie](#-podstawowe-użycie)
2. [Skanowanie projektu](#-skanowanie-projektu)
3. [Konfiguracja](#-konfiguracja)
4. [Zaawansowane funkcje](#-zaawansowane-funkcje)
5. [Integracja z CI/CD](#-integracja-z-cicd)
6. [Przykłady użycia](#-przykłady-użycia)
7. [Rozwiązywanie problemów](#-rozwiązywanie-problemów)

## 🏁 Podstawowe użycie

Najprostszy sposób na uruchomienie DoMD w Twoim projekcie:

```bash
# Przejdź do katalogu projektu
cd /ścieżka/do/projektu

# Uruchom domd
domd
```

Domyślnie DoMD:
1. Przeskanuje bieżący katalog w poszukiwaniu plików konfiguracyjnych
2. Zidentyfikuje dostępne komendy (np. z `package.json`, `Makefile`, `pyproject.toml`)
3. Wykona znalezione komendy
4. Wygeneruje raport w pliku `TODO.md`

## 🔍 Skanowanie projektu

### Obsługiwane pliki konfiguracyjne

DoMD automatycznie wykrywa i analizuje następujące typy plików:

- **JavaScript/TypeScript**: `package.json` (npm, yarn)
- **Python**: `setup.py`, `pyproject.toml`, `requirements.txt`
- **Make**: `Makefile`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Ansible**: Playbooki, role, inventory
- **PHP**: `composer.json`
- **Rust**: `Cargo.toml`
- **TOML**: Ogólna obsługa plików TOML
- **YAML**: Ogólna obsługa plików YAML
- **INI**: Ogólna obsługa plików INI

### Opcje skanowania

```bash
# Skanowanie konkretnego katalogu
domd --path /ścieżka/do/projektu

# Pomijanie określonych plików/katalogów
domd --exclude "*.test.js" --exclude "node_modules/*"

# Skanowanie tylko wybranych plików
domd --include-only "Makefile" --include-only "package.json"
```

## ⚙️ Konfiguracja

### Plik .domdignore

Możesz utworzyć plik `.domdignore` w głównym katalogu projektu, aby wykluczyć określone komendy:

```
# Ignoruj konkretne komendy
npm run test:coverage
pytest -xvs

# Ignoruj według wzorca
*coverage*
*test*
```

### Plik .dodocker

Aby uruchamiać komendy w kontenerze Docker, utwórz plik `.dodocker`:

```yaml
image: python:3.9
volumes:
  - .:/app
working_dir: /app
environment:
  - PYTHONPATH=/app
```

## 🚀 Zaawansowane funkcje

### Tryb podglądu (dry-run)

```bash
# Pokaż, jakie komendy zostałyby wykonane, bez faktycznego ich wykonywania
domd --dry-run
```

### Różne formaty wyjściowe

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
