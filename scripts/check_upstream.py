# SPDX-License-Identifier: MPL-2.0
"""Signal new Mozilla ESR security releases without silently updating the source pin."""
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
pin = json.loads((ROOT / 'upstream.json').read_text())
with urllib.request.urlopen('https://product-details.mozilla.org/1.0/firefox_versions.json', timeout=30) as response:
    versions = json.load(response)
current = versions['FIREFOX_ESR']
if pin['version'] != current:
    raise SystemExit(f'Firefox ESR security review required: pinned {pin["version"]}, current {current}. Update source hash, rebuild, test and publish signed updates.')
print(f'Firefox ESR pin is current: {current}')
component = json.loads((ROOT / 'components.json').read_text())['ublock-origin']
headers = {'User-Agent': 'Fire-Axolotl-component-review', 'Accept': 'application/vnd.github+json'}
if token := os.environ.get('GH_TOKEN'):
    headers['Authorization'] = 'Bearer ' + token
request = urllib.request.Request('https://api.github.com/repos/gorhill/uBlock/releases/latest', headers=headers)
with urllib.request.urlopen(request, timeout=30) as response:
    release = json.load(response)
if release['tag_name'] != component['version']:
    raise SystemExit(f'uBlock Origin review required: pinned {component["version"]}, current {release["tag_name"]}. Review source, filters and licenses before updating.')
asset = next((item for item in release['assets'] if item['browser_download_url'] == component['url']), None)
if not asset or asset.get('digest') != 'sha256:' + component['sha256']:
    raise SystemExit('Official uBlock Origin release digest changed or is unavailable; component review required')
print(f'uBlock Origin pin and official release digest are current: {component["version"]}')
