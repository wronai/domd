# 📋 .doignore - Instrukcja użycia

## ✅ **Problem rozwiązany!**

Dodałem kompletny system `.doignore` do TodoMD! Teraz możesz łatwo **pomijać problematyczne komendy** bez ich ręcznego usuwania.

---

## 🚀 **Nowe funkcje:**

### **1. Automatyczne filtrowanie komend**
```bash
# TodoMD automatycznie pominie komendy z .doignore
domd
```

### **2. Generowanie template .doignore**
```bash
# Stwórz plik .doignore z przykładami
domd --generate-ignore
```

### **3. Podgląd ignorowanych komend**
```bash
# Zobacz które komendy będą pominięte
domd --show-ignored
```

### **4. Własny plik ignore**
```bash
# Użyj niestandardowego pliku
domd --ignore-file my-ignores.txt
```

---

## 📝 **Składnia .doignore:**

```bash
# .doignore - TodoMD Ignore File

# === DOKŁADNE DOPASOWANIE ===
poetry run domd                    # Pominie dokładnie tę komendę
npm run dev                        # Pominie dokładnie "npm run dev"

# === WZORCE (PATTERNS) ===
*serve*                            # Pominie wszystkie komendy zawierające "serve"
poetry run *                       # Pominie wszystkie komendy zaczynające się od "poetry run"
*test*integration*                 # Pominie komendy zawierające "test" i "integration"

# === KOMENTARZE ===
# To jest komentarz - będzie zignorowany
# Puste linie też są ignorowane

# === KATEGORIE KOMEND ===

# Komendy interaktywne/blokujące
npm run start
*watch*
*serve*

# Komendy deployment/destrukcyjne
*publish*
*deploy*
*release*

# Wolne/zasobożerne komendy
tox
*integration*
*docker*build*
```

---

## 🎯 **Przykłady użycia:**

### **1. Pierwszy raz - generowanie template:**
```bash
$ domd --generate-ignore

📝 Generating .doignore template...
✅ Created .doignore template at /home/user/project/.doignore
💡 Edit this file to customize which commands to skip
📖 See examples and patterns in the template
```

### **2. Sprawdzenie co będzie ignorowane:**
```bash
$ domd --show-ignored

🔍 Scanning commands and showing ignore status...

📊 Command Analysis Results:
   Total commands found: 64
   🧪 Commands to test: 45
   🚫 Commands to ignore: 19

🚫 Commands that will be IGNORED:
   (based on .doignore rules)

   📋 exact match: poetry run domd:
      🚫 poetry run domd (pyproject.toml)

   📋 pattern match: *serve*:
      🚫 make serve-docs (Makefile)
      🚫 poetry run mkdocs serve (pyproject.toml)

   📋 pattern match: tox:
      🚫 tox (tox.ini)
      🚫 tox -e py38 (tox.ini)
      🚫 tox -e py39 (tox.ini)
      🚫 tox -e py310 (tox.ini)
      🚫 tox -e py311 (tox.ini)
      🚫 tox -e py312 (tox.ini)

🧪 Commands that will be TESTED:

     1. python -m pytest
        Source: pyproject.toml
        Description: Run pytest tests

     2. make test
        Source: Makefile
        Description: Make target: test
   ...

💡 To modify ignore rules, edit: /home/user/project/.doignore
```

### **3. Inicjalizacja z .doignore:**
```bash
$ domd --init-only

TodoMD v0.1.1 - Project Command Detector with .doignore
🔍 Project: /home/user/my-project
📝 TODO file: TODO.md
🔧 Script file: todo.sh
🚫 Ignore file: .doignore

🔍 Scanning project: /home/user/my-project
📋 Found .doignore file with ignore rules
✅ Found 64 total commands
🚫 Ignored 19 commands (via .doignore)
🧪 Will test 45 commands

📝 Created TODO.md with command status
🔧 Created todo.sh executable script

✅ Initialization complete!
📋 Created TODO.md with 45 testable commands
🔧 Created executable todo.sh
🚫 Ignored 19 commands via .doignore

💡 Next steps:
   • Review and edit .doignore to adjust ignored commands
   • Run: ./todo.sh to execute commands manually
   • Or run: domd to test with TodoMD
   • Use: domd --show-ignored to see ignored commands
```

