import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from manage_patch import apply, MARKER, SHA, VERSION, WHEEL


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "config"
        self.root.mkdir()
        (self.root / "configuration.yaml").touch()
        self.payload = base / "payload"
        src = self.payload / "custom_components/tplink"
        lib = self.payload / "techcave_tpap/lib"
        src.mkdir(parents=True)
        lib.mkdir(parents=True)
        (src / MARKER).write_text(json.dumps({
            "home_assistant_core": VERSION, "python_kasa_commit": SHA, "python_kasa_wheel": WHEEL}))
        (src / "manifest.json").write_text(json.dumps({
            "requirements": ["python-kasa[speedups] @ file:///config/techcave_tpap/lib/" + WHEEL]}))
        (lib / WHEEL).write_bytes(b"fixture, not a real wheel")
        (lib.parent / "WHEEL_SHA256.txt").write_text(hashlib.sha256((lib / WHEEL).read_bytes()).hexdigest())
        self.target = self.root / "custom_components/tplink"

    def test_install_and_rollback(self):
        apply("install", self.root, self.payload, VERSION, True)
        self.assertTrue(self.target.is_dir())
        self.assertTrue((self.root / "techcave_tpap/lib" / WHEEL).is_file())
        apply("rollback", self.root, self.payload, confirmed=True)
        self.assertFalse(self.target.exists())
        self.assertTrue(list((self.root / "techcave_tpap").glob("disabled_override_*")))

    def test_version_and_confirmation(self):
        for version, confirmed in [("2026.11.0", True), (VERSION, False)]:
            with self.assertRaises(RuntimeError):
                apply("install", self.root, self.payload, version, confirmed)
            self.assertFalse(self.target.exists())

    def test_existing_override(self):
        self.target.mkdir(parents=True)
        with self.assertRaises(RuntimeError):
            apply("install", self.root, self.payload, VERSION, True)
        with self.assertRaises(RuntimeError):
            apply("rollback", self.root, self.payload, confirmed=True)
        self.assertTrue(self.target.is_dir())

    def test_corrupt_wheel(self):
        (self.payload / "techcave_tpap/lib" / WHEEL).write_bytes(b"tampered")
        with self.assertRaises(RuntimeError):
            apply("install", self.root, self.payload, VERSION, True)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
