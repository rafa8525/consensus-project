"""Isolated ACS-03 probe classification patch tests: never touches host runtime."""
import tempfile
import unittest
from pathlib import Path
from agents.acs03_probe_error_patch import PROBE_CODES, UnsafeLayout, apply, patch_source


BASE = """def main():
    try:
        raise RuntimeError("not executed")
    except Exception as exc:
        allowed = {
            "Unsafe source quality": "UNSAFE_SOURCE",
            "Source measurement is stale or in future": "SOURCE_STALE",
        }
        code = allowed.get(str(exc), "UNCLASSIFIED")
        print(code)
        return 2
"""


class ProbePatchTests(unittest.TestCase):
    def test_inserts_all_categories_with_original_behavior(self):
        changed, count = patch_source(BASE)
        self.assertEqual(count, len(PROBE_CODES))
        for key, value in PROBE_CODES.items():
            self.assertIn(repr(key) + ": " + repr(value), changed)
        self.assertIn('"Unsafe source quality": "UNSAFE_SOURCE"', changed)
        self.assertIn('allowed.get(str(exc), "UNCLASSIFIED")', changed)
        self.assertEqual(patch_source(changed), (changed, 0))

    def test_unknown_failure_stays_fail_closed(self):
        changed, _ = patch_source(BASE)
        ns = {}
        exec(changed, ns)
        self.assertEqual(ns["main"](), 2)

    def test_rejects_different_handler(self):
        with self.assertRaises(UnsafeLayout):
            patch_source("def main():\n    return True\n")

    def test_rejects_conflicting_map(self):
        conflicting = BASE.replace(
            '"Unsafe source quality": "UNSAFE_SOURCE",',
            '"No private OAuth token": "SUCCESS",'
        )
        with self.assertRaises(UnsafeLayout):
            patch_source(conflicting)

    def test_apply_creates_backup_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "health_connect_cloud_cycle.py"
            path.write_text(BASE, encoding="utf-8")
            self.assertTrue(apply(path).startswith("PATCHED_"))
            backup = path.with_name(path.name + ".pre_acs03_probe_codes")
            self.assertEqual(backup.read_text(encoding="utf-8"), BASE)
            self.assertEqual(apply(path), "ALREADY_PATCHED")
            self.assertNotEqual(path.read_text(encoding="utf-8"), BASE)

    def test_symlink_not_modified(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "target.py"
            target.write_text(BASE)
            link = Path(folder) / "health_connect_cloud_cycle.py"
            link.symlink_to(target)
            with self.assertRaises(UnsafeLayout):
                apply(link)
            self.assertEqual(target.read_text(), BASE)


if __name__ == "__main__":
    unittest.main()
