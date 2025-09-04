# reposmith/ci_utils.py
from pathlib import Path
import textwrap

def ensure_github_actions_workflow(
    root_dir: Path,
    path: str = ".github/workflows/test-main.yml",
    *,
    py: str = "3.12",
    program: str = "app.py",
    force: bool = False,
    backup: bool = True,
) -> str:
    base = Path(root_dir)
    wf_path = base / path
    wf_path.parent.mkdir(parents=True, exist_ok=True)

    if wf_path.exists() and not force:
        return "exists"

    if wf_path.exists() and backup:
        bak = wf_path.with_suffix(wf_path.suffix + ".bak")
        bak.write_text(wf_path.read_text(encoding="utf-8"), encoding="utf-8")

    yml = textwrap.dedent(f"""
    name: Test {program}

    on: [push, pull_request]

    jobs:
      run-script:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: "{py}"

          - name: Cache pip
            uses: actions/cache@v4
            with:
              path: ~/.cache/pip
              key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
              restore-keys: |
                ${{{{ runner.os }}}}-pip-

          - name: Install requirements
            run: |
              python -m pip install --upgrade pip
              if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

          - name: Run {program}
            run: |
              if [ -f "{program}" ]; then
                echo "Running file: {program}"
                python "{program}"
              else
                echo "Program file not found. Running module fallback..."
                python -m reposmith.main --ci skip
                python -c "import reposmith; print('import ok')"
              fi
    """)

    wf_path.write_text(yml.strip() + "\n", encoding="utf-8")
    return "overwritten" if force else "created"
