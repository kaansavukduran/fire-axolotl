# SPDX-License-Identifier: MPL-2.0
"""Build independently branded, pinned native language resources."""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'localization.json').read_text())
CACHE = ROOT / 'work/localizations'


def write_sources(destination, receipts):
    """Keep the original preferred translation resources and derivation recipe."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for locale, record in PIN['locales'].items():
        shutil.copyfile(fetch(locale, record), destination / f'fire-axolotl-localization-{locale}-original.xpi')
    shutil.copyfile(ROOT / 'LICENSE', destination / 'LICENSE.txt')
    for name in ['localization.py']:
        shutil.copyfile(ROOT / 'scripts' / name, destination / name)
    shutil.copyfile(ROOT / 'localization.json', destination / 'localization.json')
    (destination / 'derivation.json').write_text(json.dumps({'upstream': PIN['upstream'], 'license': 'MPL-2.0', 'locales': receipts}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (destination / 'SOURCE.txt').write_text('Original translations: Mozilla localization contributors, MPL-2.0. Original author attribution is retained.\nThe original signed XPI is the preferred translation source; the derived built-in changes only its identity, description and branding.\nMozilla signature files are removed from the modified built-in. External language-package signature verification remains enabled.\nBranding resources used for the derivation are included in branding/. Run build_addon from localization.py with the pinned original XPI and these branding files.\n', encoding='utf-8')


def overlay_resources(archive):
    """Add only pinned language data to our existing native browser archive."""
    import tempfile
    catalog_path = 'chrome/browser/content/browser/built_in_addons.json'
    catalog = json.loads(archive.read(catalog_path))
    entries, receipts = {}, []
    with tempfile.TemporaryDirectory(prefix='fire-axolotl-locale-') as directory:
        branding = Path(directory) / 'branding'
        branding.mkdir()
        for target, original in [('brand.ftl', 'localization/en-US/branding/brand.ftl'), ('brand.properties', 'chrome/en-US/locale/branding/brand.properties')]:
            data = archive.read(original)
            if b'Fire Axolotl' not in data:
                raise ValueError('Independent native branding is required')
            (branding / target).write_bytes(data)
        for locale, record in PIN['locales'].items():
            name = f'fireaxolotl-locale-{locale}'
            addon = Path(directory) / name
            receipts.append(build_addon(fetch(locale, record), addon, locale, record, branding))
            expected = {'addon_id': record['id'], 'addon_version': record['version'], 'res_url': f'resource://builtin-addons/{name}/'}
            matches = [entry for entry in catalog['builtins'] if entry['addon_id'] == record['id']]
            if matches and matches != [expected]:
                raise ValueError('Conflicting built-in language identity')
            if not matches:
                catalog['builtins'].append(expected)
            for file in sorted(addon.rglob('*')):
                if file.is_file():
                    entries[f'chrome/browser/builtin-addons/{name}/' + file.relative_to(addon).as_posix()] = file.read_bytes()
    entries[catalog_path] = (json.dumps(catalog, ensure_ascii=False) + '\n').encode()
    return entries, receipts


def source_archive(native_zip, destination, receipts):
    """Publish preferred source for the language data added after compilation."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix='fire-axolotl-language-source-') as directory:
        directory = Path(directory)
        write_sources(directory, receipts)
        branding = directory / 'branding'
        branding.mkdir()
        with zipfile.ZipFile(native_zip) as package:
            paths = [name for name in package.namelist() if name.endswith('/browser/omni.ja')]
            if len(paths) != 1:
                raise ValueError('Expected one native browser language archive')
            with zipfile.ZipFile(io.BytesIO(package.read(paths[0]))) as archive:
                for target, original in [('brand.ftl', 'localization/en-US/branding/brand.ftl'), ('brand.properties', 'chrome/en-US/locale/branding/brand.properties')]:
                    (branding / target).write_bytes(archive.read(original))
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as output:
            for file in sorted(directory.rglob('*')):
                if file.is_file():
                    output.write(file, file.relative_to(directory).as_posix())
        with zipfile.ZipFile(destination) as archive:
            if archive.testzip() is not None:
                raise ValueError('Language source archive CRC failure')


def verify(path, locale, record):
    if hashlib.sha512(Path(path).read_bytes()).hexdigest() != record['sha512']:
        raise ValueError('Language package hash mismatch')
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)) or sum(e.file_size for e in entries) > 25_000_000:
            raise ValueError('Duplicate entries or oversized language package')
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in entry.filename or stat.S_ISLNK(entry.external_attr >> 16) or entry.flag_bits & 1:
                raise ValueError('Unsafe language package entry')
        manifest = json.loads(archive.read('manifest.json'))
        if (manifest.get('langpack_id') != locale or set(manifest.get('languages', {})) != {locale}
                or manifest['browser_specific_settings']['gecko']['id'] != record['original_id']
                or manifest['version'] != record['version']):
            raise ValueError('Unexpected language package identity/version')
        if any(key in manifest for key in ['permissions', 'optional_permissions', 'content_scripts', 'background']):
            raise ValueError('Language package must contain only localization resources')
        if not {'META-INF/mozilla.rsa', 'META-INF/cose.sig'} <= set(names) or archive.testzip():
            raise ValueError('Missing signature data or damaged language package')
        return manifest


