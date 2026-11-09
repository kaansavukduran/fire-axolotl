# SPDX-License-Identifier: MPL-2.0
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_source_windows', ROOT / 'scripts/prepare_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WindowsIdentityTests(unittest.TestCase):
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
