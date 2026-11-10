# SPDX-License-Identifier: MPL-2.0
"""Compare the real installed payload with the source-built Windows archive."""
import hashlib
import json
import os
from pathlib import Path
import zipfile
from windows_release import DIST, STEM, digest

ROOT = Path(__file__).resolve().parents[1]
destination = Path(os.environ['AION_INSTALLED_DIRECTORY']).resolve()
package = DIST / f'{STEM}.zip'
overlay = json.loads((DIST / 'newtab-ui-overlay.json').read_text())
if not package.is_file() or digest(package) != overlay['native_zip_sha256']:
    raise ValueError('The installed payload must match the exact verified native ZIP')
count = 0
with zipfile.ZipFile(package) as archive:
    ini = next(n for n in archive.namelist() if n.endswith('/application.ini'))
    prefix = ini.removesuffix('application.ini')
    for member in archive.infolist():
        if member.is_dir():
            continue
        if not member.filename.startswith(prefix):
            raise ValueError('Unexpected path outside the application payload')
        relative = member.filename.removeprefix(prefix)
        path = (destination / relative).resolve()
        if not path.is_relative_to(destination) or not path.is_file():
            raise ValueError(f'Installed payload missing or unsafe: {relative}')
        with archive.open(member) as source, path.open('rb') as installed:
            if hashlib.file_digest(source, 'sha256').digest() != hashlib.file_digest(installed, 'sha256').digest():
                raise ValueError(f'Installed payload changed: {relative}')
        count += 1
if count < 20:
    raise ValueError('Incomplete native payload')
(ROOT / 'work/windows-installer-test/payload.json').write_text(json.dumps({'verified_files': count, 'all_packaged_payload_bytes_match': True}, indent=2) + '\n')
print(f'Actual installed native payload matches all {count} packaged files')
