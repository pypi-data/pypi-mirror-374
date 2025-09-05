# ⚡ RepoSmith 
[![PyPI version](https://img.shields.io/pypi/v/reposmith-tol?style=flat-square)](https://pypi.org/project/reposmith-tol/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-pink?style=flat-square)](https://github.com/sponsors/liebemama)

**RepoSmith** is a **lightweight & portable CLI tool** that helps you **bootstrap new Python projects instantly** 🚀.  
With one command, you get a ready-to-code environment including virtualenv, config files, VS Code setup, `.gitignore`, and license.

---

## ✨ Features
- 🚀 Quick project setup with a single command
- 🐍 Python ≥ 3.12 support
- 📦 Automatic virtual environment creation (`.venv`)
- 📂 Generates essential files:
  - `setup-config.json`, `requirements.txt`, `app.py`
  - `.vscode/` (settings + launch config)
  - `.gitignore`, `LICENSE`
- ⚙️ Preconfigured GitHub Actions workflow
- 🛡️ Built-in MIT license template

---

## ⚡ Quick Start
```powershell
cd MyProject
py -m reposmith.main
```

This will:
- create `.venv/`
- add `requirements.txt`, `app.py`, `.gitignore`, `LICENSE`, `.vscode/`
- configure everything automatically with defaults.

👉 Optional flags:
- `--ci create` → add GitHub Actions workflow
- `--author "YourName"` → set your name in LICENSE

---

## 📦 Installation

### From PyPI
```bash
pip install reposmith-tol
```

### From Source
```bash
git clone https://github.com/liebemama/RepoSmith.git
cd RepoSmith
pip install -e .
```

---

## 🚀 Usage

### CLI
```bash
# Create new project structure in current folder
reposmith --ci create --gitignore python --author "Tamer"
```

### Example
```bash
cd MyNewProject
reposmith --ci create --gitignore django --license MIT --author "Tamer"
```

---

## 🧩 Library API
```python
from reposmith.venv_utils import create_virtualenv, upgrade_pip, install_requirements

venv_dir = "./.venv"
req_file = "./requirements.txt"

create_virtualenv(venv_dir)
upgrade_pip(venv_dir)
install_requirements(venv_dir, req_file)
```

---

## 🛡️ License
This project is licensed under the [MIT License](LICENSE).  
© 2025 TamerOnLine

---

## 💖 Support this project
If you find **RepoSmith** useful, consider supporting its development:  
👉 [Sponsor us on GitHub](https://github.com/sponsors/liebemama)
