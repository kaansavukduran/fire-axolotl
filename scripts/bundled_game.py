# SPDX-License-Identifier: MPL-2.0
"""Fetch immutable, SHA-256-pinned Godot exports; package them without network access.

The game is a separate, zero-permission built-in extension. Its eval requirement
is Godot's JavaScriptBridge, scoped to that origin, never the companion extension.
"""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'browser/game'
PIN = json.loads((SOURCE / 'PIN.json').read_text())
CACHE = ROOT / 'work/aion-game-production'
ADDON_ID = 'aion-game@fire-axolotl.browser'
RESOURCE = 'resource://builtin-addons/aion-game/'
PREFIX = 'chrome/browser/builtin-addons/aion-game/'


def sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def matches(path, record):
    return path.is_file() and path.stat().st_size == record['size'] and sha256(path) == record['sha256']


def files():
    for name in PIN['files']:
        if '/' in name or '\\' in name or not name.startswith('aion-' + PIN['build'] + '.'):
            raise ValueError('Unsafe game asset path')
    CACHE.mkdir(parents=True, exist_ok=True)
    result = {p.name: p for p in SOURCE.iterdir() if p.is_file()}
    missing = any(not matches(CACHE / name, record) for name, record in PIN['files'].items())
    if missing and PIN.get('bundle'):
        record = PIN['bundle']
        archive = ROOT / 'work/aion-game-assets.tar.gz'
        if not matches(archive, record):
            temporary = archive.with_suffix('.part')
            try:
                with urllib.request.urlopen(record['url'], timeout=120) as response, temporary.open('wb') as output:
                    remaining = record['size']
                    while chunk := response.read(min(1024 * 1024, remaining + 1)):
                        remaining -= len(chunk)
                        if remaining < 0:
                            raise ValueError('Oversized bundled game archive')
                        output.write(chunk)
                if not matches(temporary, record):
                    raise ValueError('Bundled game archive hash mismatch')
                temporary.replace(archive)
            finally:
                temporary.unlink(missing_ok=True)
        with tarfile.open(archive) as source:
            members = source.getmembers()
            names = [item.name for item in members]
            if len(names) != len(set(names)) or set(names) != set(PIN['files']):
                raise ValueError('Unexpected or duplicate game archive members')
            for item in members:
                expected = PIN['files'][item.name]
                if not item.isfile() or item.size != expected['size']:
                    raise ValueError('Invalid game archive member')
                destination = CACHE / item.name
                temporary = destination.with_suffix('.part')
                try:
                    with source.extractfile(item) as input_stream, temporary.open('wb') as output:
                        shutil.copyfileobj(input_stream, output)
                    if not matches(temporary, expected):
                        raise ValueError('Extracted game asset hash mismatch')
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
    for name, record in PIN['files'].items():
        target = CACHE / name
        def valid(path):
            return matches(path, record)
        if not valid(target):
            temporary = target.with_suffix(target.suffix + '.part')
            try:
                with urllib.request.urlopen(PIN['origin'] + name, timeout=120) as response, temporary.open('wb') as output:
                    if response.url != PIN['origin'] + name:
                        raise ValueError('Unexpected game download redirect')
                    remaining = record['size']
                    while chunk := response.read(min(1024 * 1024, remaining + 1)):
                        remaining -= len(chunk)
                        if remaining < 0:
                            raise ValueError('Oversized game asset')
                        output.write(chunk)
                if not valid(temporary):
                    raise ValueError('Game asset hash mismatch: ' + name)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        result[name] = target
    return result


def catalog_entry():
    return {'addon_id': ADDON_ID, 'addon_version': json.loads((SOURCE / 'manifest.json').read_text())['version'], 'res_url': RESOURCE}


def allow_game_frame(html):
    """Add only extension frames to the new-tab CSP; keep its other directives."""
    if "frame-src moz-extension:;" in html:
        return html
    anchor = "default-src 'none'; object-src 'none';"
    if html.count(anchor) != 1 or 'frame-src' in html or 'child-src' in html:
        raise ValueError('Unexpected new-tab CSP; review before embedding the game')
    return html.replace(anchor, anchor + ' frame-src moz-extension:;', 1)


def prepare(source):
    directory = source / 'browser/extensions/aion-game'
    addon = directory / 'addon'
    addon.mkdir(parents=True, exist_ok=True)
    for name, path in files().items():
        shutil.copyfile(path, addon / name)
    (directory / 'moz.build').write_text('JAR_MANIFESTS += ["jar.mn"]\n')
    (directory / 'jar.mn').write_text('browser.jar:\n  builtin-addons/aion-game/ (addon/**)\n')
    build = source / 'browser/extensions/moz.build'
    rule = '\n# Fire Axolotl isolated offline game\nDIRS += ["aion-game"]\n'
    if rule not in build.read_text():
        build.write_text(build.read_text() + rule)
    for path in (source / 'browser/extensions/newtab/prerendered').glob('activity-stream*.html'):
        path.write_text(allow_game_frame(path.read_text()))
