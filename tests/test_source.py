# SPDX-License-Identifier: MPL-2.0
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'scripts/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceSafetyTests(unittest.TestCase):
    def test_independent_app_identity_keeps_desktop_startup_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'BrowserComponents.manifest'
            path.write_text('#   browser:        {ec8030f7-c20a-464f-9b0e-13a3a9e97384}\ncategory app-startup nsBrowserGlue @mozilla.org/browser/browserglue;1 application={ec8030f7-c20a-464f-9b0e-13a3a9e97384} application={aa3c5121-dab2-40e2-81ca-7ea25febc110}\n')
            patch = load('prepare_source').replace_app_startup_identity
            patch(path); patch(path)
            registration = path.read_text().splitlines()[1]
            self.assertIn('application={75450dd9-387d-4289-8b23-7ad6609fa530}', registration)
            self.assertIn('application={aa3c5121-dab2-40e2-81ca-7ea25febc110}', registration)
            self.assertNotIn('application={ec8030f7-', registration)

    def test_corrupted_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.tar.xz'
            path.write_bytes(b'corrupted source')
            with self.assertRaises(ValueError):
                load('fetch_source').verify(path, '0' * 128)

    def test_upstream_anchor_mismatch_does_not_modify_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'confvars.sh'
            path.write_text('changed upstream')
            with self.assertRaises(ValueError):
                load('prepare_source').replace_once(path, 'old anchor', 'new content')
            self.assertEqual(path.read_text(), 'changed upstream')

    def test_addon_package_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            build = load('package_extension').package
            first = build(Path(directory) / 'a.xpi')
            second = build(Path(directory) / 'b.xpi')
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(), hashlib.sha256(second.read_bytes()).digest())

    def test_preferences_upgrade_replaces_existing_controls_without_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.inc.xhtml'
            path.write_text('<groupbox id="aionLayoutGroup"><label>old</label></groupbox>\n<!-- Browser layout -->')
            prepare = load('prepare_source').replace_preferences_block
            prepare(path, '<groupbox id="aionLayoutGroup"><label>new</label></groupbox>')
            prepare(path, '<groupbox id="aionLayoutGroup"><label>updated</label></groupbox>')
            text = path.read_text()
            self.assertEqual(text.count('id="aionLayoutGroup"'), 1)
            self.assertIn('updated', text)
            self.assertNotIn('>new<', text)

    def test_legacy_preferences_move_outside_inert_general_template(self):
        with tempfile.TemporaryDirectory() as directory:
            source = load('prepare_source')
            legacy = Path(directory) / 'main.inc.xhtml'
            legacy.write_text('<html:template id="template-paneGeneral">\n<!-- Fire Axolotl preferences begin -->\n<groupbox id="aionLayoutGroup"/>\n<!-- Fire Axolotl preferences end -->\n<!-- Browser layout -->\n</html:template>')
            source.remove_legacy_preferences(legacy)
            target = Path(directory) / 'preferences.xhtml'
            target.write_text('<vbox id="mainPrefPane">\n#include main.inc.xhtml\n</vbox>')
            source.replace_preferences_block(target, '<groupbox id="aionLayoutGroup"/>', '#include main.inc.xhtml')
            self.assertNotIn('aionLayoutGroup', legacy.read_text())
            self.assertEqual(target.read_text().count('aionLayoutGroup'), 1)


if __name__ == '__main__':
    unittest.main()
