import os
import json
from pathlib import Path

def create_vscode_files(root_dir: Path, venv_dir: str) -> None:
    print("\n[8] Creating VS Code files: settings, launch, workspace")

    ws_dir = Path(root_dir)
    vscode_dir = ws_dir / ".vscode"
    settings_path = vscode_dir / "settings.json"
    launch_path = vscode_dir / "launch.json"
    workspace_path = ws_dir / "project.code-workspace"

    os.makedirs(vscode_dir, exist_ok=True)

    interp = (
        os.path.join(venv_dir, "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(venv_dir, "bin", "python")
    )

    settings = {
        "python.defaultInterpreterPath": interp,
        "python.terminal.activateEnvironment": True,
        "editor.formatOnSave": True,
        "python.formatting.provider": "black",
    }
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run app.py",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/app.py",
                "cwd": "${workspaceFolder}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "envFile": "${workspaceFolder}/.env",
            }
        ],
    }
    with open(launch_path, "w", encoding="utf-8") as f:
        json.dump(launch, f, indent=2)

    workspace = {
        "folders": [{"path": "."}],
        "settings": {"python.defaultInterpreterPath": interp},
    }
    with open(workspace_path, "w", encoding="utf-8") as f:
        json.dump(workspace, f, indent=2)

    print("VS Code files updated: settings.json, launch.json, project.code-workspace")
