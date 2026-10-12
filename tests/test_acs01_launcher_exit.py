"""Run the real ACS-01 launcher with fake git and Python commands."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "agents/run_acs01_supervisor.sh"


class LauncherExitTests(unittest.TestCase):
    def run_case(self, fetch=0, sync=0, supervisor=0):
        with tempfile.TemporaryDirectory() as root:
            d = Path(root)
            (d / "consensus-project").mkdir()
            bin_dir = d / "bin"
            bin_dir.mkdir()
            git = bin_dir / "git"
            git.write_text("""#!/usr/bin/env bash
if [[ "$1" == "fetch" ]]; then exit "${MOCK_FETCH_RC}"; fi
if [[ "$1" == "show" ]]; then
  echo '# mocked sync payload'
  exit "${MOCK_SHOW_RC:-0}"
fi
exit 0
""")
            git.chmod(0o755)
            py = bin_dir / "python3"
            py.write_text("""#!/usr/bin/env bash
if [[ "$1" == "-m" ]]; then exit "${MOCK_SUPERVISOR_RC}"; fi
exit "${MOCK_SYNC_RC}"
""")
            py.chmod(0o755)
            env = dict(os.environ, HOME=str(d),
                       CONSENSUS_REPO_ROOT=str(d / "consensus-project"),
                       PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
                       MOCK_FETCH_RC=str(fetch), MOCK_SYNC_RC=str(sync),
                       MOCK_SUPERVISOR_RC=str(supervisor))
            result = subprocess.run(["bash", str(SCRIPT)],
                                    env=env, capture_output=True, text=True, timeout=15)
            return result

    def test_both_healthy(self):
        result = self.run_case()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_failed_sync_not_masked(self):
        result = self.run_case(sync=2)
        self.assertEqual(result.returncode, 2)
        self.assertIn("supervisor rc=0", result.stdout)

    def test_failed_fetch_not_masked(self):
        result = self.run_case(fetch=1)
        self.assertEqual(result.returncode, 3)
        self.assertIn("supervisor rc=0", result.stdout)

    def test_failed_supervisor_propagates(self):
        result = self.run_case(supervisor=1)
        self.assertEqual(result.returncode, 1)

    def test_both_failed_reports_sync(self):
        result = self.run_case(sync=2, supervisor=1)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
