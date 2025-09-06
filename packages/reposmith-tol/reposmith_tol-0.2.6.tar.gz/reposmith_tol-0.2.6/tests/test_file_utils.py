
import unittest
import tempfile
from pathlib import Path

from reposmith.file_utils import create_requirements_file, create_app_file

DEFAULT_REQ_PREFIX = "# Add your dependencies here"

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        self.tmp_ctx.cleanup()

    # -------- requirements.txt --------
    def test_create_requirements_new(self):
        p = self.tmp / "requirements.txt"
        state = create_requirements_file(p, force=False)
        self.assertEqual(state, "written")
        content = p.read_text(encoding="utf-8")
        self.assertTrue(content.startswith(DEFAULT_REQ_PREFIX))

    def test_create_requirements_exists_without_force(self):
        p = self.tmp / "requirements.txt"
        p.write_text("old", encoding="utf-8")
        state = create_requirements_file(p, force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "old")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_create_requirements_with_force_and_backup(self):
        p = self.tmp / "requirements.txt"
        p.write_text("v1", encoding="utf-8")
        state = create_requirements_file(p, force=True)
        self.assertEqual(state, "written")
        content = p.read_text(encoding="utf-8")
        self.assertTrue(content.startswith(DEFAULT_REQ_PREFIX))
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

    # -------- app file (main.py / run.py) --------
    def test_create_app_file_new_with_default_content(self):
        p = self.tmp / "main.py"
        state = create_app_file(p, force=False)
        self.assertEqual(state, "written")
        text = p.read_text(encoding="utf-8")
        # Basic sanity checks for the default content
        self.assertIn("Welcome! This is your entry file.", text)
        self.assertIn("You can now start writing your application code here.", text)

    def test_create_app_file_with_custom_content(self):
        p = self.tmp / "run.py"
        custom = "print('مرحبا — Berlin 2025')\n"
        state = create_app_file(p, force=False, content=custom)
        self.assertEqual(state, "written")
        self.assertEqual(p.read_text(encoding="utf-8"), custom)

    def test_create_app_file_existing_without_force(self):
        p = self.tmp / "app.py"
        p.write_text("old = 1\n", encoding="utf-8")
        state = create_app_file(p, force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "old = 1\n")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_create_app_file_force_with_backup(self):
        p = self.tmp / "app.py"
        p.write_text("v1\n", encoding="utf-8")
        state = create_app_file(p, force=True, content="v2\n")
        self.assertEqual(state, "written")
        self.assertEqual(p.read_text(encoding="utf-8"), "v2\n")
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1\n")

if __name__ == "__main__":
    unittest.main(verbosity=2)
