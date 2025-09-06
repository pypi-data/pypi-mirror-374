# ⚡ RepoSmith 

[![PyPI version](https://img.shields.io/pypi/v/reposmith-tol?style=flat-square)](https://pypi.org/project/reposmith-tol/)
![Python](https://img.shields.io/pypi/pyversions/reposmith-tol?style=flat-square)
![License](https://img.shields.io/github/license/liebemama/RepoSmith?style=flat-square)
[![CI](https://github.com/liebemama/RepoSmith/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/liebemama/RepoSmith/actions/workflows/ci.yml)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-pink?style=flat-square)](https://github.com/sponsors/liebemama)



**RepoSmith** is a **portable Python project bootstrapper** — a zero-dependency CLI & library that helps you spin up new projects instantly.  
With one command, you get a ready-to-code environment: virtualenv, config files, VS Code setup, `.gitignore`, LICENSE, and optional CI.

---

## ✨ Features
- 🚀 **Zero dependencies** — built only with Python stdlib
- ⚙️ **Virtual environment** auto-created (`.venv`)
- 📦 **requirements.txt** scaffolded (empty but ready)
- 📝 **Entry file** (`main.py` or `run.py`) with a welcome message
- 🛡 **LICENSE** (MIT by default, more soon)
- 🙈 **.gitignore** presets (Python, Node, Django…)
- 💻 **VS Code config** (`settings.json`, `launch.json`, workspace)
- 🔄 **GitHub Actions** workflow (`.github/workflows/test-main.yml`)
- 🔧 Idempotent: runs safely again without overwriting unless `--force`

---

## ⚡ Quick Start

### Option 1 — run via Python module (always works)
```powershell
cd MyProject
py -m reposmith.main init --entry run.py --with-vscode --with-ci
```

### Option 2 — run via CLI (if Scripts folder is on PATH)
```powershell
reposmith init --entry run.py --with-vscode --with-ci
```

Both commands will:
- create `.venv/`
- add `requirements.txt`, `run.py`, `.gitignore`, `LICENSE`, `.vscode/`
- configure everything automatically with defaults

---

## 🚀 Usage

Basic:
```powershell
reposmith init --entry main.py
```

With extras:
```powershell
reposmith init --entry run.py --with-ci --with-gitignore --with-license --with-vscode --author "YourName"
```

Flags:
- `--force` → overwrite existing files (with `.bak` backup)
- `--no-venv` → skip creating `.venv`
- `--with-license` → add LICENSE (MIT)
- `--with-gitignore` → add .gitignore (Python preset by default)
- `--with-vscode` → add VS Code config
- `--with-ci` → add GitHub Actions workflow
- `--author` / `--year` → customize LICENSE metadata
- `--ci-python` → set Python version for CI (default: 3.12)

---

## 📦 Installation
```powershell
py -m pip install --upgrade reposmith-tol
```

If PATH not configured, use:
```powershell
py -m reposmith.main init --entry run.py
```

---

## 🧪 Development
Run tests:
```powershell
python -m unittest discover -s tests -v
```

---

## 🗺️ Roadmap



🔗 [Follow the project progress on GitHub Projects](https://github.com/orgs/liebemama/projects/2)


---


## 🛡 License
This project is licensed under the [MIT License](https://github.com/liebemama/RepoSmith/blob/main/LICENSE).  
© 2025 TamerOnLine

---

## 💬 Support

- 🐛 **Report Issues:** [GitHub Issues](https://github.com/liebemama/RepoSmith/issues)  
- 💡 **Feature Requests:** [GitHub Issues](https://github.com/liebemama/RepoSmith/issues) (اختر نوع *Feature Request*)  
- 💖 **Sponsor:** [GitHub Sponsors](https://github.com/sponsors/liebemama)  
- 📧 **Contact:** (info@tameronline.com)
