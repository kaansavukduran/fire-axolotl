# SPDX-License-Identifier: MPL-2.0
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('release_validation', ROOT / 'scripts/release_validation.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseProvenanceTests(unittest.TestCase):
    def test_foreign_failed_or_unreviewed_runs_cannot_supply_release_binaries(self):
        config = release.CONFIG
        good = {'status': 'completed', 'conclusion': 'success', 'head_sha': config['source_commit'], 'head_branch': 'main', 'head_repository': {'id': config['repository_id'], 'full_name': config['repository']}, 'workflow_id': config['native_workflow_id'], 'path': '.github/workflows/native-linux.yml', 'event': 'workflow_dispatch'}
        release.validate_run(good)
        for change in [{'conclusion': 'failure'}, {'head_sha': '0' * 40}, {'head_branch': 'untrusted'}, {'head_repository': {'id': 1, 'full_name': 'other/repo'}}, {'event': 'pull_request'}, {'workflow_id': 1}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                run = copy.deepcopy(good)
                run.update(change)
                release.validate_run(run)


if __name__ == '__main__':
    unittest.main()
