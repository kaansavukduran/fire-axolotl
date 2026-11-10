# SPDX-License-Identifier: MPL-2.0
"""Package pinned, unmodified Microsoft CRT files with the Windows application."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'windows-runtime.json').read_text())
CRT_NAME = re.compile(r'^(?:msvcp|vcruntime|concrt|vccorlib)\d+(?:_[a-z0-9_]+)?\.dll$', re.I)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pe_imports(data):
    """Return machine and normal/delay import names from a PE image."""
    def u16(offset): return struct.unpack_from('<H', data, offset)[0]
    def u32(offset): return struct.unpack_from('<I', data, offset)[0]
    if data[:2] != b'MZ':
        raise ValueError('Expected PE image')
    pe = u32(60)
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('Invalid PE signature')
    coff, opt = pe + 4, pe + 24
    magic = u16(opt)
    if magic not in (0x10b, 0x20b):
        raise ValueError('Unsupported PE optional header')
    sections = []
    for index in range(u16(coff + 2)):
        offset = opt + u16(coff + 16) + 40 * index
        size, address, raw_size, raw = struct.unpack_from('<IIII', data, offset + 8)
        sections.append((address, max(size, raw_size), raw))
    def file_offset(rva):
        for address, size, raw in sections:
            if address <= rva < address + size:
                return rva - address + raw
        raise ValueError('PE import RVA is outside its sections')
    def name(rva):
        offset = file_offset(rva)
        return data[offset:data.index(0, offset)].decode('ascii').lower()
    directory = opt + (112 if magic == 0x20b else 96)
    imports = []
    for entry, stride, name_offset in [(1, 20, 12), (13, 32, 4)]:
        rva = u32(directory + entry * 8)
        if not rva:
            continue
        offset = file_offset(rva)
        while any(data[offset:offset + stride]):
            name_rva = u32(offset + name_offset)
            if entry == 13 and not u32(offset) & 1:
                image_base = struct.unpack_from('<Q' if magic == 0x20b else '<I', data, opt + (24 if magic == 0x20b else 28))[0]
                name_rva -= image_base
            imports.append(name(name_rva))
            offset += stride
    return u16(coff), imports


def verify_crt_closure(path):
    requirements = {}
    with zipfile.ZipFile(path) as archive:
        root = next(n.removesuffix('application.ini') for n in archive.namelist() if n.endswith('/application.ini'))
        for entry in archive.namelist():
            if not entry.lower().endswith(('.exe', '.dll')):
                continue
            machine, imports = pe_imports(archive.read(entry))
            required = sorted({n for n in imports if CRT_NAME.match(n)})
            if required and machine != 0x8664:
                raise ValueError('A non-x64 component requires an architecture-specific CRT layout')
            for name in required:
                if root + name not in archive.namelist() or name not in PIN['files']:
                    raise ValueError('Required application-local runtime missing: ' + name)
                if sha(archive.read(root + name)) != PIN['files'][name]['sha256']:
                    raise ValueError('Application-local runtime changed: ' + name)
            if required:
                requirements[entry] = required
    return requirements


def augment(path):
    staging = ROOT / 'work/windows-runtime'
    command = [shutil.which('pwsh') or 'powershell', '-NoProfile', '-NonInteractive', '-File', str(ROOT / 'scripts/collect_windows_runtime.ps1'), '-OutputDirectory', str(staging)]
    subprocess.run(command, check=True)
    collection = json.loads((staging / 'collection.json').read_text(encoding='utf-8-sig'))
    original = sha(path.read_bytes())
    additions = {}
    with zipfile.ZipFile(path) as archive:
        root = next(n.removesuffix('application.ini') for n in archive.namelist() if n.endswith('/application.ini'))
        for name, expected in PIN['files'].items():
            data = (staging / 'files' / name).read_bytes()
            record = collection['files'][name]
            if sha(data) != expected['sha256'] or len(data) != expected['bytes'] or pe_imports(data)[0] != 0x8664 or record['signature'] != 'Valid' or 'O=Microsoft Corporation' not in record['signer']:
                raise ValueError('Runtime hash, architecture or Microsoft signature mismatch')
            additions[root + name] = data
        for name in ['MICROSOFT-NOTICE.txt', 'REDISTRIBUTION.txt']:
            additions[root + 'distribution/sources/windows-runtime/' + name] = (ROOT / 'windows-runtime' / name).read_bytes()
        additions[root + 'distribution/sources/windows-runtime/REDIST.txt'] = (staging / 'REDIST.txt').read_bytes()
        additions[root + 'distribution/sources/windows-runtime/provenance.json'] = (json.dumps({'pins': PIN, 'collection': collection}, indent=2) + '\n').encode()
        if set(additions) & set(archive.namelist()):
            raise ValueError('Runtime augmentation must not overwrite an existing native file')
        temporary = path.with_suffix('.zip.runtime')
        unchanged = {}
        with zipfile.ZipFile(temporary, 'w') as output:
            for entry in archive.infolist():
                data = archive.read(entry.filename)
                unchanged[entry.filename] = sha(data)
                output.writestr(entry, data)
            for name, data in additions.items():
                output.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() or any(sha(archive.read(n)) != h for n, h in unchanged.items()):
            raise ValueError('An existing native file changed while adding the runtime')
    requirements = verify_crt_closure(temporary)
    temporary.replace(path)
    return {'original_native_zip_sha256': original, 'native_zip_with_runtime_sha256': sha(path.read_bytes()), 'added': {n: sha(d) for n, d in additions.items()}, 'unchanged_native_files': len(unchanged), 'crt_imports': requirements, 'collection': collection, 'license': 'Unmodified Microsoft Windows Distributable Code; not MPL; notices included in application and about:license'}
