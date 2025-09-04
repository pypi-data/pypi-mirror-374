import json
from pathlib import Path

def load_or_create_config(root_dir: Path):
    print("\n[1] Setting up setup-config.json")
    config_path = Path(root_dir) / "setup-config.json"
    if not config_path.exists():
        print("Creating config file...")
        default_config = {
            "project_name": Path(root_dir).name,
            "main_file": "app.py",
            "entry_point": "main.py",
            "requirements_file": "requirements.txt",
            "venv_dir": ".venv",
            "python_version": "3.12",
        }
        config_path.write_text(json.dumps(default_config, indent=2), encoding="utf-8")
        print("setup-config.json created.")
    else:
        print("Config file already exists.")
    return json.loads(config_path.read_text(encoding="utf-8"))