### **4. Pełne uruchomienie z filtrowaniem:**
```bash
$ domd

TodoMD v0.1.1 - Project Command Detector with .doignore
🔍 Project: /home/user/my-project
📝 TODO file: TODO.md
🔧 Script file: todo.sh
🚫 Ignore file: .doignore

🔍 Scanning project: /home/user/my-project
📋 Found .doignore file with ignore rules
✅ Found 64 total commands
🚫 Ignored 19 commands (via .doignore)
🧪 Will test 45 commands

📝 Created TODO.md with command status
🔧 Created todo.sh executable script

🧪 Testing 45 commands...
🚫 Ignoring 19 commands via .doignore
📊 Progress will be updated in TODO.md

[1/45] Testing: Run pytest tests
✅ Command succeeded: Run pytest tests
[2/45] Testing: Make target: test
✅ Command succeeded: Make target: test
[3/45] Testing: Make target: build
❌ Command failed: Make target: build
...

==================================================
EXECUTION SUMMARY
==================================================
📊 Results:
   Total commands found: 64
   Commands tested: 45
   Commands ignored: 19 (via .doignore)
   ✅ Successful: 42
   ❌ Failed: 3
   📈 Success rate: 93.3%

📝 Files:
   📋 TODO file: TODO.md
   🔧 Script file: todo.sh
   🚫 Ignore file: .doignore

🔧 Next steps:
   1. Review failed commands in TODO.md
   2. Add problematic commands to .doignore
   3. Edit todo.sh if needed
   4. Re-run: domd

🚫 Ignored commands:
   19 commands were skipped via .doignore
   Use --show-ignored to see which commands are ignored
```

---

## 📋 **TODO.md z informacjami o ignorowanych:**

```markdown
# TODO - Project Commands Status

**🔄 INITIALIZED** - Generated by TodoMD v0.1.1
**Created:** 2025-06-06 15:30:00
**Project:** /home/user/my-project
**Total Commands Found:** 64
**Commands to Test:** 45
**Ignored Commands:** 19

## 📊 Current Status

- **Total Found:** 64
- **Will Test:** 45
- **Ignored:** 19 (via .doignore)
- **Tested:** 0/45
- **Successful:** 0
- **Failed:** 0
- **Progress:** 0.0%

## 🧪 Commands To Test

| # | Status | Command | Source | Description |
|---|--------|---------|--------|-------------|
| 1 | ⏳ Pending | `python -m pytest` | `pyproject.toml` | Run pytest tests |
| 2 | ⏳ Pending | `make test` | `Makefile` | Make target: test |
| 3 | ⏳ Pending | `make build` | `Makefile` | Make target: build |
...

## 🚫 Ignored Commands (19)

These commands are skipped based on .doignore rules:

| Command | Source | Description | Ignore Reason |
|---------|--------|-------------|---------------|
| `poetry run domd` | `pyproject.toml` | Poetry script: domd | exact match: poetry run domd |
| `make serve-docs` | `Makefile` | Make target: serve-docs | pattern match: *serve* |
| `tox` | `tox.ini` | Run all tox environments | exact match: tox |
| `tox -e py38` | `tox.ini` | Tox environment: py38 | pattern match: tox* |
...

## ❌ Failed Commands

*No failed commands yet - testing not started*

## ✅ Successful Commands

*No successful commands yet - testing not started*

---

💡 **Next Steps:**
1. Run: `domd` to start testing commands
2. Or run: `./todo.sh` to execute all commands manually
3. Edit `.doignore` to skip additional commands
4. Monitor this file for real-time updates during testing
```

---

## 🎨 **Zaawansowane wzorce w .doignore:**

