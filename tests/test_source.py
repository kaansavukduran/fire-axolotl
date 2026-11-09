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


if __name__ == '__main__':
    unittest.main()
