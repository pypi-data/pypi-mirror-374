
import unittest
import tempfile
from pathlib import Path
from datetime import datetime

from reposmith.license_utils import create_license

class TestLicenseUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        self.tmp_ctx.cleanup()

    def test_create_license_new_mit(self):
        create_license(self.tmp, license_type="MIT", author="TamerOnLine", year=2025, force=False)
        p = self.tmp / "LICENSE"
        text = p.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2025 TamerOnLine", text)

    def test_existing_license_without_force(self):
        p = self.tmp / "LICENSE"
        p.write_text("OLD", encoding="utf-8")
        create_license(self.tmp, license_type="MIT", author="X", year=2000, force=False)
        self.assertEqual(p.read_text(encoding="utf-8"), "OLD")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_existing_license_with_force_and_backup(self):
        p = self.tmp / "LICENSE"
        p.write_text("v1", encoding="utf-8")
        create_license(self.tmp, license_type="MIT", author="Alice", year=2030, force=True)
        text = p.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("2030", text)
        self.assertIn("Alice", text)
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

    def test_unsupported_license_raises(self):
        with self.assertRaises(ValueError):
            create_license(self.tmp, license_type="Apache-2.0", author="Bob", year=2024, force=False)

    def test_default_year_uses_current_year(self):
        year_now = datetime.now().year
        create_license(self.tmp, license_type="MIT", author="NowUser", year=None, force=True)
        text = (self.tmp / "LICENSE").read_text(encoding="utf-8")
        self.assertIn(str(year_now), text)
        self.assertIn("NowUser", text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
