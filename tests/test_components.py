# SPDX-License-Identifier: MPL-2.0
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fetch_components', ROOT / 'scripts/fetch_components.py')
components = importlib.util.module_from_spec(spec)
spec.loader.exec_module(components)


class ComponentSafetyTests(unittest.TestCase):
    def test_source_checkout_preserves_pinned_bytes_despite_windows_git_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            components.git(root, 'init', '-q')
            path = root / 'filter.txt'
            body = b'filter source\nlicense line\n'
            path.write_bytes(body)
            components.git(root, 'add', 'filter.txt')
            components.git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
            components.git(root, 'config', 'core.autocrlf', 'true')
            path.unlink()
            components.git(root, 'checkout', '--', 'filter.txt')
            self.assertEqual(path.read_bytes(), body)

    def test_damaged_official_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'component.xpi'
            path.write_bytes(b'not the signed official package')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                components.verify_xpi(path)

    def test_archive_traversal_rejected_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'component.xpi'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('../outside.js', 'unexpected')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                components.verify_xpi(path, {'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

    def test_wrong_component_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'component.xpi'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('manifest.json', json.dumps({'version': '1.0', 'browser_specific_settings': {'gecko': {'id': 'someone-else@example.org'}}}))
            with self.assertRaisesRegex(ValueError, 'identity/version'):
                components.verify_xpi(path, {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'id': 'expected@example.org', 'version': '1.0'})
