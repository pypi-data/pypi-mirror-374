
import unittest
import tempfile
from pathlib import Path
import sys
import subprocess
import os

class TestCLISmokeWithCI(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory()
        self.root = Path(self.ctx.name) / "proj"
        self.root.mkdir()
        # Point PYTHONPATH to the project root so '-m reposmith.main' uses local code
        self.project_root = Path(__file__).resolve().parents[1]

    def tearDown(self):
        self.ctx.cleanup()

    def _run(self, args):
        env = os.environ.copy()
        # Prepend project_root to PYTHONPATH
        env['PYTHONPATH'] = str(self.project_root) + (os.pathsep + env['PYTHONPATH'] if 'PYTHONPATH' in env else '')
        subprocess.run([sys.executable, "-m", "reposmith.main"] + args, check=True, cwd=self.root, env=env)

    def test_init_with_ci_generates_workflow(self):
        self._run([
            "init",
            "--no-venv",
            "--entry", "run.py",
            "--with-ci",
            "--ci-python", "3.13"
        ])

        wf = self.root / ".github" / "workflows" / "test-main.yml"
        self.assertTrue(wf.exists(), "Workflow file was not created")

        yml = wf.read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v4", yml)
        self.assertIn("actions/setup-python@v5", yml)
        self.assertIn('python-version: "3.13"', yml)
        # New workflow should say Run unit tests (not Run run.py)
        self.assertIn("Run unit tests", yml)

if __name__ == "__main__":
    unittest.main(verbosity=2)
