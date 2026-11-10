# SPDX-License-Identifier: MPL-2.0
"""Revalidate the exact preserved native package without recompiling the engine."""
import json
import os
from pathlib import Path
import subprocess
import tarfile
import zipfile

from verify_native_package import verify
from windows_release import gh, digest

ROOT = Path(__file__).resolve().parents[1]
BUILD_RUN = 42791204074
BUILD_COMMIT = '9d564dced55dc4816cc4aeb57387ba1643f007ed'
REPO = 'kaansavukduran/fire-axolotl'
REPO_ID = 1451383337


def validate_build(run, jobs):
    expected = {'status': 'completed', 'head_sha': BUILD_COMMIT, 'head_branch': 'main', 'workflow_id': 412586894, 'path': '.github/workflows/native-windows.yml'}
    if any(run.get(k) != v for k, v in expected.items()) or run.get('event') != 'push' or run['repository']['id'] != REPO_ID or run['head_repository']['id'] != REPO_ID:
        raise ValueError('Preserved engine build provenance mismatch')
    required = {'Compile the actual Windows Firefox fork', 'Package the compiled Windows payload', 'Verify the actual offline NSIS installer was packaged', 'Preserve corresponding applied Windows source'}
    successful = {s['name'] for j in jobs['jobs'] for s in j['steps'] if s['conclusion'] == 'success'}
    if not required <= successful:
        raise ValueError('The preserved compilation, installer and source steps must have succeeded')


def prepare():
    run = json.loads(gh('api', f'repos/{REPO}/actions/runs/{BUILD_RUN}'))
    jobs = json.loads(gh('api', f'repos/{REPO}/actions/runs/{BUILD_RUN}/jobs'))
    validate_build(run, jobs)
    protected = ['browser', 'branding', 'components.json', 'upstream.json', 'localization.json', 'scripts/localization.py', 'scripts/prepare_source.py', 'scripts/package_extension.py', 'scripts/fetch_components.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', BUILD_COMMIT, 'HEAD', '--', *protected], cwd=ROOT, text=True).strip()
    if changed:
        raise ValueError('Revalidation permits test/workflow changes only; engine inputs changed: ' + changed)
    incoming = ROOT / 'work/windows-inputs'
    packages = list(incoming.glob('*.win64.zip'))
    installers = list(incoming.glob('*.installer.exe'))
    if len(packages) != 1 or len(installers) != 1 or installers[0].stat().st_size < 50_000_000:
        raise ValueError('Exact preserved runtime ZIP and offline installer required')
    package = packages[0]
    verify(package)
    source = incoming / 'fire-axolotl-windows-applied-source.tar.zst'
    if Path(str(source) + '.sha256').read_text().split() != [digest(source), source.name]:
        raise ValueError('Preserved applied source checksum mismatch')
    import zstandard
    receipt = None
    with source.open('rb') as raw, zstandard.ZstdDecompressor().stream_reader(raw) as stream:
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for member in archive:
                if member.name.removeprefix('./') == 'fire-axolotl-build.json':
                    receipt = json.load(archive.extractfile(member))
                    break
    if not receipt or receipt['overlay_commit'] != BUILD_COMMIT or receipt['overlay_dirty'] or receipt['upstream'] != json.loads((ROOT / 'upstream.json').read_text()):
        raise ValueError('Applied source identity mismatch')
    runtime = ROOT / 'work/preserved-windows-runtime'
    if runtime.exists():
        raise ValueError('Revalidation runtime directory must be fresh')
    with zipfile.ZipFile(package) as archive:
        # verify() already rejects traversal, links and Windows path collisions.
        roots = [n.rsplit('/', 1)[0] for n in archive.namelist() if n.endswith('/application.ini')]
        if len(roots) != 1:
            raise ValueError('Expected one independently branded native product')
        archive.extractall(runtime)
    binary = runtime / roots[0] / 'fire-axolotl.exe'
    if not binary.is_file():
        raise ValueError('Preserved native executable missing')
    report = {'engine_run_id': BUILD_RUN, 'source_commit': BUILD_COMMIT, 'validation_commit': os.environ['GITHUB_SHA'], 'native_zip_sha256': digest(package), 'installer_sha256': digest(installers[0]), 'source_sha256': digest(source), 'engine_inputs_unchanged': True}
    out = ROOT / 'work/native-test-artifacts'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'validation-inputs.json').write_text(json.dumps(report, indent=2) + '\n')
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as stream:
        stream.write(f'AION_NATIVE_BINARY={binary}\n')
    print('Exact preserved native package and corresponding source verified; all user-interface tests must now run')


if __name__ == '__main__':
    prepare()
