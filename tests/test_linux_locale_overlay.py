# SPDX-License-Identifier: MPL-2.0
import io
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runner_overlay


class NativeLinuxResourceOverlayTests(unittest.TestCase):
    def fixture(self, directory, unsafe=None):
        path = Path(directory) / 'native.tar.xz'
        with tarfile.open(path, 'w:xz') as archive:
            for name, data, mode in [('app/application.ini', b'identity', 0o644), ('app/browser/omni.ja', b'old UI data', 0o644), ('app/fire-axolotl', b'native executable bytes', 0o755)]:
                entry = tarfile.TarInfo(name)
                entry.size, entry.mode, entry.uid, entry.gid, entry.mtime = len(data), mode, 1001, 1001, 12345
                archive.addfile(entry, io.BytesIO(data))
            link = tarfile.TarInfo('app/browser-link')
            link.type, link.linkname = tarfile.SYMTYPE, 'fire-axolotl'
            archive.addfile(link)
            if unsafe:
                entry = tarfile.TarInfo(unsafe)
                entry.size = 1
                archive.addfile(entry, io.BytesIO(b'x'))
        return path

    @unittest.skipUnless(os.name == 'posix', 'Linux file modes and symlinks require a POSIX packaging host')
    def test_language_data_update_preserves_executable_bytes_permissions_and_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.fixture(directory)
            def update(runtime):
                (runtime / 'browser/omni.ja').write_bytes(b'new language UI data')
                return {'changed': {'language': True}}
            with patch.object(runner_overlay, 'apply', side_effect=update):
                report = runner_overlay.linux_archive(path)
            with tarfile.open(path) as archive:
                self.assertEqual(archive.extractfile('app/fire-axolotl').read(), b'native executable bytes')
                self.assertEqual(archive.getmember('app/fire-axolotl').mode, 0o755)
                self.assertEqual(archive.getmember('app/fire-axolotl').uid, 1001)
                self.assertEqual(archive.getmember('app/fire-axolotl').mtime, 12345)
                self.assertEqual(archive.getmember('app/browser-link').linkname, 'fire-axolotl')
                self.assertEqual(archive.extractfile('app/browser/omni.ja').read(), b'new language UI data')
            self.assertEqual(report['only_native_member_changed'], 'app/browser/omni.ja')

    def test_unsafe_paths_and_duplicate_members_are_rejected_before_editing(self):
        for unsafe in ['../outside', '/absolute', 'app/application.ini']:
            with tempfile.TemporaryDirectory() as directory:
                path = self.fixture(directory, unsafe)
                original = path.read_bytes()
                with self.assertRaises(ValueError):
                    runner_overlay.linux_archive(path)
                self.assertEqual(path.read_bytes(), original)
