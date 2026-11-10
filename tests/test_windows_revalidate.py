# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy
import unittest
from windows_revalidate import validate_build, BUILD_COMMIT, REPO_ID


class PreservedBuildTests(unittest.TestCase):
    def fixture(self):
        run = {'status': 'completed', 'conclusion': 'failure', 'event': 'push', 'head_sha': BUILD_COMMIT, 'head_branch': 'main', 'workflow_id': 412586894, 'path': '.github/workflows/native-windows.yml', 'repository': {'id': REPO_ID}, 'head_repository': {'id': REPO_ID}}
        names = ['Compile the actual Windows Firefox fork', 'Package the compiled Windows payload', 'Verify the actual offline NSIS installer was packaged', 'Preserve corresponding applied Windows source']
        jobs = {'jobs': [{'steps': [{'name': n, 'conclusion': 'success'} for n in names]}]}
        return run, jobs

    def test_revalidation_requires_the_exact_completed_compilation_and_source(self):
        run, jobs = self.fixture()
        validate_build(run, jobs)
        for key, value in [('event', 'pull_request'), ('head_sha', 'other'), ('repository', {'id': 1}), ('head_repository', {'id': 1}), ('workflow_id', 1), ('status', 'in_progress')]:
            with self.assertRaises(ValueError):
                validate_build({**run, key: value}, jobs)
        for index in range(4):
            altered = deepcopy(jobs)
            altered['jobs'][0]['steps'][index]['conclusion'] = 'failure'
            with self.assertRaises(ValueError):
                validate_build(run, altered)
