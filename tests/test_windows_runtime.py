# SPDX-License-Identifier: MPL-2.0
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile

from windows_runtime import pe_imports, verify_crt_closure, sha


def image(import_name=None, delay=False, machine=0x8664):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HH', data, 0x84, machine, 1)
    struct.pack_into('<H', data, 0x94, 240)
    struct.pack_into('<H', data, 0x98, 0x20b)
    section = 0x98 + 240
    struct.pack_into('<IIII', data, section + 8, 512, 0x1000, 512, 0x200)
    if import_name:
        struct.pack_into('<II', data, 0x98 + 112 + (13 if delay else 1) * 8, 0x1000, 64)
        if delay:
            struct.pack_into('<II', data, 0x200, 1, 0x1080)
        else:
            struct.pack_into('<I', data, 0x20c, 0x1080)
        text = import_name.encode() + b'\0'
        data[0x280:0x280 + len(text)] = text
    return bytes(data)


class RuntimeDependencyTests(unittest.TestCase):
    def test_normal_and_delayed_runtime_imports_are_recognized(self):
        for delay in (False, True):
            self.assertEqual(pe_imports(image('VCRUNTIME140.dll', delay)), (0x8664, ['vcruntime140.dll']))
        legacy = bytearray(image('VCRUNTIME140.dll', delay=True, machine=0x14c))
        struct.pack_into('<H', legacy, 0x98, 0x10b)
        struct.pack_into('<I', legacy, 0x98 + 28, 0x400000)
        struct.pack_into('<II', legacy, 0x98 + 96 + 13 * 8, 0x1000, 64)
        struct.pack_into('<II', legacy, 0x200, 0, 0x401080)
        self.assertEqual(pe_imports(legacy), (0x14c, ['vcruntime140.dll']))
        with self.assertRaises(ValueError):
            pe_imports(b'not an executable')

    def test_missing_or_changed_crt_is_rejected_even_if_host_has_it(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'native.zip'
            dll = image()
            pins = {'files': {'vcruntime140.dll': {'sha256': sha(dll)}}}
            with patch('windows_runtime.PIN', pins):
                for payload in [None, b'changed', dll]:
                    with zipfile.ZipFile(package, 'w') as archive:
                        archive.writestr('app/application.ini', '[App]')
                        archive.writestr('app/browser.exe', image('VCRUNTIME140.dll'))
                        if payload is not None:
                            archive.writestr('app/vcruntime140.dll', payload)
                    if payload == dll:
                        self.assertEqual(verify_crt_closure(package), {'app/browser.exe': ['vcruntime140.dll']})
                    else:
                        with self.assertRaises(ValueError):
                            verify_crt_closure(package)

    def test_x86_importer_cannot_silently_use_x64_runtime_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'native.zip'
            with zipfile.ZipFile(package, 'w') as archive:
                archive.writestr('app/application.ini', '[App]')
                archive.writestr('app/helper.exe', image('VCRUNTIME140.dll', machine=0x14c))
            with self.assertRaisesRegex(ValueError, 'non-x64'):
                verify_crt_closure(package)
