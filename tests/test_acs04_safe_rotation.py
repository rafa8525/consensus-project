"""ACS-04 automatic rotation must never alter Git-tracked log evidence."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "agents/infrastructure_guardian.py"

class SafeRotationTests(unittest.TestCase):
    def test_python_syntax(self):
        ast.parse(SOURCE.read_text(encoding="utf-8"))

    def test_rotation_requires_git_tracking_check(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "InfrastructureGuardian")
        method = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "check_logs")
        body = ast.get_source_segment(SOURCE.read_text(encoding="utf-8"), method)
        self.assertIn('"ls-files", "--error-unmatch"', body)
        self.assertIn('"tracked_log_requires_review"', body)
        self.assertIn("if probe.returncode == 0:", body)
        self.assertLess(body.index('"ls-files", "--error-unmatch"'), body.index("self.rotate_file(path)"))

if __name__ == "__main__":
    unittest.main()
