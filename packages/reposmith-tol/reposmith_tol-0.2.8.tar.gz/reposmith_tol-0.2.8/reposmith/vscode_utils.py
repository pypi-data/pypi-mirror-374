# reposmith/vscode_utils.py
from __future__ import annotations

import os
import json
from pathlib import Path

from .core.fs import write_file


import os
from pathlib import Path


def _venv_python_path(venv_dir: Path) -> str:
    """
    Return the Python interpreter path for Visual Studio Code.

    This function determines the appropriate Python interpreter path 
    based on the presence of a virtual environment (venv). 

    Args:
        venv_dir (Path): The directory of the virtual environment.

    Returns:
        str: The path to the Python interpreter. 
             - If the venv exists, its interpreter is used.
             - Otherwise, falls back to 'python.exe' (Windows) 
               or 'python3' (Linux/Mac).
    """
    if os.name == "nt":
        candidate = Path(venv_dir) / "Scripts" / "python.exe"
        return str(candidate) if candidate.exists() else "python.exe"
    else:
        candidate = Path(venv_dir) / "bin" / "python3"
        return str(candidate) if candidate.exists() else "python3"



def create_vscode_files(
    root_dir: Path,
    venv_dir: Path,
    *,
    main_file: str = "main.py",
    force: bool = False,
) -> None:
    """
    Safely create/update VS Code configuration files for a project.

    This function generates the following:
        - .vscode/settings.json: Sets Python interpreter from the virtual environment.
        - .vscode/launch.json: Configures debugging for the main script.
        - project.code-workspace: Creates a simple workspace file.

    Args:
        root_dir (Path): Project root directory where files will be created.
        venv_dir (Path): Path to the virtual environment.
        main_file (str, optional): Name of the main file to run. Defaults to "main.py".
        force (bool, optional): Overwrite existing files if True. Defaults to False.

    Returns:
        None
    """
    root = Path(root_dir)
    vscode = root / ".vscode"
    vscode.mkdir(parents=True, exist_ok=True)

    py_path = _venv_python_path(venv_dir)

    # settings.json
    settings = {
        "python.defaultInterpreterPath": py_path,
        "python.analysis.autoImportCompletions": True,
        "terminal.integrated.env.windows": {
            # Placeholder for environment variables if needed
        },
    }
    settings_path = vscode / "settings.json"
    write_file(
        settings_path,
        json.dumps(settings, indent=2),
        force=force,
        backup=True,
    )

    # launch.json
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": f"Python: {main_file}",
                "type": "python",
                "request": "launch",
                "program": main_file,
                "console": "integratedTerminal",
            }
        ],
    }
    launch_path = vscode / "launch.json"
    write_file(
        launch_path,
        json.dumps(launch, indent=2),
        force=force,
        backup=True,
    )

    # workspace (optional but useful)
    workspace = {
        "folders": [{"path": "."}],
        "settings": {"python.defaultInterpreterPath": py_path},
    }
    ws_path = root / "project.code-workspace"
    write_file(
        ws_path,
        json.dumps(workspace, indent=2),
        force=force,
        backup=True,
    )

    print(
        "VS Code files updated: settings.json, launch.json, project.code-workspace"
    )
