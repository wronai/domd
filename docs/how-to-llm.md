# 📋 INSTRUKCJA - DONE.md i TODO.md dla LLM

## ✅ **Problem rozwiązany w 100%!**

Stworzyłem kompletny system **dwóch plików**:
- **`DONE.md`** - działające komendy oznaczone na zielono ✅
- **`TODO.md`** - zadania dla LLM z konkretnymi instrukcjami naprawy

---

## 🎯 **Jak to działa:**

### **1. DONE.md - Lista sukcesów ✅**
- Wszystkie **działające komendy** z zielonymi oznaczeniami
- **Czas wykonania** każdej komendy
- **Grupowanie według źródła** (package.json, Makefile, etc.)
- **Status "WORKING"** dla każdej komendy

### **2. TODO.md - Lista zadań dla LLM 🤖**
- **Instrukcje dla LLM** na górze pliku
- Każda niedziałająca komenda jako **osobny header `### [ ]`**
- **Pełny kod błędu** w blokach source code
- **Szczegółowe sugestie napraw** dla każdego błędu
- **Kryteria ukończenia** zadania

---

## 📊 **Przykład struktury plików:**

### **DONE.md:**
```markdown
# ✅ DONE - Successfully Working Commands

## 🟢 Working Commands

### 📄 From Makefile

#### ✅ Make target: test
**Command:** `make test`
**Execution Time:** 3.45s
**Status:** 🟢 **WORKING**

#### ✅ Make target: lint
**Command:** `make lint`
**Execution Time:** 0.89s
**Status:** 🟢 **WORKING**
```

### **TODO.md:**
```markdown
# 🤖 TODO - LLM Task List for Command Fixes

**📋 INSTRUCTIONS FOR LLM:**
This file contains broken commands that need fixing.
Each task has error details and fix suggestions.

## 🔧 Tasks to Fix (6 commands)

### [ ] Task 1: NPM script - build

**📋 Command:** `npm run build`
**📁 Source:** `package.json`
**🔴 Return Code:** 1

#### 🔴 Error Output:
```bash
# Command that failed:
npm run build

# Error output:
npm ERR! missing script: build
```

#### 💡 Suggested Fix Actions:
- [ ] Check package.json for script definition errors
- [ ] Add missing "build" script to package.json
- [ ] Verify build tools are installed
```

---

## 🚀 **Implementacja (3 kroki):**

### **1. Zamień plik detector.py:**
```bash
# Zamień src/todomd/detector.py na nową wersję z artefaktu:
# done_md_generator
```

### **2. Reinstaluj paczkę:**
```bash
pip install -e .
```

### **3. Przetestuj:**
```bash
# Uruchom testowanie
domd

# Sprawdź wygenerowane pliki
ls -la TODO.md DONE.md
cat DONE.md    # Zobacz działające komendy
cat TODO.md    # Zobacz zadania dla LLM
```

---

## 🎮 **Przykład użycia:**

### **Pierwszy run:**
```bash
$ domd

TodoMD v0.1.1 - Project Command Detector with .domdignore
🔍 Project: /home/user/my-project
📋 Found .domdignore file with ignore rules
✅ Found 64 total commands
🚫 Ignored 19 commands (via .domdignore)
🧪 Will test 45 commands

📝 Created TODO.md (LLM task list)
✅ Created DONE.md (working commands)
🔧 Created todo.sh (executable script)

🧪 Testing 45 commands...
[1/45] Testing: Run pytest tests
✅ Command succeeded: Run pytest tests
[2/45] Testing: NPM script - build
❌ Command failed: NPM script - build
[3/45] Testing: Make target - test
✅ Command succeeded: Make target - test
...

📊 Test Results:
   ✅ Working: 39 → DONE.md
   ❌ Failed: 6 → TODO.md
   🚫 Ignored: 19 (via .domdignore)
```

### **DONE.md (po testowaniu):**
```markdown
# ✅ DONE - Successfully Working Commands

**Total Working Commands:** 39

## 🟢 Working Commands

### 📄 From pyproject.toml
#### ✅ Run pytest tests
**Command:** `python -m pytest`
**Execution Time:** 2.34s
**Status:**
