# SPDX-License-Identifier: MPL-2.0
import contextlib
import io
import json
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]


class UpstreamReviewTests(unittest.TestCase):
    def setUp(self):
        self.engine = json.loads((ROOT / 'upstream.json').read_text())
        self.component = json.loads((ROOT / 'components.json').read_text())['ublock-origin']
        self.versions = {'FIREFOX_ESR': self.engine['version']}
        self.release = {'tag_name': self.component['version'], 'assets': [{'browser_download_url': self.component['url'], 'digest': 'sha256:' + self.component['sha256']}]}

    def check(self):
        def response(request, **kwargs):
            url = request if isinstance(request, str) else request.full_url
            data = self.versions if url.startswith('https://product-details.mozilla.org/') else self.release
            return io.BytesIO(json.dumps(data).encode())
        with patch('urllib.request.urlopen', side_effect=response), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(ROOT / 'scripts/check_upstream.py'), run_name='__main__')

    def test_current_engine_and_official_component_digest_pass(self):
        self.check()

    def test_new_esr_blocks_release_even_if_component_is_current(self):
        self.versions['FIREFOX_ESR'] = '999.0.0esr'
        with self.assertRaisesRegex(SystemExit, 'security review required'):
            self.check()

    def test_new_component_requires_review(self):
        self.release['tag_name'] = '999.0'
        with self.assertRaisesRegex(SystemExit, 'uBlock Origin review required'):
            self.check()

    def test_changed_official_asset_digest_is_rejected(self):
        self.release['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaisesRegex(SystemExit, 'digest changed'):
            self.check()

    def test_missing_official_asset_is_rejected(self):
        self.release['assets'] = []
        with self.assertRaisesRegex(SystemExit, 'unavailable'):
            self.check()

    def test_unreachable_authority_does_not_mean_up_to_date(self):
        with patch('urllib.request.urlopen', side_effect=URLError('offline')):
            with self.assertRaises(URLError):
                runpy.run_path(str(ROOT / 'scripts/check_upstream.py'), run_name='__main__')
