# SPDX-License-Identifier: MPL-2.0
"""Publish a complete tested prerelease with repository-scoped Actions credentials."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'release.json').read_text())


def gh(*args):
    return subprocess.check_output(['gh', *args], cwd=ROOT, text=True).strip()


def main():
    if os.environ.get('GITHUB_REPOSITORY') != CONFIG['repository'] or os.environ.get('GITHUB_REF_NAME') != 'main' or os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch':
        raise ValueError('Publishing is restricted to the selected repository main-branch manual workflow')
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_upstream.py')], check=True)
    dist = ROOT / 'dist'
    expected = {}
    for line in (dist / 'SHA256SUMS').read_text().splitlines():
        sha, name = line.split()
        if not re.fullmatch('[a-f0-9]{64}', sha) or Path(name).name != name or name in expected:
            raise ValueError('Invalid release file manifest')
        with (dist / name).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != sha:
                raise ValueError('Release asset changed after validation')
        expected[name] = sha
    with (dist / 'SHA256SUMS').open('rb') as stream:
        expected['SHA256SUMS'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    evidence = json.loads((dist / 'release-manifest.json').read_text())
    if evidence['browser_source_commit'] != CONFIG['source_commit'] or evidence['packaging_commit'] != os.environ['GITHUB_SHA']:
        raise ValueError('Release provenance changed')
    repo, tag = CONFIG['repository'], CONFIG['tag']
    releases = json.loads(gh('api', f'repos/{repo}/releases?per_page=100'))
    existing = next((r for r in releases if r['tag_name'] == tag), None)
    if existing and not existing['draft']:
        raise ValueError('This tag is already published; preserve it and prepare a new version')
    if existing and existing['target_commitish'] not in [CONFIG['source_commit'], os.environ['GITHUB_SHA']]:
        raise ValueError('Existing draft belongs to a different source revision')
    if not existing:
        request = ROOT / 'work/linux-release-draft-create.json'
        request.parent.mkdir(parents=True, exist_ok=True)
        request.write_text(json.dumps({'tag_name': tag, 'target_commitish': os.environ['GITHUB_SHA'], 'name': f'Fire Axolotl {CONFIG["version"]} · Linux geliştirici önizlemesi', 'body': (dist / 'RELEASE-NOTES.md').read_text(), 'draft': True, 'prerelease': True, 'make_latest': 'false'}))
        existing = json.loads(gh('api', '--method', 'POST', f'repos/{repo}/releases', '--input', str(request)))
    for asset in existing['assets']:
        if asset['name'] not in expected or asset.get('digest') != 'sha256:' + expected[asset['name']]:
            raise ValueError('Existing draft asset differs; refusing to overwrite')
    present = {a['name'] for a in existing['assets']}
    for path in sorted(dist.iterdir(), key=lambda p: p.stat().st_size, reverse=True):
        if path.is_file() and path.name not in present:
            gh('release', 'upload', tag, str(path), '--repo', repo)
    final = json.loads(gh('api', f'repos/{repo}/releases/{existing["id"]}'))
    local = {p.name for p in dist.iterdir() if p.is_file()}
    if {a['name'] for a in final['assets']} != local:
        raise ValueError('Release upload is incomplete; retain the unpublished draft')
    for asset in final['assets']:
        if asset['name'] in expected and asset.get('digest') != 'sha256:' + expected[asset['name']]:
            raise ValueError('Uploaded asset digest mismatch')
    gh('release', 'edit', tag, '--repo', repo, '--target', os.environ['GITHUB_SHA'], '--prerelease', '--latest=false', '--notes-file', str(dist / 'RELEASE-NOTES.md'), '--draft=false')
    published = json.loads(gh('api', f'repos/{repo}/releases/{existing["id"]}'))
    if published['draft'] or not published['prerelease']:
        raise ValueError('Release publication state is incorrect')
    print(published['html_url'])


if __name__ == '__main__':
    main()
