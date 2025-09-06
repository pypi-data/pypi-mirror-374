import unittest
import tempfile
from pathlib import Path
import sys
import subprocess
import os

class TestCLISmoke(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory()
        self.root = Path(self.ctx.name) / "proj"
        self.root.mkdir()
        # Ensure subprocess uses local project code (not site-packages)
        self.project_root = Path(__file__).resolve().parents[1]

    def tearDown(self):
        self.ctx.cleanup()

    def _run(self, args):
        env = os.environ.copy()
        # Prepend project root so '-m reposmith.main' imports local package
        env['PYTHONPATH'] = str(self.project_root) + (os.pathsep + env['PYTHONPATH'] if 'PYTHONPATH' in env else '')
        subprocess.run([sys.executable, "-m", "reposmith.main"] + args, check=True, cwd=self.root, env=env)

    def test_init_basic_without_venv(self):
        self._run([
            "init", "--no-venv", "--entry", "run.py",
            "--with-gitignore", "--with-license", "--with-vscode",
            "--author", "TestUser", "--year", "2099"
        ])
        # files exist
        for rel in [
            "requirements.txt",
            "run.py",
            ".gitignore",
            "LICENSE",
            ".vscode/settings.json",
            ".vscode/launch.json",
            "project.code-workspace"
        ]:
            self.assertTrue((self.root / rel).exists(), f"missing {rel}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
