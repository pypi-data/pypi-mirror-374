import argparse
import os
import subprocess
import sys
from importlib.metadata import version, PackageNotFoundError

def sh(cmd: list[str]) -> int:
    """
    Execute a shell command and print it.

    Args:
        cmd (list[str]): Command and arguments to execute.

    Returns:
        int: The return code from the executed command.
    """
    print("\n$ " + " ".join(cmd))
    return subprocess.call(cmd)

def cmd_init(args: argparse.Namespace) -> int:
    """
    Handle the 'init' command to initialize a project using reposmith.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Return code from the executed initialization command.
    """
    base = [
        sys.executable, "-m", "reposmith", "init",
        "--with-license", "--with-gitignore", "--with-vscode"
    ]

    if args.root:
        base += ["--root", args.root]
    if args.entry:
        base += ["--entry", args.entry]
    if args.author:
        base += ["--author", args.author]
    if args.with_ci:
        base.append("--with-ci")
        if args.ci_python:
            base += ["--ci-python", args.ci_python]
    if args.force:
        base.append("--force")
    if args.no_venv:
        base.append("--no-venv")

    if args.interactive:
        if not args.entry:
            entry = input("Entry filename (Enter = main.py): ").strip()
            if entry:
                base += ["--entry", entry]
        if not args.author:
            author = input("Author (Enter = skip): ").strip()
            if author:
                base += ["--author", author]
        if not args.with_ci and input("Add GitHub CI? (y/n): ").lower() == "y":
            base.append("--with-ci")
            ci_py = input("CI Python (Enter = 3.12): ").strip()
            if ci_py:
                base += ["--ci-python", ci_py]
        if not args.force and input("--force overwrite? (y/n): ").lower() == "y":
            base.append("--force")
        if not args.no_venv and input("--no-venv? (y/n): ").lower() == "y":
            base.append("--no-venv")

    return sh(base)

def cmd_info(_: argparse.Namespace) -> int:
    """
    Handle the 'info' command to show environment and reposmith status.

    Args:
        _ (argparse.Namespace): Unused parsed arguments.

    Returns:
        int: Always returns 0.
    """
    print("CWD:", os.getcwd())
    print("Python:", sys.version.split()[0])
    try:
        print("reposmith-tol:", version("reposmith-tol"))
    except PackageNotFoundError:
        print("reposmith-tol: (not installed) → install via: pip install reposmith-tol")

    code = subprocess.call(
        [sys.executable, "-m", "reposmith", "-h"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("reposmith module:", "OK" if code == 0 else "Not found")
    return 0

def build_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser instance.
    """
    parser = argparse.ArgumentParser(prog="on", description="TamerOnLine helper CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_parser = sub.add_parser("init", help="Initialize a project via reposmith (with sane defaults)")
    init_parser.add_argument("--root", help="Target project folder (default: current)")
    init_parser.add_argument("--entry", help="Entry filename (default: main.py)")
    init_parser.add_argument("--author", help="Author for LICENSE")
    init_parser.add_argument("--with-ci", action="store_true", dest="with_ci", help="Create GitHub Actions workflow")
    init_parser.add_argument("--ci-python", dest="ci_python", help="Python version for CI (e.g. 3.12)")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    init_parser.add_argument("--no-venv", action="store_true", help="Skip virtualenv creation")
    init_parser.add_argument("-i", "--interactive", action="store_true", help="Ask minimal questions to fill missing options")
    init_parser.set_defaults(func=cmd_init)

    info_parser = sub.add_parser("info", help="Show quick env info and reposmith presence")
    info_parser.set_defaults(func=cmd_info)

    return parser

def main(argv=None) -> int:
    """
    Main entry point of the script.

    Args:
        argv (list[str], optional): List of command-line arguments. Defaults to None.

    Returns:
        int: Return code from the selected command.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
