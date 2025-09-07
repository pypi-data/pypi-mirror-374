import json
from pathlib import Path
from .core.fs import write_file


def load_or_create_config(root_dir: Path) -> dict:
    """
    Load the ``setup-config.json`` file if it exists, otherwise create it
    with default values. Ensures safe creation using atomic write.

    Args:
        root_dir (Path): The root directory where the config file is located.

    Returns:
        dict: The loaded or newly created configuration.

    Notes:
        - Default configuration values include project name, main file,
          entry point, requirements file, virtual environment directory,
          and Python version.
        - The default main file is set to ``main.py`` instead of ``app.py``.
    """
    print("\n[1] Checking setup-config.json")
    config_path = Path(root_dir) / "setup-config.json"

    default_config = {
        "project_name": Path(root_dir).name,
        "main_file": "main.py",  # Default changed from app.py to main.py
        "entry_point": None,
        "requirements_file": "requirements.txt",
        "venv_dir": ".venv",
        "python_version": "3.12",
    }

    if not config_path.exists():
        state = write_file(
            config_path,
            json.dumps(default_config, indent=2),
            force=True,
            backup=False,
        )
        print(f"[config] {state}: {config_path}")
    else:
        print(f"[config] exists: {config_path}")

    return json.loads(config_path.read_text(encoding="utf-8"))
