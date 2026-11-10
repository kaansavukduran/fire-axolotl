# SPDX-License-Identifier: MPL-2.0
"""Apply only audited new-tab UI resources to our own compiled browser.

The engine and built-in add-ons are preserved. The modified omni.ja and complete
overlay source are recorded separately from the original engine build receipt.
"""
import argparse
import configparser
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import tarfile
import copy
import zipfile
from localization import overlay_resources

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'chrome/browser/content/browser/'


def check_source_delta(base):
    protected = ['browser', 'branding', 'components.json', 'upstream.json', 'localization.json', 'scripts/localization.py', 'scripts/prepare_source.py', 'scripts/package_extension.py', 'scripts/fetch_components.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD', '--', *protected], cwd=ROOT, text=True).splitlines()
    allowed = {'browser/native/aion-chrome.js', 'browser/native/aion-layout.js', 'browser/native/aion-layout.inc.xhtml', 'scripts/prepare_source.py', 'browser/extension/_locales/tr/messages.json', 'browser/extension/_locales/en/messages.json'}
    allowed.update('browser/native/aion-runner/' + name for name in ['AionRunnerParent.sys.mjs', 'AionRunnerChild.sys.mjs', 'card.sys.mjs', 'world.sys.mjs', 'aion-runner.png', 'PROVENANCE.json'])
    allowed.update(['localization.json', 'scripts/localization.py', 'browser/preferences/fire-axolotl.js'])
    if set(changed) - allowed:
        raise ValueError('The compiled core differs from the reviewed build: ' + ', '.join(sorted(set(changed) - allowed)))
    before = subprocess.check_output(['git', 'show', base + ':scripts/prepare_source.py'], cwd=ROOT).decode()
    anchor = "    shutil.copytree(ROOT / 'browser/extension/fonts', base / 'content/aion-fonts', dirs_exist_ok=True)"
    if "shutil.copytree(ROOT / 'browser/native/aion-runner'" not in before:
        before = before.replace(anchor, "    shutil.copytree(ROOT / 'browser/native/aion-runner', base / 'content/aion-runner', dirs_exist_ok=True)\n" + anchor)
    anchor = "    replace_once(base / 'jar.mn', 'browser.jar:\\n', 'browser.jar:\\n' + entries + '\\n')"
    if 'runner_anchor =' not in before:
        before = before.replace(anchor, anchor + "\n    runner_anchor = '        content/browser/aion-fonts/ (content/aion-fonts/**)\\n'\n    replace_once(base / 'jar.mn', runner_anchor, runner_anchor + '        content/browser/aion-runner/ (content/aion-runner/**)\\n')")
    if 'from localization import embed as embed_localizations' not in before:
        anchor = 'from fetch_components import fetch_all, PIN as UBLOCK_PIN, CACHE as COMPONENT_CACHE, sha256'
        before = before.replace(anchor, anchor + '\nfrom localization import embed as embed_localizations')
        before = before.replace('    ublock = embed_ublock(source)', "    localizations = embed_localizations(source, branding / 'locales/en-US')\n    ublock = embed_ublock(source)")
        anchor = "    (source / 'fire-axolotl-build.json').write_text(json.dumps(receipt, indent=2) + '\\n')"
        before = before.replace(anchor, "    receipt['localizations'] = localizations\n" + anchor)
    if before != (ROOT / 'scripts/prepare_source.py').read_text():
        raise ValueError('Only the reviewed resource-copy additions to source preparation are allowed')
    old_preferences = subprocess.check_output(['git', 'show', base + ':browser/preferences/fire-axolotl.js'], cwd=ROOT).decode()
    if 'pref("intl.locale.requested", "");' not in old_preferences:
        old_preferences = old_preferences.replace('/* SPDX-License-Identifier: MPL-2.0 */\n', '/* SPDX-License-Identifier: MPL-2.0 */\n' + LOCALE_DEFAULT)
    if old_preferences != (ROOT / 'browser/preferences/fire-axolotl.js').read_text():
        raise ValueError('Only the OS-language default preference addition is reviewed')
    return changed


