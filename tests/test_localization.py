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
    def test_complete_official_catalog_has_unique_pinned_independent_language_identities(self):
        pin = localization.PIN
        self.assertEqual(set(pin['official_locales']), set(pin['locales']) | {'en-US'})
        self.assertEqual(len(pin['official_locales']), 103)
        self.assertEqual(len({r['id'] for r in pin['locales'].values()}), 102)
        for locale, record in pin['locales'].items():
            self.assertEqual(record['original_id'], f'langpack-{locale}@firefox.mozilla.org')
            self.assertEqual(record['id'], f'langpack-{locale}@fire-axolotl.browser')
            self.assertRegex(record['sha512'], r'^[a-f0-9]{128}$')
            self.assertTrue(record['url'].startswith(f'https://archive.mozilla.org/pub/firefox/releases/{pin["upstream"]}/linux-x86_64/xpi/'))

    def test_localized_brand_attributes_and_copyright_comments_are_preserved(self):
        original = '# Mozilla Public License notice\n-brand-short-name = Firefox\n    .gender = masculine\n    .case-status = with-cases\n    .genitive = Firefoxu\ntrademarkInfo.part1=Firefox is a trademark of Mozilla.\n'
        updated = localization.rebrand_resource(original)
        self.assertIn('# Mozilla Public License notice', updated)
        self.assertIn('.gender = masculine', updated)
        self.assertIn('.case-status = with-cases', updated)
        self.assertIn('.genitive = Fire Axolotlu', updated)
        self.assertIn('-brand-short-name = Fire Axolotl', updated)
        self.assertIn('trademarkInfo.part1=Firefox is a trademark of Mozilla.', updated)

    def test_language_package_cannot_add_experimental_executable_apis(self):
        with tempfile.TemporaryDirectory() as directory:
            path, record = self.fixture(directory)
            with zipfile.ZipFile(path) as archive:
                files = {n: archive.read(n) for n in archive.namelist()}
            manifest = json.loads(files['manifest.json'])
            manifest['experiment_apis'] = {'bad': {'schema': 'schema.json'}}
            files['manifest.json'] = json.dumps(manifest).encode()
            with zipfile.ZipFile(path, 'w') as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
            record['sha512'] = hashlib.sha512(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'only localization resources'):
                localization.verify(path, 'tr', record)

    def test_locale_identifier_cannot_escape_a_packaging_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path, record = self.fixture(directory)
            with self.assertRaisesRegex(ValueError, 'identifier'):
                localization.verify(path, '../tr', record)

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
