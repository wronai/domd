# DoMD - Wykrywacz komend projektowych

<div align="center">

![DoMD Logo](assets/logo.png)

**Automatyczne wykrywanie i wykonywanie komend w projektach programistycznych**

[![Wersja PyPI](https://img.shields.io/pypi/v/domd.svg)](https://pypi.org/project/domd/)
[![Wspierane wersje Pythona](https://img.shields.io/pypi/pyversions/domd.svg)](https://pypi.org/project/domd/)
[![Licencja](https://img.shields.io/badge/Licencja-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Testy](https://github.com/wronai/domd/workflows/Tests/badge.svg)](https://github.com/wronai/domd/actions)
[![Pokrycie kodu](https://codecov.io/gh/wronai/domd/branch/main/graph/badge.svg)](https://codecov.io/gh/wronai/domd)
[![Dokumentacja](https://img.shields.io/badge/dokumentacja-aktualna-brightgreen.svg)](https://domd.readthedocs.io/)

</div>

## 🌟 Czym jest DoMD?

DoMD to narzędzie do automatycznego wykrywania i wykonywania komend w projektach programistycznych. Automatycznie analizuje pliki konfiguracyjne projektu i generuje raporty z wykonania komend.

### Główne funkcje

- **Automatyczne wykrywanie** komend z popularnych plików konfiguracyjnych
- **Wykonywanie komend** z obsługą błędów i limitów czasowych
- **Generowanie raportów** w formacie Markdown, JSON lub zwykłym tekście
- **Integracja z Dockerem** do izolowanego wykonywania komend
- **Obsługa wielu języków** i narzędzi programistycznych
- **Konfigurowalne** z użyciem plików `.domdignore` i `.dodocker`

## 🚀 Szybki start

```bash
# Instalacja
pip install domd

# Uruchomienie w katalogu projektu
domd
```

## 📖 Spis treści

1. [Instalacja](installation.md) - Jak zainstalować i skonfigurować DoMD
2. [Użycie](usage.md) - Szczegółowy przewodnik po funkcjach
3. [Funkcje](features/) - Opis dostępnych funkcji i możliwości
4. [API](api.md) - Dokumentacja interfejsu programistycznego
5. [Rozwój](development/) - Informacje dla programistów

## 🌍 Wspierane języki i narzędzia

- **Python**: `pyproject.toml`, `setup.py`, `requirements.txt`
- **JavaScript/Node.js**: `package.json`
- **Make**: `Makefile`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Ansible**: Playbooki, role i inventory
- Oraz wiele innych...

## 📊 Przykładowy raport

```markdown
# Raport DoMD - 2023-11-15 14:30:00

## ✅ Zakończone pomyślnie
- `pytest` - Testy jednostkowe (1.2s)
- `black .` - Formatowanie kodu (0.8s)

## ❌ Błędy
- `mypy .` - Błąd typowania (2.1s)
  ```
  error: Function is missing a return type annotation
  ```

## ⚠ Ostrzeżenia
- `bandit -r .` - Znaleziono potencjalne problemy bezpieczeństwa (3.4s)
  - Uwaga: Użycie niebezpiecznej funkcji `eval` w pliku `utils.py:42`
```

## 🤝 Wsparcie

Masz pytania lub problemy? [Zgłoś issue](https://github.com/wronai/domd/issues) lub skorzystaj z naszej dokumentacji.

## 📜 Licencja

[Apache 2.0](LICENSE) © 2023 WronAI
