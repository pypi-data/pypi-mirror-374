"""RepoSmith CLI entry point.

This module provides the command-line interface for bootstrapping a new
Python project with optional virtual environment, VS Code settings,
.gitignore, LICENSE, and CI workflow files.
"""

import argparse
from datetime import datetime
from pathlib import Path

from .ci_utils import ensure_github_actions_workflow
from .file_utils import create_app_file, create_requirements_file
from .gitignore_utils import create_gitignore
from .license_utils import create_license
from .venv_utils import (
    create_env_info,
    create_virtualenv,
    install_requirements,
    upgrade_pip,
)
from .vscode_utils import create_vscode_files



def build_parser():
    """Create and configure the top-level argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser for the ``reposmith`` CLI.

    Notes:
        The parser defines a single ``init`` subcommand that bootstraps a new
        project directory with optional components such as a virtual
        environment, VS Code configuration, GitHub Actions workflow, and
        licensing files.
    """

    parser = argparse.ArgumentParser(
        prog="reposmith",
        description=(
            "RepoSmith: Bootstrap Python projects (zero deps)"
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Target project folder",
    )
    sc.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    sc.add_argument(
        "--no-venv",
        action="store_true",
        help="Skip virtualenv creation",
    )
    sc.add_argument(
        "--entry",
        default="main.py",
        help="Entry filename (default: main.py)",
    )
    sc.add_argument(
        "--with-license",
        action="store_true",
        help="Create LICENSE file",
    )
    sc.add_argument(
        "--with-gitignore",
        action="store_true",
        help="Create .gitignore file",
    )
    sc.add_argument(
        "--with-vscode",
        action="store_true",
        help="Create VSCode files",
    )
    sc.add_argument(
        "--with-ci",
        action="store_true",
        help="Create GitHub Actions workflow",
    )
    sc.add_argument(
        "--ci-python",
        default="3.12",
        help="Python version for CI",
    )
    sc.add_argument(
        "--author",
        default="Your Name",
        help="Author for LICENSE",
    )
    sc.add_argument(
        "--year",
        type=int,
        help="Year for LICENSE (defaults to current year)",
    )
    return parser



def main(argv=None):
    """Execute the ``reposmith`` CLI.

    Args:
        argv (list[str] | None): Optional list of command-line arguments.
            If ``None``, arguments are read from ``sys.argv``.

    Returns:
        None

    Notes:
        This function does not alter business logic; it orchestrates the
        configured steps according to the provided CLI flags and options.
    """
    args = build_parser().parse_args(argv)

    if args.cmd == "init":
        root = args.root
        root.mkdir(parents=True, exist_ok=True)
        print(f"Target project root: {root}")

        # Paths
        venv_dir = root / ".venv"
        reqs = root / "requirements.txt"
        main_file = root / args.entry

        # 1) Create requirements.txt first (before installation)
        req_state = create_requirements_file(reqs, force=args.force)
        print(f"[requirements] {req_state}: {reqs}")

        # 2) Virtual environment + install (optional)
        if not args.no_venv:
            venv_state = create_virtualenv(venv_dir)
            print(f"[venv] {venv_state}: {venv_dir}")

            if not args.force:
                pip_state = upgrade_pip(venv_dir)
                print(f"[pip] {pip_state}")

            reqs_state = install_requirements(venv_dir, reqs)
            print(f"[install] {reqs_state}: {reqs}")

            env_state = create_env_info(venv_dir)
            print(f"[env-info] {env_state}")



        # 3) Create the entry file (supports --force with .bak backup)
        entry_state = create_app_file(main_file, force=args.force)
        print(f"[entry] {entry_state}: {main_file}")       

        # 4) Optional extras
        if args.with_vscode:
            create_vscode_files(
                root,
                venv_dir,
                main_file=str(main_file),
                force=args.force,
            )

        if args.with_gitignore:
            create_gitignore(root, preset="python", force=args.force)

        if args.with_license:
            year = args.year or datetime.now().year
            create_license(
                root,
                license_type="MIT",
                author=args.author,
                year=year,
                force=args.force,
            )

        if args.with_ci:
            state = ensure_github_actions_workflow(
                root,
                py=args.ci_python,
                program=args.entry,
                force=args.force,
            )
            print(
                f"[ci] {state}: "
                f"{root / '.github' / 'workflows' / 'ci.yml'}"
            )

        print("Project setup complete.")


if __name__ == "__main__":
    main()

