from pathlib import Path

PYTHON_GITIGNORE = """# =========================
# 🧠 Python: Bytecode, Caches, Compiled Files
# =========================
__pycache__/
*.py[cod]
*$py.class
*.so
*.sage.py
*.manifest
*.spec
cython_debug/

# =========================
# ⚙️ Virtual Environments
# =========================
.env
.venv
env/
venv/
venv*/
ENV/
env.bak/
venv.bak/
.pdm-python
.pdm-build/
__pypackages__/

# =========================
# 📦 Package/Build Artifacts
# =========================
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# =========================
# 📄 Installer Logs
# =========================
pip-log.txt
pip-delete-this-directory.txt

# =========================
# 🧪 Testing / Coverage
# =========================
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# =========================
# 🌍 Translations
# =========================
*.mo
*.pot

# =========================
# 🌐 Django / Flask / Scrapy
# =========================
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
instance/
.webassets-cache
.scrapy

# =========================
# 📚 Documentation
# =========================
docs/_build/
.site
.pybuilder/
target/
.mypy_cache/
.dmypy.json
dmypy.json
.pytype/
.pyre/
.ruff_cache/

# =========================
# 🧪 IDE / Editor Configs
# =========================
.vscode/
.idea/
.spyderproject
.spyproject
.ropeproject

# =========================
# 📓 Jupyter / IPython
# =========================
.ipynb_checkpoints
profile_default/
ipython_config.py

# =========================
# 🔧 pyenv / Poetry / Pipenv / PDM / UV
# =========================
.python-version
# Pipfile.lock
# poetry.lock
# pdm.lock
.pdm.toml
# uv.lock

# =========================
# 🧵 Celery
# =========================
celerybeat-schedule
celerybeat.pid

# =========================
# 🧠 AI Editors / Tools
# =========================
.abstra/
.cursorignore
.cursorindexingignore

# =========================
# 🔐 Private / Config Files
# =========================
.pypirc
*.code-workspace

# =========================
# 🧾 user-specific files
# =========================
gitingest.txt
*info/
publish.py
publish_test.py
venv_switcher.py
summary_tree.txt
Dev_requirements.txt
*.exe

# Local cache from the app
.cache/

# OS junk
.DS_Store
Thumbs.db

# Generated env info 
env-info.txt
"""

NODE_GITIGNORE = """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-store/
dist/
build/
# IDE
.vscode/
.idea/
# OS
.DS_Store
Thumbs.db
"""

DJANGO_GITIGNORE = PYTHON_GITIGNORE + """# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
"""

PRESETS = {
    "python": PYTHON_GITIGNORE,
    "node": NODE_GITIGNORE,
    "django": DJANGO_GITIGNORE,
}

def create_gitignore(root_dir, preset: str = "python") -> None:
    print("\n[9] Checking .gitignore")
    path = Path(root_dir) / ".gitignore"
    if path.exists():
        print(".gitignore already exists.")
        return
    content = PRESETS.get(preset.lower(), PYTHON_GITIGNORE)
    path.write_text(content, encoding="utf-8")
    print(f".gitignore created with preset: {preset}")
