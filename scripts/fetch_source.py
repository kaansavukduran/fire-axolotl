# SPDX-License-Identifier: MPL-2.0
"""Download the reviewed, hash-pinned Firefox source; do not track a floating branch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def verify(archive, expected):
    with Path(archive).open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha512').hexdigest()
    if actual != expected:
        raise ValueError('Firefox source SHA-512 mismatch; refusing to extract')


def extract(archive, destination):
    destination = Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Destination must be empty; existing work is never replaced')
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as source:
        source.extractall(destination, filter='data')
    roots = [p for p in destination.iterdir() if p.is_dir() and (p / 'mach').is_file()]
    if len(roots) != 1:
        raise ValueError('Expected one Firefox source root')
    return roots[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--destination', type=Path, default=ROOT / 'work/upstream')
    parser.add_argument('--github-env', action='store_true', help='Expose the verified extracted source root to following Actions steps')
    args = parser.parse_args()
    upstream = json.loads((ROOT / 'upstream.json').read_text())
    archive = args.archive or ROOT / 'work' / Path(upstream['source_url']).name
    if not archive.exists():
        archive.parent.mkdir(parents=True, exist_ok=True)
        partial = archive.with_suffix(archive.suffix + '.partial')
        with urllib.request.urlopen(upstream['source_url'], timeout=60) as response, partial.open('wb') as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        verify(partial, upstream['sha512'])
        partial.rename(archive)
    verify(archive, upstream['sha512'])
    source = extract(archive, args.destination)
    if args.github_env:
        with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as stream:
            stream.write(f'FIRE_AXOLOTL_SOURCE={source.as_posix()}\n')
    print(source)


if __name__ == '__main__':
    main()
