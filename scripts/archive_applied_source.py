# SPDX-License-Identifier: MPL-2.0
"""Archive the complete prepared engine source, excluding build/cache output."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
source, output = args.source.resolve(), args.output.resolve()
if not (source / 'fire-axolotl-build.json').is_file():
    raise ValueError('Prepare and verify the source overlay before archiving')
if source == output or source in output.parents:
    raise ValueError('Source archive destination must be outside the source tree')
output.parent.mkdir(parents=True, exist_ok=True)
if os.name == 'nt':
    import zstandard

    def source_only(member):
        parts = Path(member.name).parts
        if any(p.startswith('obj-') or p in {'.git', '.hg', '__pycache__'} or p.endswith('.pyc') for p in parts):
            return None
        return member

    with output.open('wb') as raw, zstandard.ZstdCompressor(level=3, threads=2).stream_writer(raw) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|') as archive:
            archive.add(source, arcname='.', filter=source_only)
else:
    subprocess.run(['tar', '--zstd', '-cf', str(output), '--exclude=./obj-*', '--exclude=./.git', '--exclude=./.hg', '--exclude=__pycache__', '--exclude=*.pyc', '-C', str(source), '.'], check=True)
with output.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
output.with_suffix(output.suffix + '.sha256').write_text(f'{digest}  {output.name}\n')
print(json.dumps({'source_archive': str(output), 'sha256': digest, 'bytes': output.stat().st_size}))
