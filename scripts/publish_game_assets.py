# SPDX-License-Identifier: MPL-2.0
"""Publish only the already reviewed immutable game assets with Actions auth."""
import gzip
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
from urllib.parse import urlsplit
import bundled_game


def main():
    pin = bundled_game.PIN
    bundle = pin.pop('bundle')
    paths = bundled_game.files()
    directory = bundled_game.ROOT / 'work'
    archive = directory / Path(urlsplit(bundle['url']).path).name
    with archive.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', mtime=0, filename='') as compressed, tarfile.open(fileobj=compressed, mode='w|') as packed:
        for name in sorted(pin['files']):
            path = paths[name]
            info = tarfile.TarInfo(name)
            info.size = path.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            with path.open('rb') as source:
                packed.addfile(info, source)
    if archive.stat().st_size != bundle['size'] or hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest() != bundle['sha256']:
        raise ValueError('Reproduced game archive differs from the reviewed pin')
    tag = urlsplit(bundle['url']).path.split('/')[-2]
    repo = 'kaansavukduran/fire-axolotl'
    notes = directory / 'game-component-notes.md'
    notes.write_text('Pinned full Aion Endless Run game assets for browser packaging. This is a build input, not a browser installer.\n\n' + (bundled_game.SOURCE / 'SOURCE.md').read_text() + '\n\nGame: ' + pin['version'] + ', production build: ' + pin['build'] + '. SHA-256: ' + bundle['sha256'] + '. Original game source/asset and engine/font license copies are in browser/game/.\n')
    subprocess.run(['gh', 'release', 'create', tag, '--repo', repo, '--target', os.environ['GITHUB_SHA'], '--title', 'Aion Endless Run ' + pin['version'] + ' · pinned browser game assets', '--notes-file', str(notes), '--draft', '--prerelease', '--latest=false'], check=True)
    subprocess.run(['gh', 'release', 'upload', tag, str(archive), '--repo', repo], check=True)
    subprocess.run(['gh', 'release', 'edit', tag, '--repo', repo, '--draft=false', '--prerelease', '--latest=false'], check=True)


if __name__ == '__main__':
    main()
