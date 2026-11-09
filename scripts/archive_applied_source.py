# SPDX-License-Identifier: MPL-2.0
"""Archive the complete prepared engine source, excluding build/cache output."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

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
subprocess.run(['tar', '--zstd', '-cf', str(output), '--exclude=./obj-*', '--exclude=./.git', '--exclude=./.hg', '--exclude=__pycache__', '--exclude=*.pyc', '-C', str(source), '.'], check=True)
with output.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
output.with_suffix(output.suffix + '.sha256').write_text(f'{digest}  {output.name}\n')
print(json.dumps({'source_archive': str(output), 'sha256': digest, 'bytes': output.stat().st_size}))
