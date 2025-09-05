# reposmith/venv_utils.py
import os
import sys
import subprocess

def _venv_python(venv_dir: str) -> str:
    return (
        os.path.join(venv_dir, "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(venv_dir, "bin", "python")
    )

def create_virtualenv(venv_dir, python_version=None) -> str:
    print("\n[2] Checking virtual environment")
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment at: {venv_dir}")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Virtual environment created.")
        return "written"
    else:
        print("Virtual environment already exists.")
        return "exists"

def install_requirements(venv_dir, requirements_path) -> str:
    print("\n[4] Installing requirements")
    py = _venv_python(venv_dir)

    if os.path.exists(requirements_path) and os.path.getsize(requirements_path) > 0:
        subprocess.run(
            [py, "-m", "pip", "install", "-r", requirements_path, "--upgrade-strategy", "only-if-needed"],
            check=True,
        )
        print("Packages installed.")
        return "written"
    else:
        print("requirements.txt is empty or missing, skipping install.")
        return "skipped"

def upgrade_pip(venv_dir) -> str:
    print("\n[5] Upgrading pip")
    py = _venv_python(venv_dir)
    subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    print("pip upgraded.")
    return "written"

def create_env_info(venv_dir) -> str:
    print("\n[6] Creating env-info.txt")
    info_path = os.path.join(os.path.abspath(os.path.join(venv_dir, os.pardir)), "env-info.txt")
    py = _venv_python(venv_dir)
    with open(info_path, "w", encoding="utf-8") as f:
        subprocess.run([py, "--version"], stdout=f)
        f.write("\nInstalled packages:\n")
        subprocess.run([py, "-m", "pip", "freeze"], stdout=f)
    print(f"Environment info saved to {info_path}")
    return "written"
