# SPDX-License-Identifier: MPL-2.0
"""Signal new Mozilla ESR security releases without silently updating the source pin."""
import json
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
