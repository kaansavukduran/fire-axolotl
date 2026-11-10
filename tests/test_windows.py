# SPDX-License-Identifier: MPL-2.0
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_source_windows', ROOT / 'scripts/prepare_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WindowsIdentityTests(unittest.TestCase):
    def test_windows_package_rejects_case_collisions_and_unsafe_paths(self):
        import verify_native_package
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'native.zip'
            for names, message in [(['app/A.txt', 'app/a.txt'], 'Duplicate'), (['../outside.exe'], 'Unsafe'), (['app/file:stream'], 'Unsafe')]:
                with zipfile.ZipFile(path, 'w') as archive:
                    for name in names:
                        archive.writestr(name, b'payload')
                with self.assertRaisesRegex(ValueError, message):
                    verify_native_package.verify(path)

    def test_publication_requires_successful_reviewed_native_main_build(self):
        import windows_release
        config = windows_release.CONFIG
        run = {'status': 'completed', 'conclusion': 'success', 'event': 'workflow_dispatch', 'head_branch': 'main', 'head_sha': config.get('validation_commit', config['source_commit']), 'workflow_id': config['native_workflow_id'], 'path': config.get('native_workflow_path', '.github/workflows/native-windows.yml'), 'repository': {'id': config['repository_id']}, 'head_repository': {'id': config['repository_id']}}
        with patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'workflow_dispatch'}):
            with patch.object(windows_release, 'gh', return_value=json.dumps(run)):
                windows_release.preflight()
            with patch.object(windows_release, 'gh', return_value=json.dumps({**run, 'event': 'push'})):
                windows_release.preflight()
            for key, value in [('conclusion', 'failure'), ('event', 'pull_request'), ('head_sha', 'unknown'), ('repository', {'id': 1}), ('head_repository', {'id': 1})]:
                with patch.object(windows_release, 'gh', return_value=json.dumps({**run, key: value})):
                    with self.assertRaises(ValueError):
                        windows_release.preflight()

    def test_installer_has_independent_namespaces_and_cannot_download_firefox(self):
        keys = ['BrandFullNameInternal', 'BrandFullName', 'CompanyName', 'URLInfoAbout', 'HelpLink', 'URLSystemRequirements', 'URLManualDownload', 'URLStubDownloadX86', 'URLStubDownloadAMD64', 'URLStubDownloadAArch64', 'CertNameDownload', 'CertIssuerDownload']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            branding = root / 'branding'
            branding.mkdir()
            (branding / 'branding.nsi').write_text('\n'.join(f'!define {key} "Mozilla Developer Preview"' for key in keys) + '\n')
            defines = root / 'browser/installer/windows/nsis/defines.nsi.in'
            defines.parent.mkdir(parents=True)
            defines.write_text('\n'.join(f'!define {key} "Firefox"' for key in ['AppName', 'DDEApplication', 'AppRegName', 'BrandProductName']) + '\n')
            module.prepare_windows_installer(root, branding)
            module.prepare_windows_installer(root, branding)
            text = (branding / 'branding.nsi').read_text()
            self.assertNotIn('Mozilla Developer Preview', text)
            for key in ['URLStubDownloadX86', 'URLStubDownloadAMD64', 'URLStubDownloadAArch64']:
                self.assertIn(f'!define {key} ""', text)
            self.assertIn('!define AppRegName "FireAxolotl"', defines.read_text())
            self.assertIn('!define DDEApplication "FireAxolotl"', defines.read_text())
            self.assertNotIn('"Firefox"', defines.read_text())
            self.assertEqual((branding / 'firefox64.ico').read_bytes(), (ROOT / 'branding/aion.ico').read_bytes())


if __name__ == '__main__':
    unittest.main()
