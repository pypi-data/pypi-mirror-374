from .core.fs import write_file
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

from pathlib import Path


def create_gitignore(root_dir, preset: str = "python", *, force: bool = False) -> str:
    """
    Create or update a .gitignore file safely.

    This function writes a .gitignore file in the given root directory
    based on predefined presets. It will not overwrite an existing file
    unless `force=True` is specified. If overwriting occurs, a backup
    (`.bak`) file is created automatically. The writing process is
    performed atomically to prevent data corruption.

    Args:
        root_dir (str or Path): The target directory where the .gitignore
            file should be created.
        preset (str, optional): The preset to use for the .gitignore
            content. Defaults to "python".
        force (bool, optional): If True, overwrite the existing file.
            Defaults to False.

    Returns:
        str: A status string describing the result. Possible values include:
            - "exists": The file already exists and was not overwritten.
            - Other states as defined by `write_file`.

    Notes:
        - Requires `PRESETS`, `PYTHON_GITIGNORE`, and `write_file` to be
          defined in the surrounding scope.
    """
    path = Path(root_dir) / ".gitignore"
    content = PRESETS.get(preset.lower(), PYTHON_GITIGNORE)

    state = write_file(path, content, force=force, backup=True)
    if state == "exists":
        print(".gitignore already exists. Use --force to overwrite.")
    else:
        print(f".gitignore created/updated with preset: {preset}")
    return state

