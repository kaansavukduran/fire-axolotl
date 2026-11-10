# SPDX-License-Identifier: MPL-2.0
"""Fetch exact released bytes for a read-only network-evidence review."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
windows = platform.system() == 'Windows'
tag = 'v0.1.0-dev.20261110-windows.1' if windows else 'v0.1.0-dev.20261110-linux.1'
name = 'fire-axolotl-0.1.0-dev.20261110.1-windows-x86_64.zip' if windows else 'fire-axolotl-153.7.0.en-US.linux-x86_64.tar.xz'
expected = 'f032b69fab754923f7f43978169c7a5adf79ed74b120a7d35f0ec99a990e0832' if windows else 'aedaeda2a9c784bb7811dac17544c75fe37d2491663e48e85ff8ada741994c4f'
release = json.loads(subprocess.check_output(['gh', 'api', f'repos/kaansavukduran/fire-axolotl/releases/tags/{tag}']))
assert not release['draft'] and release['prerelease']
assert release['target_commitish'] == '0759fae4b09e5cf27f709a1496eea3a23d1c33df'
asset = next(item for item in release['assets'] if item['name'] == name)
assert asset['digest'] == 'sha256:' + expected
out = ROOT / 'work/published-network-review'
out.mkdir(parents=True, exist_ok=True)
archive = out / name
with urllib.request.urlopen(asset['browser_download_url'], timeout=120) as response, archive.open('wb') as stream:
    while block := response.read(1024 * 1024):
        stream.write(block)
with archive.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected
assert archive.stat().st_size == asset['size']
target = out / 'runtime'
target.mkdir()
if windows:
    with zipfile.ZipFile(archive) as source:
        assert source.testzip() is None
        for item in source.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert ':' not in item.filename and '\\' not in item.filename
        source.extractall(target)
else:
    with tarfile.open(archive) as source:
        source.extractall(target, filter='data')
binary = target / 'fire-axolotl' / ('fire-axolotl.exe' if windows else 'fire-axolotl')
assert binary.is_file()
with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as stream:
    stream.write(f'AION_NATIVE_BINARY={binary}\n')
evidence = ROOT / 'work/network-test-artifacts'
evidence.mkdir(exist_ok=True)
(evidence / 'published-provenance.json').write_text(json.dumps({'release': release['html_url'], 'asset': name, 'bytes': asset['size'], 'sha256': expected, 'packaging_commit': release['target_commitish'], 'verification_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(), 'unchanged_published_bytes': True}, indent=2) + '\n')
print('Exact published payload SHA-256 verified; no release asset is changed')
