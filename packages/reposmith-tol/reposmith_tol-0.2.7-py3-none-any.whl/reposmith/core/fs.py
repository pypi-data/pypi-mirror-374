# reposmith/core/fs.py
from pathlib import Path
import tempfile, shutil

def ensure_dir(path: Path):
    """Ensure parent directories exist for a target file path."""
    path.parent.mkdir(parents=True, exist_ok=True)

def atomic_write(path: Path, data: str, encoding="utf-8"):
    """Write to a temp file then atomically replace the target."""
    ensure_dir(path)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding=encoding, dir=str(path.parent)) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    # Atomic replace on the same filesystem
    tmp_path.replace(path)

def write_file(path: Path, data: str, *, force=False, backup=True) -> str:
    """
    Safe write:
      - If file exists and force=False -> return "exists" without writing.
      - If file exists and backup=True -> create .bak before replacing.
      - Always write atomically.
    """
    if path.exists() and not force:
        return "exists"
    if backup and path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    atomic_write(path, data)
    return "written"
