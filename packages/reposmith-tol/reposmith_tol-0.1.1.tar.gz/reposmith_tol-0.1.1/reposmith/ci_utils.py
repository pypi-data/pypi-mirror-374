from pathlib import Path
import textwrap

def ensure_github_actions_workflow(root_dir: Path, path=".github/workflows/test-main.yml", *, py="3.12", force=False, backup=True) -> str:
    base = Path(root_dir)
    wf_path = base / path
    wf_path.parent.mkdir(parents=True, exist_ok=True)

    if wf_path.exists() and not force:
        return "exists"

    if wf_path.exists() and backup:
        bak = wf_path.with_suffix(wf_path.suffix + ".bak")
        bak.write_text(wf_path.read_text(encoding="utf-8"), encoding="utf-8")

    yml = textwrap.dedent(f"""
    name: Test main.py

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

          - name: Install minimal requirements (if any)
            run: |
              python -m pip install --upgrade pip

          - name: Run main.py
            run: |
              python main.py
    """)
    wf_path.write_text(yml.strip() + "\n", encoding="utf-8")
    return "overwritten" if force else "created"
