import sys
import argparse
from pathlib import Path

# Ensure package init for -m runs
pkg_dir = Path(__file__).resolve().parent
init_file = pkg_dir / "__init__.py"
if not init_file.exists():
    init_file.write_text("# Auto-created to mark package\\n", encoding="utf-8")
    print(f"[init] Created {init_file}")

# Flexible imports (module vs script)
try:
    from .config_utils import load_or_create_config
    from .venv_utils import create_virtualenv, upgrade_pip, install_requirements, create_env_info
    from .file_utils import create_requirements_file, create_app_file
    from .vscode_utils import create_vscode_files
    from .ci_utils import ensure_github_actions_workflow
    from .gitignore_utils import create_gitignore
    from .license_utils import create_license
except ImportError:
    from config_utils import load_or_create_config
    from venv_utils import create_virtualenv, upgrade_pip, install_requirements, create_env_info
    from file_utils import create_requirements_file, create_app_file
    from vscode_utils import create_vscode_files
    from ci_utils import ensure_github_actions_workflow
    from gitignore_utils import create_gitignore
    from license_utils import create_license


from pathlib import Path
import os

def resolve_root(args) -> Path:
    if args.root:
        return Path(args.root).resolve()     # <-- الآن يفسر . بالنسبة لـ CWD
    if args.up is not None:
        root = Path(os.getcwd())
        for _ in range(args.up):
            root = root.parent
        return root.resolve()
    return Path(os.getcwd()).resolve()



def main():
    parser = argparse.ArgumentParser(description="Project setup and CI generator (with gitignore/license)")
    parser.add_argument("--ci", choices=["skip", "create", "force"], default="skip")
    parser.add_argument("--ci-python", default="3.12")
    parser.add_argument("--root", help="Target project root (relative to this file or absolute)")
    parser.add_argument("--up", type=int, help="Go up N directories from this file's folder")
    parser.add_argument("--gitignore", default="python", help="Preset for .gitignore (python|node|django)")
    parser.add_argument("--license", dest="license_type", default="MIT", help="License type (MIT|Apache-2.0)")
    parser.add_argument("--author", default="Your Name", help="Author name for LICENSE")
    parser.add_argument("--year", type=int, help="Year for LICENSE header")

    args = parser.parse_args()

    root_dir = resolve_root(args)
    print(f"Target project root: {root_dir}")
    if not root_dir.exists():
        print(f"Creating target directory: {root_dir}")
        root_dir.mkdir(parents=True, exist_ok=True)

    print("\\nStarting project setup...\\n" + "-" * 40)
    config = load_or_create_config(root_dir)

    if args.ci in ("create", "force"):
        status = ensure_github_actions_workflow(root_dir, py=args.ci_python, force=(args.ci == "force"))
        print(f"[ci] {status}: {root_dir / '.github' / 'workflows' / 'test-main.yml'}")

    venv_dir = (root_dir / config["venv_dir"]).as_posix()
    requirements_path = (root_dir / config["requirements_file"]).as_posix()
    main_file = (root_dir / config["main_file"]).as_posix()

    create_virtualenv(venv_dir)
    create_requirements_file(requirements_path)
    upgrade_pip(venv_dir)
    install_requirements(venv_dir, requirements_path)
    create_env_info(venv_dir)
    create_app_file(main_file)
    create_vscode_files(root_dir, venv_dir)

    # New: gitignore + license
    create_gitignore(root_dir, preset=args.gitignore)
    create_license(root_dir, license_type=args.license_type, author=args.author, year=args.year)

    print("\\nProject setup complete.")


if __name__ == "__main__":
    main()