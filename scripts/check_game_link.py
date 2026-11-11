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
    if build['version'] != PIN['version'] or build['build'] != PIN['build']:
        raise ValueError('Bundled game is behind the current production deployment; refresh and verify the immutable game pin before publishing')
    assets = files()
    result = {'packaged_version':PIN['version'],'packaged_build':PIN['build'],'packaged_assets_verified':len(PIN['files']),'source_commit':PIN['source_commit'],'full_game':True,'url':URL,'version':build['version'],'build':build['build'],'tls_verification':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'mode':'Full pinned game packaged locally; runtime does not contact Vercel. Live deployment observation is recorded separately.'}
    (ROOT / 'work/game-link-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Verified live Aion Endless Run deployment:', build['version'], build['build'])
    return result

if __name__ == '__main__':
    verify()
