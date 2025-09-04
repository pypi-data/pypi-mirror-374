import os
import argparse
from pathlib import Path
from datetime import datetime

# Ensure package init for -m runs
pkg_dir = Path(__file__).resolve().parent
init_file = pkg_dir / "__init__.py"
if not init_file.exists():
    init_file.write_text("# Auto-created to mark package\n", encoding="utf-8")
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


def resolve_root(args: argparse.Namespace) -> Path:
    """
    Resolve the target project root.
    --root: absolute OR relative to this file's folder.
    --up: go up N directories from this file's folder.
    default: current working directory.
    """
    if args.root:
        r = Path(args.root)
        return (r if r.is_absolute() else (pkg_dir / r)).resolve()

    if args.up is not None:
        root = pkg_dir
        for _ in range(max(0, args.up)):
            root = root.parent
        return root.resolve()

    return Path(os.getcwd()).resolve()


def main():
    parser = argparse.ArgumentParser(description="Project setup and CI generator (with gitignore/license)")
    parser.add_argument("--ci", choices=["skip", "create", "force"], default="skip")
    parser.add_argument("--ci-python", default="3.12")
    parser.add_argument("--root", help="Target project root (absolute or relative to THIS file)")
    parser.add_argument("--up", type=int, help="Go up N directories from THIS file's folder")
    parser.add_argument("--gitignore", default="python", help="Preset for .gitignore (python|node|django)")

    parser.add_argument(
        "--license",
        dest="license_type",
        choices=["MIT"],
        default="MIT",
        help="License type (MIT only)",
    )

    parser.add_argument("--no-pip-upgrade", action="store_true",
                        help="Skip upgrading pip inside the virtual environment")

    parser.add_argument("--author", default="Your Name", help="Author name for LICENSE")
    parser.add_argument("--year", type=int, help="Year for LICENSE header (defaults to current year)")

    args = parser.parse_args()

    root_dir = resolve_root(args)
    print(f"Target project root: {root_dir}")
    if not root_dir.exists():
        print(f"Creating target directory: {root_dir}")
        root_dir.mkdir(parents=True, exist_ok=True)

    print("\nStarting project setup...\n" + "-" * 40)

    # NOTE: make sure load_or_create_config accepts a root path (Path)
    config = load_or_create_config(root_dir)

    # CI setup (optional)
    if args.ci in ("create", "force"):
        entry_point = config.get("entry_point")
        main_file_name = config.get("main_file", "app.py")

        program_to_run = entry_point or main_file_name  # file name, not absolute path
        picked = "entry_point" if entry_point else "main_file"
        print(f"[ci] Using {picked}: {program_to_run}")

        if entry_point and not (root_dir / entry_point).exists():
            print(f"[ci] Warning: entry_point '{entry_point}' not found on disk; falling back to '{main_file_name}'.")
            program_to_run = main_file_name

        status = ensure_github_actions_workflow(
            root_dir,
            py=args.ci_python,
            program=program_to_run,
            force=(args.ci == "force"),
        )
        print(f"[ci] {status}: {root_dir / '.github' / 'workflows' / 'test-main.yml'}")

    # Paths (keep as Path; convert to str only inside functions if needed)
    venv_dir = root_dir / config["venv_dir"]
    requirements_path = root_dir / config["requirements_file"]
    main_file_path = root_dir / config["main_file"]

    # 1) venv + requirements
    create_virtualenv(venv_dir)
    create_requirements_file(requirements_path)

    # 2) pip upgrade (unless skipped)
    if not args.no_pip_upgrade:
        upgrade_pip(venv_dir)
    else:
        print("[5] Skipping pip upgrade (per --no-pip-upgrade)")

    # 3) install deps + env info
    install_requirements(venv_dir, requirements_path)
    create_env_info(venv_dir)

    # 4) app + vscode
    create_app_file(main_file_path)
    create_vscode_files(root_dir, venv_dir, main_file=str(main_file_path))

    # 5) gitignore + license
    year = args.year if args.year else datetime.now().year
    create_gitignore(root_dir, preset=args.gitignore)
    create_license(root_dir, license_type=args.license_type, author=args.author, year=year)

    print(
        "\nSummary:\n"
        f"- venv: {venv_dir}\n"
        f"- requirements: {requirements_path}\n"
        f"- main: {main_file_path}\n"
        f"- gitignore preset: {args.gitignore}\n"
        f"- license: {args.license_type} ({year})"
    )

    print("\nProject setup complete.")


if __name__ == "__main__":
    main()