LOCALE_DEFAULT = '// Follow the operating-system language until the user makes a language choice.\npref("intl.locale.requested", "");\n'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply(runtime):
    identity = configparser.ConfigParser()
    identity.read(runtime / 'application.ini')
    if identity['App']['ID'] != '{75450dd9-387d-4289-8b23-7ad6609fa530}' or identity['App']['Name'] != 'FireAxolotl':
        raise ValueError('The compiled Fire Axolotl product is required')
    path = runtime / 'browser/omni.ja'
    original = path.read_bytes()
    replacements = {
        PREFIX + 'aion-chrome.js': (ROOT / 'browser/native/aion-chrome.js').read_bytes(),
        PREFIX + 'preferences/aion-layout.js': (ROOT / 'browser/native/aion-layout.js').read_bytes()
    }
    for locale in ['tr', 'en']:
        replacements[PREFIX + f'preferences/aion-{locale}.json'] = (ROOT / f'browser/extension/_locales/{locale}/messages.json').read_bytes()
    for file in sorted((ROOT / 'browser/native/aion-runner').iterdir()):
        if file.is_file():
            replacements[PREFIX + 'aion-runner/' + file.name] = file.read_bytes()
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('Duplicate omni.ja member')
        locale_entries, locales = overlay_resources(archive)
        replacements.update(locale_entries)
        pref_path = 'defaults/preferences/firefox-branding.js'
        preferences = archive.read(pref_path).decode().replace('\r\n', '\n')
        if 'pref("intl.locale.requested", "");' not in preferences:
            expected = (ROOT / 'browser/preferences/fire-axolotl.js').read_text().replace(LOCALE_DEFAULT, '')
            if preferences != expected:
                raise ValueError('Unexpected native privacy/security defaults')
            replacements[pref_path] = (ROOT / 'browser/preferences/fire-axolotl.js').read_bytes()
        elif preferences != (ROOT / 'browser/preferences/fire-axolotl.js').read_text():
            raise ValueError('Unexpected native language or privacy defaults')
        pref = PREFIX + 'preferences/preferences.xhtml'
        text = archive.read(pref).decode()
        begin, end = '<!-- Fire Axolotl preferences begin -->', '<!-- Fire Axolotl preferences end -->'
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError('Expected the existing native appearance preferences')
        before, rest = text.split(begin, 1)
        _, after = rest.split(end, 1)
        text = before + begin + '\n' + (ROOT / 'browser/native/aion-layout.inc.xhtml').read_text().rstrip() + '\n' + end + after
        replacements[pref] = text.encode()
        temp = path.with_suffix('.ja.new')
        unchanged = {}
        changed = {}
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as output:
            for entry in archive.infolist():
                data = archive.read(entry.filename)
                updated = replacements.pop(entry.filename, data)
                output.writestr(entry, updated)
                if data != updated:
                    changed[entry.filename] = {'before': sha(data), 'after': sha(updated)}
                else:
                    unchanged[entry.filename] = sha(data)
            for name, data in replacements.items():
                output.writestr(name, data)
                changed[name] = {'before': None, 'after': sha(data)}
    with zipfile.ZipFile(temp) as archive:
        if archive.testzip() is not None:
            raise ValueError('Repacked UI archive CRC failure')
        if any(sha(archive.read(name)) != expected for name, expected in unchanged.items()):
            raise ValueError('An unrelated native browser resource changed')
    if changed:
        temp.replace(path)
    else:
        temp.unlink()
    return {'original_browser_omni_sha256': sha(original), 'browser_omni_sha256': sha(path.read_bytes()), 'changed': changed, 'unchanged_member_count': len(unchanged), 'localizations': locales, 'scope': 'Listed browser/omni.ja UI resources, pinned built-in translation data/catalog and OS-language default only. Native executables, engine, policies, Aion and signed uBlock Origin are preserved.'}


