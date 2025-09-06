# tests/test_fs.py
import unittest
import tempfile
from pathlib import Path
from reposmith.core.fs import ensure_dir, atomic_write, write_file

class TestFS(unittest.TestCase):
    def setUp(self):
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        self.tmp_ctx.cleanup()

    def test_ensure_dir_creates_parents(self):
        target = self.tmp / "a" / "b" / "c.txt"
        ensure_dir(target)
        self.assertTrue((self.tmp / "a" / "b").exists())

    def test_atomic_write_produces_file_with_content(self):
        p = self.tmp / "a.txt"
        atomic_write(p, "Hello\nWorld\n")
        self.assertTrue(p.exists())
        self.assertEqual(p.read_text(encoding="utf-8"), "Hello\nWorld\n")

    def test_write_file_new(self):
        p = self.tmp / "new.txt"
        self.assertEqual(write_file(p, "data"), "written")
        self.assertEqual(p.read_text(encoding="utf-8"), "data")

    def test_write_file_existing_without_force(self):
        p = self.tmp / "keep.txt"
        p.write_text("old", encoding="utf-8")
        self.assertEqual(write_file(p, "new", force=False), "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "old")
        self.assertFalse((p.with_suffix(p.suffix + ".bak")).exists())

    def test_write_file_with_force_and_backup(self):
        p = self.tmp / "override.txt"
        p.write_text("v1", encoding="utf-8")
        self.assertEqual(write_file(p, "v2", force=True, backup=True), "written")
        self.assertEqual(p.read_text(encoding="utf-8"), "v2")
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

    def test_write_file_force_without_backup(self):
        p = self.tmp / "nobak.txt"
        p.write_text("old", encoding="utf-8")
        self.assertEqual(write_file(p, "new", force=True, backup=False), "written")
        self.assertEqual(p.read_text(encoding="utf-8"), "new")
        self.assertFalse((p.with_suffix(p.suffix + ".bak")).exists())

    def test_utf8_non_ascii(self):
        p = self.tmp / "utf8.txt"
        text = "Hello — Berlin 2025"
        self.assertEqual(write_file(p, text), "written")
        self.assertEqual(p.read_text(encoding="utf-8"), text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
