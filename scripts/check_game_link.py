# SPDX-License-Identifier: MPL-2.0
"""Check the user-owned live game's current deployment for each browser release."""
from datetime import datetime, timezone
from bundled_game import PIN, files
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://aionendlessrun.vercel.app/'


def unchanged_gameplay(compare):
    """Only reviewed non-game files may differ from our game source snapshot.

    Web loader/worker changes do not run in the browser's local wrapper. An
    asset, scene, game script, project/export configuration or unknown change
    requires a fresh game snapshot and full gameplay verification.
    """
    files = compare.get('files')
    if not isinstance(files, list) or compare.get('status') not in ['ahead', 'identical'] or len(files) >= 300 or compare.get('ahead_by', 0) > 250:
        return False
    web_files = {'packaging/web_boot.js', 'packaging/web_update.js', 'packaging/web_updates.py', 'packaging/web_worker.js'}
    def non_runtime(name):
        return name in web_files or name in {'README.md', 'FORGE.md'} or name.startswith(('docs/', 'tests/', '.github/workflows/'))
    return all(non_runtime(item['filename']) and (not item.get('previous_filename') or non_runtime(item['previous_filename'])) for item in files)


def source_freshness(build):
    if build['version'] != PIN['version']:
        raise ValueError('Refresh the bundled game version before publishing')
    if build['build'] == PIN['build']:
        return {'gameplay_source_matches': True, 'mode': 'identical-production-build'}
    request = urllib.request.Request('https://api.github.com/repos/kaansavukduran/aion_endless_run/compare/' + PIN['source_commit'] + '...main', headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'Fire-Axolotl-release-verification'})
    with urllib.request.urlopen(request, timeout=45) as response:
        comparison = json.load(response)
    if not unchanged_gameplay(comparison):
        raise ValueError('Game runtime source changed; refresh and verify the immutable game pin before publishing')
    return {'gameplay_source_matches': True, 'mode': 'same-gameplay-with-new-web-host', 'compared_head': (comparison.get('commits') or [{}])[-1].get('sha', PIN['source_commit']), 'non_runtime_changes': [item['filename'] for item in comparison.get('files', [])], 'limits': 'The local wrapper replaces the web host/updater. Pinned export bytes and source commit remain explicit; a new web host build is not claimed to be the same binary export.'}


def verify():
    with urllib.request.urlopen(URL + 'build.json', timeout=45) as response:
        if response.url != URL + 'build.json':
            raise ValueError('Unexpected game metadata redirect')
        build = json.load(response)
    if not re.fullmatch(r'\d+\.\d+\.\d+', build.get('version', '')) or not re.fullmatch('[a-f0-9]{16}', build.get('build', '')):
        raise ValueError('Invalid live game build metadata')
    with urllib.request.urlopen(URL, timeout=45) as response:
        html = response.read(1024 * 1024).decode()
    if 'Aion' not in html or build['build'] not in html:
        raise ValueError('Live page does not match its advertised game build')
    freshness = source_freshness(build)
    assets = files()
    result = {'freshness':freshness,'packaged_version':PIN['version'],'packaged_build':PIN['build'],'packaged_assets_verified':len(PIN['files']),'source_commit':PIN['source_commit'],'full_game':True,'url':URL,'version':build['version'],'build':build['build'],'tls_verification':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'mode':'Full pinned game packaged locally; runtime does not contact Vercel. Live deployment observation is recorded separately.'}
    (ROOT / 'work/game-link-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Verified live Aion Endless Run deployment:', build['version'], build['build'])
    return result

if __name__ == '__main__':
    verify()