def windows_archive(path):
    original_hash = sha(path.read_bytes())
    with tempfile.TemporaryDirectory(prefix='aion-ui-') as folder:
        directory = Path(folder)
        with zipfile.ZipFile(path) as archive:
            roots = [name.rsplit('/', 1)[0] for name in archive.namelist() if name.endswith('/application.ini')]
            if len(roots) != 1:
                raise ValueError('Expected one compiled runtime')
            archive.extractall(directory)
        report = apply(directory / roots[0])
        if not report['changed']:
            return {**report, 'original_native_zip_sha256': original_hash, 'native_zip_sha256': original_hash, 'unchanged_native_files': len(archive.namelist()), 'only_native_member_changed': None}
        omni = roots[0] + '/browser/omni.ja'
        replacement = (directory / omni).read_bytes()
        temp = path.with_suffix('.zip.new')
        unchanged = {}
        with zipfile.ZipFile(path) as archive, zipfile.ZipFile(temp, 'w') as output:
            for entry in archive.infolist():
                data = archive.read(entry.filename)
                output.writestr(entry, replacement if entry.filename == omni else data)
                if entry.filename != omni:
                    unchanged[entry.filename] = sha(data)
        with zipfile.ZipFile(temp) as archive:
            if archive.testzip() is not None or any(sha(archive.read(name)) != value for name, value in unchanged.items()):
                raise ValueError('A native file changed outside the reviewed browser UI archive')
        temp.replace(path)
    return {**report, 'original_native_zip_sha256': original_hash, 'native_zip_sha256': sha(path.read_bytes()), 'unchanged_native_files': len(unchanged), 'only_native_member_changed': omni}


def linux_archive(path):
    """Keep every native file, mode and symlink while changing reviewed UI data."""
    original_hash = sha(path.read_bytes())
    with tempfile.TemporaryDirectory(prefix='aion-linux-ui-') as folder:
        directory = Path(folder)
        with tarfile.open(path) as archive:
            members = archive.getmembers()
            names = [m.name for m in members]
            if len(names) != len(set(names)) or any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n for n in names):
                raise ValueError('Unsafe or duplicate native Linux archive member')
            roots = [m.name.rsplit('/', 1)[0] for m in members if m.isfile() and m.name.endswith('/application.ini')]
            if len(roots) != 1:
                raise ValueError('Expected one compiled runtime')
            archive.extractall(directory, filter='data')
        report = apply(directory / roots[0])
        if not report['changed']:
            return {**report, 'original_native_tar_sha256': original_hash, 'native_tar_sha256': original_hash, 'only_native_member_changed': None}
        omni = roots[0] + '/browser/omni.ja'
        replacement = (directory / omni).read_bytes()
        temporary = path.with_suffix('.xz.new')
        unchanged, metadata = {}, {}
        with tarfile.open(path) as archive, tarfile.open(temporary, 'w:xz', preset=3) as output:
            for member in archive:
                metadata[member.name] = (member.type, member.mode, member.linkname, member.uid, member.gid, member.uname, member.gname, member.mtime)
                if member.isfile():
                    data = archive.extractfile(member).read()
                    if member.name == omni:
                        member = copy.copy(member)
                        member.size = len(replacement)
                        output.addfile(member, io.BytesIO(replacement))
                    else:
                        unchanged[member.name] = sha(data)
                        output.addfile(member, io.BytesIO(data))
                else:
                    output.addfile(member)
        with tarfile.open(temporary) as archive:
            actual = {}
            for member in archive:
                actual[member.name] = (member.type, member.mode, member.linkname, member.uid, member.gid, member.uname, member.gname, member.mtime)
                if member.name in unchanged and sha(archive.extractfile(member).read()) != unchanged[member.name]:
                    raise ValueError('An unrelated native Linux file changed')
            if actual != metadata:
                raise ValueError('Native Linux file modes or links changed')
        temporary.replace(path)
    return {**report, 'original_native_tar_sha256': original_hash, 'native_tar_sha256': sha(path.read_bytes()), 'unchanged_native_files': len(unchanged), 'only_native_member_changed': omni}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runtime', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    report = apply(args.runtime)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Applied {len(report["changed"])} UI resources; {report["unchanged_member_count"]} original archive members verified unchanged')
