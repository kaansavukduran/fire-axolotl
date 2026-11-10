# SPDX-License-Identifier: MPL-2.0
"""Check trusted native CI provenance and complete release inputs before publishing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
from verify_native_package import verify

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'release.json').read_text())


def validate_run(run, config=CONFIG):
    if (run.get('status') != 'completed' or run.get('conclusion') != 'success'
            or run.get('head_sha') != config['source_commit']
            or run.get('head_branch') != 'main'
            or run.get('head_repository', {}).get('id') != config['repository_id']
            or run.get('head_repository', {}).get('full_name') != config['repository']
            or run.get('workflow_id') != config['native_workflow_id']
            or run.get('path') != '.github/workflows/native-linux.yml'
            or run.get('event') != 'workflow_dispatch'):
        raise ValueError('Native artifact is not from the reviewed successful main-branch build')


def preflight():
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_upstream.py')], check=True)
    run_id = os.environ.get('AION_NATIVE_RUN_ID', str(CONFIG['native_run_id']))
    if not run_id.isdigit() or int(run_id) != CONFIG['native_run_id']:
        raise ValueError('This preview is pinned to one validated native run')
    request = urllib.request.Request(f'https://api.github.com/repos/{CONFIG["repository"]}/actions/runs/{run_id}', headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=60) as response:
        run = json.load(response)
    validate_run(run)
    print('Trusted native run verified:', run_id, run['head_sha'])


def inputs(directory, evidence, output):
    native = directory / 'fire-axolotl-153.6.0.en-US.linux-x86_64.tar.xz'
    source = directory / 'fire-axolotl-applied-source.tar.zst'
    receipt = json.loads((directory / 'fire-axolotl-build.json').read_text())
    if receipt['overlay_commit'] != CONFIG['source_commit'] or receipt['overlay_dirty']:
        raise ValueError('Native source receipt differs from the reviewed commit')
    if source.stat().st_size < 100_000_000:
        raise ValueError('Expected the full applied engine source, not a smoke archive')
    line = Path(str(source) + '.sha256').read_text().strip().split()
    if len(line) != 2 or line[1] != source.name or not re.fullmatch('[a-f0-9]{64}', line[0]):
        raise ValueError('Invalid applied-source checksum record')
    with source.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != line[0]:
        raise ValueError('Applied-source archive checksum mismatch')
    reports = {name: json.loads((evidence / relative).read_text()) for name, relative in {
        'native': 'native-test-artifacts/results.json',
        'restart': 'native-test-artifacts/restart-results.json',
        'integration': 'native-e2e-artifacts/results.json',
    }.items()}
    if (len(reports['native']['passed']) < 11 or len(reports['restart']['passed']) < 4
            or len(reports['integration']['passed']) < 34
            or reports['integration']['mode'] != 'compiled-fork'
            or reports['native']['identity']['id'] != '{75450dd9-387d-4289-8b23-7ad6609fa530}'):
        raise ValueError('Required compiled-fork test evidence is missing')
    package = verify(native)
    output.mkdir(parents=True, exist_ok=True)
    report = {'source_commit': CONFIG['source_commit'], 'native_run': CONFIG['native_run_id'], 'package': package, 'source_sha256': actual, 'reports': reports, 'stage': 'native-inputs-verified; installer tests still required'}
    (output / 'release-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Native package, full source, restart and integration evidence verified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preflight', 'inputs'])
    parser.add_argument('--directory', type=Path, default=ROOT / 'work/release-inputs')
    parser.add_argument('--evidence', type=Path, default=ROOT / 'work/release-evidence')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    preflight() if args.mode == 'preflight' else inputs(args.directory, args.evidence, args.output)
