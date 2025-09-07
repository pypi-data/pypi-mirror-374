from .core.fs import write_file
from pathlib import Path
from typing import Union

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
.env.*
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
.coverage
.coverage.*
.pytest_cache/
.ruff_cache/
.mypy_cache/
.pytype/
.pyre/
.dmypy.json
.tox/
.nox/
nosetests.xml
coverage.xml
coverage/
*.cover
*.py,cover
.hypothesis/

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
dmypy.json

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
*.bak
*.orig
*.rej
*.swp
*.tmp
*.tmp.*

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
# Env files
.env
.env.*
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

PRESETS: dict[str, str] = {
    "python": PYTHON_GITIGNORE,
    "node": NODE_GITIGNORE,
    "django": DJANGO_GITIGNORE,
}

def create_gitignore(root_dir: Union[str, Path], preset: str = "python", *, force: bool = False) -> str:
    """
    Create or update a .gitignore file safely.

    Args:
        root_dir: Target directory (str or Path).
        preset: One of PRESETS keys ("python", "node", "django").
        force: Overwrite if exists (creates .bak).

    Returns:
        str: "written" | "exists" (from write_file).
    """
    path = Path(root_dir) / ".gitignore"
    key = preset.lower().strip()
    if key not in PRESETS:
        print(f"[gitignore] Unknown preset '{preset}', falling back to 'python'. Available: {', '.join(PRESETS)}")
        key = "python"
    content = PRESETS[key]

    state = write_file(path, content, force=force, backup=True)
    if state == "exists":
        print(".gitignore already exists. Use --force to overwrite.")
    else:
        print(f".gitignore created/updated with preset: {key}")
    return state
