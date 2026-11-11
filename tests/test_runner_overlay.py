# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from runner_overlay import apply, PREFIX


class RunnerOverlayTests(unittest.TestCase):
    def test_ui_repack_preserves_unrelated_resources_and_rejects_other_products(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = Path(folder)
            (runtime / 'browser').mkdir()
            identity = runtime / 'application.ini'
            identity.write_text('[App]\nID={75450dd9-387d-4289-8b23-7ad6609fa530}\nName=FireAxolotl\n')
            archive = runtime / 'browser/omni.ja'
            original = b'\x00untouched original native resource\xff'
            with zipfile.ZipFile(archive, 'w') as output:
                output.writestr('unrelated/native.dat', original)
                output.writestr(PREFIX + 'built_in_addons.json', '{"builtins":[{"addon_id":"aion@fire-axolotl.browser","addon_version":"0.1.0","res_url":"resource://builtin-addons/aion/"}]}')
                output.writestr('defaults/preferences/firefox-branding.js', (Path(__file__).resolve().parents[1] / 'browser/preferences/fire-axolotl.js').read_bytes())
                output.writestr(PREFIX + 'aion-chrome.js', 'old UI')
                output.writestr(PREFIX + 'preferences/preferences.xhtml', '<window><!-- Fire Axolotl preferences begin --><old/><!-- Fire Axolotl preferences end --></window>')
            with patch('runner_overlay.overlay_resources', return_value=({}, [])), patch('runner_overlay.bundled_game.files', return_value={}):
                report = apply(runtime)
            with zipfile.ZipFile(archive) as output:
                self.assertEqual(output.read('unrelated/native.dat'), original)
                self.assertIn(b'aion-newtab-game', output.read(PREFIX + 'preferences/preferences.xhtml'))
                self.assertIn(PREFIX + 'aion-runner/aion-runner.png', output.namelist())
            self.assertEqual(report['unchanged_member_count'], 2)
            self.assertNotEqual(report['original_browser_omni_sha256'], report['browser_omni_sha256'])
            with patch('runner_overlay.overlay_resources', return_value=({}, [])), patch('runner_overlay.bundled_game.files', return_value={}):
                second = apply(runtime)
            self.assertEqual(second['changed'], {})
            self.assertEqual(second['original_browser_omni_sha256'], second['browser_omni_sha256'])
            identity.write_text('[App]\nID=other-browser\nName=Other\n')
            with self.assertRaisesRegex(ValueError, 'Fire Axolotl'):
                apply(runtime)
