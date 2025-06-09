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

### Częste problemy

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
