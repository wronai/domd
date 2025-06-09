# DoMD - Project Command Detector

DoMD to narzędzie do automatycznego wykrywania, testowania i raportowania komend projektowych. Skanuje pliki konfiguracyjne projektu, wykrywa komendy, wykonuje je i generuje raporty o sukcesach i błędach.

## 🚀 Główne funkcje

- **Wykrywanie komend**: Automatyczne wykrywanie komend z różnych plików konfiguracyjnych (package.json, Makefile, pyproject.toml, itp.)
- **Testowanie komend**: Wykonywanie komend z obsługą błędów i timeoutów
- **Raportowanie**: Generowanie raportów w formacie Markdown, JSON lub tekstu
- **Ignorowanie komend**: Możliwość ignorowania określonych komend za pomocą pliku `.doignore`
- **Wsparcie dla środowisk wirtualnych**: Integracja z wirtualnymi środowiskami Python

## 📦 Wspierane typy projektów

- **JavaScript/Node.js**: `package.json` (skrypty npm)
- **Python**: `pyproject.toml`, `setup.py`, `requirements.txt`
- **Make**: `Makefile`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Ansible**: Playbooki, role, inwentarze
- **PHP**: `composer.json`
- **Rust**: `Cargo.toml`
- **Inne**: Pliki TOML, YAML, INI

## 🛠 Instalacja

```bash
pip install domd
```

## 📖 Użycie

### Podstawowe użycie
```bash
# Skanowanie bieżącego katalogu
domd

# Skanowanie określonego projektu
domd --path /ścieżka/do/projektu

# Podgląd komend bez wykonywania
domd --dry-run

# Niestandardowy plik wyjściowy
domd --output FAILED_COMMANDS.md
```

### Zaawansowane opcje
```bash
# Szczegółowe logi
domd --verbose

# Tryb cichy (tylko błędy)
domd --quiet

# Niestandardowy timeout (domyślnie: 60 sekund)
domd --timeout 120

# Różne formaty wyjściowe
domd --format json
domd --format text

# Wykluczanie określonych wzorców
domd --exclude "*.test.js" --exclude "node_modules/*"

# Uwzględnianie tylko określonych wzorców
domd --include-only "Makefile" --include-only "package.json"
```

## 🔧 Ignorowanie komend z .doignore

Utwórz plik `.doignore` w katalogu głównym projektu, aby pominąć określone komendy podczas testowania.

### Przykładowy plik `.doignore`:
```
# Pomijanie określonych komend
npm run dev
npm run start

# Pomijanie wzorców
*serve*
*deploy*
*release*

# Pomijanie komend testowych
*test*
*e2e*
```

### Użycie:
```bash
# Wygeneruj szablon pliku .doignore
domd --generate-ignore

# Pokaż, które komendy byłyby ignorowane
domd --show-ignored

# Użyj niestandardowego pliku ignorowania
domd --ignore-file custom.ignore
```

## 📊 Przykładowy wynik

Gdy komendy nie powodzą się, DoMD generuje ustrukturyzowany plik TODO.md:

```markdown
# TODO - Nieudane komendy projektu

Automatycznie wygenerowane przez DoMD v0.1.0
Data: 2025-06-06 10:30:15
Projekt: /home/user/my-project

Znaleziono **2** komendy wymagające naprawy:

## Zadanie 1: Skrypt NPM - test

**Źródło:** `package.json`
**Kod zwrotny:** 1

### Komenda do naprawy:
```bash
npm run test
```

### Błąd:
```
Error: Cannot find module 'jest'
npm ERR! Test failed. See above for more details.
```

### Sugerowane działania:
- [ ] Zainstaluj brakujące zależności: `npm install`
- [ ] Sprawdź, czy jest w devDependencies
- [ ] Zweryfikuj konfigurację testów
- [ ] Uruchom `npm install --save-dev jest` jeśli brakuje

---

## Zadanie 2: Cel Make - build

**Źródło:** `Makefile`
**Kod zwrotny:** 2

### Komenda do naprawy:
```bash
make build
```

### Błąd:
```
make: *** No rule to make target 'src/main.c', needed by 'build'. Stop.
```

### Sugerowane działania:
- [ ] Sprawdź, czy pliki źródłowe istnieją
- [ ] Zweryfikuj ścieżki i zależności w Makefile
- [ ] Przejrzyj konfigurację budowania
- [ ] Upewnij się, że wszystkie wymagane pliki są obecne
```

## 🔍 Architektura

DoMD składa się z kilku kluczowych komponentów:

1. **ProjectCommandDetector** - Główny moduł wykrywający i wykonujący komendy
2. **CommandHandler** - Zarządza wykonywaniem komend i logiką ignorowania
3. **PatternMatcher** - Zapewnia metody dopasowywania wzorców (`match_command`)
4. **Reporter** - Zarządza generowaniem raportów za pomocą formaterów
5. **Formatters** - Obiekty formatujące raporty (MarkdownFormatter, JsonFormatter, itp.)

## 🔄 Przepływ pracy

1. Skanowanie plików konfiguracyjnych projektu
2. Wykrywanie komend
3. Wykonywanie komend (lub ich ignorowanie na podstawie wzorców z `.doignore`)
4. Generowanie raportów dla udanych i nieudanych komend
5. Tworzenie plików TODO.md i DONE.md

## 🐛 Rozwiązywanie problemów

- **Błąd "Command failed after X attempts"**: Sprawdź, czy komenda istnieje i może być wykonana w bieżącym środowisku
- **Problemy z formatowaniem raportów**: Upewnij się, że formatery są używane jako obiekty z metodami `format_report` i `write_report`
- **Problemy z ignorowaniem komend**: Sprawdź, czy plik `.doignore` istnieje i ma poprawny format

## 🤝 Współpraca

Zachęcamy do współpracy! Jeśli chcesz pomóc w rozwoju DoMD:

1. Sklonuj repozytorium
2. Utwórz nową gałąź
3. Wprowadź zmiany
4. Wyślij pull request
