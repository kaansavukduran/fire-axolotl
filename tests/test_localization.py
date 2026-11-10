# SPDX-License-Identifier: MPL-2.0
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('localization', ROOT / 'scripts/localization.py')
localization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(localization)


class LocalizationTests(unittest.TestCase):
    def fixture(self, directory, extra=None):
        path = Path(directory) / 'tr.xpi'
        record = dict(localization.PIN['locales']['tr'])
        manifest = {'langpack_id': 'tr', 'languages': {'tr': {}}, 'version': record['version'], 'author': 'Original translation contributors', 'browser_specific_settings': {'gecko': {'id': record['original_id']}}}
        files = {'manifest.json': json.dumps(manifest), 'META-INF/mozilla.rsa': 'signature fixture', 'META-INF/cose.sig': 'signature fixture', 'browser/localization/tr/branding/brand.ftl': '-brand-short-name = Firefox', 'browser/chrome/tr/locale/branding/brand.properties': 'brandShortName=Firefox', 'browser/localization/tr/browser/browser.ftl': 'test-message = Merhaba Türkçe'}
        files.update(extra or {})
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        record['sha512'] = hashlib.sha512(path.read_bytes()).hexdigest()
        return path, record

    def test_language_hash_and_archive_paths_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            path, record = self.fixture(directory, {'../escaped': 'unsafe'})
            with self.assertRaises(ValueError):
                localization.verify(path, 'tr', record)
            path, record = self.fixture(directory)
            path.write_bytes(path.read_bytes() + b'changed')
            with self.assertRaises(ValueError):
                localization.verify(path, 'tr', record)

    def test_derivative_keeps_translations_and_attribution_without_claiming_original_signatures(self):
        with tempfile.TemporaryDirectory() as directory:
            path, record = self.fixture(directory)
            brand = Path(directory) / 'branding'
            brand.mkdir()
            (brand / 'brand.ftl').write_text('-brand-short-name = Fire Axolotl\n')
            (brand / 'brand.properties').write_text('brandShortName=Fire Axolotl\n')
            out = Path(directory) / 'addon'
            receipt = localization.build_addon(path, out, 'tr', record, brand)
            manifest = json.loads((out / 'manifest.json').read_text())
            self.assertEqual(manifest['author'], 'Original translation contributors')
            self.assertEqual(manifest['browser_specific_settings']['gecko']['id'], record['id'])
            self.assertFalse((out / 'META-INF').exists())
            self.assertNotIn('default_locale', manifest)
            self.assertNotIn('__MSG_', manifest['name'])
            self.assertEqual((out / 'browser/localization/tr/browser/browser.ftl').read_text(), 'test-message = Merhaba Türkçe')
            self.assertIn('Fire Axolotl', (out / 'browser/localization/tr/branding/brand.ftl').read_text())
            self.assertEqual(set(receipt['modified_files']), {'manifest.json', 'browser/localization/tr/branding/brand.ftl', 'browser/chrome/tr/locale/branding/brand.properties'})


if __name__ == '__main__':
    unittest.main()
