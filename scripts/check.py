# SPDX-License-Identifier: MPL-2.0
"""Dependency-free repository checks used locally and in Actions."""
from pathlib import Path
import json
import re
import subprocess
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / 'browser/extension'
translations = {lang: json.loads((EXT / f'_locales/{lang}/messages.json').read_text()) for lang in ['tr', 'en']}
assert translations['tr'].keys() == translations['en'].keys(), 'Locale key mismatch'
keys = set()
for file in EXT.glob('*.html'):
    text = file.read_text()
    keys.update(re.findall(r'data-(?:i18n|label|placeholder)="([^"]+)"', text))
    assert '<script>' not in text and not re.search(r'\son\w+\s*=', text), f'Inline script in {file}'
assert keys <= translations['en'].keys(), f'Missing keys: {keys - translations["en"].keys()}'
for lang, messages in translations.items():
    assert all(v['message'].strip() for v in messages.values()), f'Empty translation in {lang}'
for file in EXT.glob('*.js'):
    subprocess.run(['node', '--check', str(file)], check=True)
    assert 'innerHTML' not in file.read_text(), f'Untrusted HTML sink in {file}'
for file in (ROOT / 'browser/native').glob('*.js'):
    subprocess.run(['node', '--check', str(file)], check=True)
native_keys = set(re.findall(r'data-aion-l10n="([^"]+)"', (ROOT / 'browser/native/aion-layout.inc.xhtml').read_text()))
assert native_keys <= translations['en'].keys(), 'Missing native tab-layout translations'
manifest = json.loads((EXT / 'manifest.json').read_text())
assert manifest['version'] == json.loads((ROOT / 'package.json').read_text())['version']
assert not any('*' in p or p == '<all_urls>' for p in manifest['permissions']), 'Broad mandatory host access'
assert not manifest.get('content_scripts'), 'No automatic page injection is permitted'
assert json.loads((ROOT / 'upstream.json').read_text())['version'] in json.loads((ROOT / 'tests/gecko-runtime.json').read_text())['firefox']['url'], 'Test runtime must match the source pin'
for name, record in json.loads((EXT / 'fonts/SOURCES.json').read_text()).items():
    assert hashlib.sha256((EXT / 'fonts' / name).read_bytes()).hexdigest() == record['sha256'], f'Font provenance mismatch: {name}'
assert manifest['sidebar_action']['open_at_install'] is False, 'Companion sidebar must be opt-in'
for name, record in json.loads((EXT / 'characters/PROVENANCE.json').read_text())['sources'].items():
    assert hashlib.sha256((EXT / 'characters' / name).read_bytes()).hexdigest() == record['packaged_sha256'], f'Character provenance mismatch: {name}'
for character in json.loads((EXT / 'characters/catalog.json').read_text()):
    assert character['path'].startswith('characters/') and '..' not in character['path']
    for frames in character['clips'].values():
        assert frames and all(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= character['width'] and y+h <= character['height'] for x,y,w,h in frames), 'Character frame out of bounds'
print(f'Checked JavaScript, manifests, permissions and {len(keys)} UI translation keys in both languages')