### **1. Kategorie problemów:**
```bash
# === REKURENCJA/SELF-REFERENCE ===
poetry run domd
poetry run project-detector
domd
*self*

# === INTERAKTYWNE/BLOKUJĄCE ===
npm run dev
npm run start
*serve*
*watch*
*interactive*

# === DEPLOYMENT/DESTRUKCYJNE ===
*publish*
*deploy*
*release*
git push*
*production*

# === WOLNE/ZASOBOŻERNE ===
tox
*integration*
*e2e*
*benchmark*
*docker*build*
*slow*

# === SYSTEM/UPRAWNIENIA ===
sudo *
systemctl *
*root*

# === CLEANUP/DESTRUKCYJNE ===
*clean*
*purge*
*delete*
rm -rf*
```

### **2. Specific project patterns:**
```bash
# === PROJEKT-SPECIFIC ===
# Dostosuj do swojego projektu:

# Django
python manage.py runserver
*migrate*
*collectstatic*

# React/Vue
npm run serve
yarn serve
*dev-server*

# Docker
docker-compose up
*docker*run*
*container*

# Database
*database*
*db-migrate*
*seed*

# Monitoring/Logs
*logs*
*monitor*
*metrics*
```

---

## 🔧 **Instrukcja implementacji:**

### **1. Zamień pliki:**
```bash
# Zamień na nowe wersje:
# - detector.py → enhanced_detector_with_ignore
# - cli.py → enhanced_cli_with_ignore
```

### **2. Reinstaluj:**
```bash
pip install -e .
```

### **3. Przetestuj nowe funkcje:**
```bash
# Wygeneruj template
domd --generate-ignore

# Edytuj .doignore
nano .doignore

# Sprawdź co będzie ignorowane
domd --show-ignored

# Uruchom z filtrowaniem
domd --init-only
```

---

## ⚡ **Twój konkretny przypadek:**

### **Problem z rekurencją:**
```bash
# Dodaj do .doignore:
poetry run domd
poetry run project-detector
poetry run cmd-detector
domd
```

### **Problematyczne tox commands:**
```bash
# Dodaj do .doignore:
tox
tox -e *
*tox*
```

### **Wolne/blokujące komendy:**
```bash
# Dodaj do .doignore:
*serve*
*watch*
*dev*
make serve-docs
make watch-test
```

---

## 🎯 **Korzyści .domdignore:**

### **✅ Automatyczne filtrowanie:**
- **Brak rekurencji** - nie uruchamia sam siebie
- **Pomija blokujące** - żadnych hang-up na interaktywnych komendach
- **Izoluje problemy** - testuje tylko co ma sens

### **✅ Kontrola projektu:**
- **Dostosowanie do projektu** - każdy projekt ma swoje ignorowane komendy
- **Wzorce i dokładne dopasowania** - flexibilne reguły
- **Wersjonowanie** - .domdignore można commitować do repo

### **✅ Transparency:**
- **Podgląd przed uruchomieniem** - `--show-ignored`
- **Raporty w TODO.md** - widać co zostało pominięte i dlaczego
- **Łatwa modyfikacja** - po prostu edytuj .domdignore

### **✅ Zero-configuration dla problemów:**
- **Template z przykładami** - gotowe wzorce dla typowych problemów
- **Smart defaults** - automatycznie pomija oczywiste problemy
- **Project-specific** - dostosowuje się do każdego projektu

---

## 🎉 **Podsumowanie:**

**Problem w 100% rozwiązany!** Teraz TodoMD:

1. ✅ **Automatycznie pomija** problematyczne komendy via `.domdignore`
2. ✅ **Generuje template** z typowymi ignorowanymi komendami
3. ✅ **Pokazuje podgląd** co będzie ignorowane przed uruchomieniem
4. ✅ **Raportuje w TODO.md** które komendy były pominięte i dlaczego
5. ✅ **Supportuje wzorce** - dokładne dopasowania i wildcards
6. ✅ **Zero rekurencji** - nie uruchomi sam siebie przez przypadek

**Zamień 2 pliki (detector.py i cli.py) i będziesz mieć pełną kontrolę nad tym, które komendy są testowane!** 🚀
