# SPDX-License-Identifier: MPL-2.0
import unittest

from windows_sfx import MAGIC, replace_stub


class InstallerWrapperTests(unittest.TestCase):
    def test_rebranding_preserves_the_whole_native_archive(self):
        tag = b';!@Install@!UTF-8!\nTitle="Fire Axolotl"\n;!@InstallEnd@!\n'
        native = MAGIC + bytes(range(256)) * 200
        updated, digest = replace_stub(b'MZold-wrapper' + tag + native, tag, b'MZown-wrapper')
        self.assertEqual(updated, b'MZown-wrapper' + tag + native)
        self.assertEqual(len(digest), 64)
        for invalid in [b'MZ' + tag + native + tag, b'MZ' + tag + b'bad archive', b'notPE' + tag + native]:
            with self.assertRaises(ValueError):
                replace_stub(invalid, tag, b'MZown-wrapper')
        with self.assertRaises(ValueError):
            replace_stub(b'MZ' + tag + native, b'Firefox', b'MZwrapper')
