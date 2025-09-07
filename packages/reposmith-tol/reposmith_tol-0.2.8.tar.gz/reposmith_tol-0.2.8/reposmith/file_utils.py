# reposmith/file_utils.py
from __future__ import annotations
from pathlib import Path
from .core.fs import write_file

DEFAULT_REQUIREMENTS = "# Add your dependencies here\n"
DEFAULT_APP_CONTENT = (
    'print("Welcome! This is your entry file.")\n'
    'print("You can now start writing your application code here.")\n'
)


def create_requirements_file(path: Path, *, force: bool = False) -> str:
    """
    Create a `requirements.txt` file safely.

    This function writes a `requirements.txt` file at the specified path
    with default placeholder content. It will not overwrite an existing
    file unless `force=True` is specified. If overwriting occurs, a
    backup (`.bak`) file is created automatically.

    Args:
        path (Path): The path to the `requirements.txt` file to be created.
        force (bool, optional): If True, overwrite the file if it already
            exists. Defaults to False.

    Returns:
        str: A status string returned by `write_file`, indicating the
        outcome of the operation.

    Notes:
        - Requires `write_file` to be defined in `.core.fs`.
    """
    return write_file(path, DEFAULT_REQUIREMENTS, force=force, backup=True)


def create_app_file(
    path: Path, *, force: bool = False, content: str | None = None
) -> str:
    """
    Create an application entry file safely (e.g., `main.py` or `run.py`).

    This function writes an entry-point Python file at the specified path
    with either custom content or a default welcome message. It will not
    overwrite an existing file unless `force=True` is specified. If
    overwriting occurs, a backup (`.bak`) file is created automatically.

    Args:
        path (Path): The path to the application entry file to be created.
        force (bool, optional): If True, overwrite the file if it already
            exists. Defaults to False.
        content (str | None, optional): The file content to write. If None,
            a default message is used. Defaults to None.

    Returns:
        str: A status string returned by `write_file`, indicating the
        outcome of the operation.

    Notes:
        - Requires `write_file` to be defined in `.core.fs`.
    """
    body = content if content is not None else DEFAULT_APP_CONTENT
    return write_file(path, body, force=force, backup=True)
