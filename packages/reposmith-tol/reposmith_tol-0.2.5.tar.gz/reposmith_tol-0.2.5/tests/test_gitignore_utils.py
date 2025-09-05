
import unittest
import tempfile
from pathlib import Path

from reposmith.gitignore_utils import create_gitignore, PRESETS

class TestGitignoreUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        self.tmp_ctx.cleanup()

    def test_create_gitignore_python_preset(self):
        state = create_gitignore(self.tmp, preset="python", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", gi)
        self.assertIn("*.py[cod]", gi)

    def test_create_gitignore_node_preset(self):
        state = create_gitignore(self.tmp, preset="node", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("node_modules/", gi)
        self.assertIn("yarn-error.log*", gi)

    def test_create_gitignore_django_preset(self):
        state = create_gitignore(self.tmp, preset="django", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("db.sqlite3", gi)
        self.assertIn("staticfiles/", gi)

    def test_existing_gitignore_without_force(self):
        p = self.tmp / ".gitignore"
        p.write_text("OLD", encoding="utf-8")
        state = create_gitignore(self.tmp, preset="python", force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "OLD")
        self.assertFalse((p.with_suffix(p.suffix + ".bak")).exists())

    def test_existing_gitignore_with_force_and_backup(self):
        p = self.tmp / ".gitignore"
        p.write_text("v1", encoding="utf-8")
        state = create_gitignore(self.tmp, preset="python", force=True)
        self.assertEqual(state, "written")
        gi = p.read_text(encoding="utf-8")
        self.assertIn("__pycache__/", gi)
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

if __name__ == "__main__":
    unittest.main(verbosity=2)
