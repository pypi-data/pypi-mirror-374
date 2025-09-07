# reposmith/ci_utils.py
from __future__ import annotations
import textwrap
from pathlib import Path
from .core.fs import write_file

def ensure_github_actions_workflow(
    root_dir: Path,
    path: str = ".github/workflows/ci.yml",
    *,
    py: str = "3.12",
    program: str = "app.py",  # للإبقاء على التوافق الخلفي فقط (غير مستخدم الآن)
    force: bool = False,
) -> str:
    """
    Generate a GitHub Actions workflow that runs unit tests (unittest)
    and forces CI to import the local repo code (not a possibly installed package).
    """
    wf_path = Path(root_dir) / path
    wf_path.parent.mkdir(parents=True, exist_ok=True)

    yml = textwrap.dedent(f"""
    name: Run tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: "{py}"

          - name: Install dependencies (if any)
            run: |
              if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi

          - name: Run unit tests
            run: |
              # Ensure CI uses local repo code for imports and subprocesses
              export PYTHONPATH="$GITHUB_WORKSPACE:$PYTHONPATH"
              # (Optional) remove any installed package that might shadow local code
              pip uninstall -y reposmith-tol || true
              python -m unittest discover -s tests -v
    """).lstrip()

    return write_file(wf_path, yml, force=force, backup=True)

