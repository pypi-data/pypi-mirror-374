# reposmith/ci_utils.py

from __future__ import annotations

import textwrap
from pathlib import Path

from .core.fs import write_file


def ensure_github_actions_workflow(
    root_dir: Path,
    path: str = ".github/workflows/test-main.yml",
    *,
    py: str = "3.12",
    program: str = "app.py",
    force: bool = False,
) -> str:
    """Generate a simple GitHub Actions workflow file.

    This function creates a minimal GitHub Actions CI workflow file that runs a
    Python program in a specified environment. It avoids overwriting existing files
    unless explicitly allowed.

    Args:
        root_dir (Path): The root directory where the workflow will be created.
        path (str, optional): The relative path for the workflow file.
            Defaults to ".github/workflows/test-main.yml".
        py (str, optional): The Python version to use in the workflow.
            Defaults to "3.12".
        program (str, optional): The program to run in the workflow.
            Defaults to "app.py".
        force (bool, optional): If True, overwrite the workflow file if it exists.
            A backup with `.bak` extension is created. Defaults to False.

    Returns:
        str: The state of the operation:
            - "written" if the file was successfully created or replaced.
            - "exists" if the file already existed and was not overwritten.

    Notes:
        - Atomic write is ensured.
        - A `.bak` file is created when replacing an existing workflow file.
    """
    wf_path = Path(root_dir) / path
    wf_path.parent.mkdir(parents=True, exist_ok=True)

    yml = textwrap.dedent(f"""
    name: Test {program}
    on: [push, pull_request]
    jobs:
      run:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: "{py}"

          - name: Install dependencies
            run: |
              if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi

          - name: Run {program}
            run: python "{program}"
    """).lstrip()

    state = write_file(wf_path, yml, force=force, backup=True)
    return state