def fetch(locale, record):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f'{locale}-{PIN["upstream"]}.xpi'
    if not path.exists():
        temporary = path.with_suffix('.download')
        try:
            with urllib.request.urlopen(record['url'], timeout=60) as response:
                data = response.read(5_000_001)
            if len(data) > 5_000_000:
                raise ValueError('Language package download exceeds limit')
            temporary.write_bytes(data)
            verify(temporary, locale, record)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    verify(path, locale, record)
    return path


def build_addon(path, destination, locale, record, branding):
    manifest = verify(path, locale, record)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            if item.filename.startswith('META-INF/') or item.filename == 'mozilla-recommendation.json':
                continue
            archive.extract(item, destination)
    manifest['browser_specific_settings']['gecko']['id'] = record['id']
    manifest['name'] = 'Türkçe · Fire Axolotl'
    manifest['description'] = 'Fire Axolotl için Türkçe tarayıcı arayüzü.'
    manifest.pop('default_locale', None)
    modified = ['manifest.json']
    for relative, original in [(f'browser/localization/{locale}/branding/brand.ftl', 'brand.ftl'), (f'browser/chrome/{locale}/locale/branding/brand.properties', 'brand.properties')]:
        target = destination / relative
        if not target.is_file():
            raise ValueError('Language package branding layout changed')
        shutil.copyfile(Path(branding) / original, target)
        modified.append(relative)
    (destination / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'locale': locale, **record, 'modified_files': {name: hashlib.sha256((destination / name).read_bytes()).hexdigest() for name in modified}, 'status': 'derived native built-in; not an unmodified Mozilla-signed package'}


def embed(source, branding):
    upstream = json.loads((ROOT / 'upstream.json').read_text())['version']
    if PIN['upstream'] != upstream:
        raise ValueError('Review language pins for the current engine version')
    receipts, directories = [], []
    sources = source / 'browser/app/distribution/sources'
    sources.mkdir(parents=True, exist_ok=True)
    for locale, record in PIN['locales'].items():
        path = fetch(locale, record)
        name = f'fireaxolotl-locale-{locale}'
        directory = source / 'browser/extensions' / name
        if directory.exists():
            if not (directory / '.fire-axolotl-overlay').is_file():
                raise ValueError('Existing localization directory is not owned by this overlay')
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        (directory / '.fire-axolotl-overlay').write_text('Managed by scripts/localization.py\n')
        addon = directory / 'addon'
        receipts.append(build_addon(path, addon, locale, record, branding))
        (directory / 'moz.build').write_text('JAR_MANIFESTS += ["jar.mn"]\n')
        entries = ['browser.jar:']
        for item in sorted(addon.iterdir()):
            suffix, target = ('/**', item.name + '/') if item.is_dir() else ('', item.name)
            entries.append(f'  builtin-addons/{name}/{target} (addon/{item.name}{suffix})')
        (directory / 'jar.mn').write_text('\n'.join(entries) + '\n')
        directories.append(name)
        shutil.copyfile(path, sources / f'fire-axolotl-localization-{locale}-original.xpi')
    build = source / 'browser/extensions/moz.build'
    begin, end = '# Fire Axolotl localizations begin', '# Fire Axolotl localizations end'
    text = build.read_text()
    if begin in text:
        before, rest = text.split(begin, 1)
        _, after = rest.split(end, 1)
        text = before + after
    block = begin + '\nDIRS += ' + json.dumps(directories) + '\n' + end + '\n'
    build.write_text(text.rstrip() + '\n\n' + block)
    receipt = {'upstream': upstream, 'license': 'MPL-2.0', 'locales': receipts}
    (sources / 'fire-axolotl-localization.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'LICENSE', sources / 'Fire-Axolotl-Localization-LICENSE.txt')
    (sources / 'Fire-Axolotl-Localization-SOURCE.txt').write_text('Original translations: Mozilla localization contributors, MPL-2.0; author attribution remains in each manifest.\nThe pinned original signed XPI is included beside this notice.\nFire Axolotl changes the addon identity, localized description and product branding.\nThe derived resource is a built-in of this independently compiled browser; Mozilla signature files are not copied into the modified resource.\nExternal language-pack signature verification remains enabled.\nPreferred modification source: original XPI resources plus scripts/localization.py, localization.json and the prepared branding files in the complete applied source archive.\n')
    return receipt
