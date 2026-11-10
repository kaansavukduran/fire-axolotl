# SPDX-License-Identifier: MPL-2.0
"""Manually review the complete official desktop language catalog for a pinned ESR."""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile
from localization import verify

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    upstream = json.loads((ROOT / 'upstream.json').read_text())
    version = upstream['version']
    base = f'https://archive.mozilla.org/pub/firefox/releases/{version}/'
    assert upstream['checksums_url'] == base + 'SHA512SUMS'
    with urllib.request.urlopen(upstream['checksums_url'], timeout=60) as response:
        sums = response.read()
    checksums = {line.split()[1]: line.split()[0] for line in sums.decode().splitlines()}
    assert checksums[f'source/firefox-{version}.source.tar.xz'] == upstream['sha512']
    prefix = 'linux-x86_64/xpi/'
    official = {name[len(prefix):-4]: sha for name, sha in checksums.items() if name.startswith(prefix) and name.endswith('.xpi')}
    windows = {name[len('win64/xpi/'):-4]: sha for name, sha in checksums.items() if name.startswith('win64/xpi/') and name.endswith('.xpi')}
    assert official == windows and 'en-US' in official and 'tr' in official
    with urllib.request.urlopen('https://product-details.mozilla.org/1.0/languages.json', timeout=30) as response:
        names = json.load(response)
    cache = ROOT / 'work/localizations'
    cache.mkdir(parents=True, exist_ok=True)

    def record(locale):
        url = base + prefix + locale + '.xpi'
        path = cache / f'{locale}-{version}.xpi'
        if not path.exists():
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read(5_000_001)
            if len(data) > 5_000_000 or hashlib.sha512(data).hexdigest() != official[locale]:
                raise ValueError('Official language bytes differ from the reviewed checksum catalog')
        else:
            data = path.read_bytes()
            assert hashlib.sha512(data).hexdigest() == official[locale]
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            manifest = json.loads(archive.read('manifest.json'))
        entry = {'url': url, 'sha512': official[locale], 'version': manifest['version'], 'original_id': f'langpack-{locale}@firefox.mozilla.org', 'id': f'langpack-{locale}@fire-axolotl.browser', 'name': names.get(locale, {}).get('native', locale)}
        temporary = path.with_suffix('.catalog-review')
        temporary.write_bytes(data)
        try:
            verify(temporary, locale, entry)
            if not path.exists():
                temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        print('Verified official resource-only language:', locale, flush=True)
        return locale, entry

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = dict(pool.map(record, sorted(set(official) - {'en-US'})))
    pin = {'upstream': version, 'fallback': 'tr', 'base_locale': 'en-US', 'verified_on': datetime.now(timezone.utc).date().isoformat(), 'checksums_url': upstream['checksums_url'], 'checksums_sha512': hashlib.sha512(sums).hexdigest(), 'official_locales': sorted(official), 'locales': records}
    output = ROOT / ('localization.json' if args.write else 'work/localization-catalog-review.json')
    output.write_text(json.dumps(pin, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(official)} official locales: built-in en-US and {len(records)} verified derived language resources; wrote {output.name}')


if __name__ == '__main__':
    main()
