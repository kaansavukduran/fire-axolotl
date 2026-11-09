# SPDX-License-Identifier: MPL-2.0
"""Apply an inspectable overlay to the reviewed Firefox source tree."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_extension import package
from fetch_components import fetch_all, PIN as UBLOCK_PIN, CACHE as COMPONENT_CACHE, sha256

ROOT = Path(__file__).resolve().parents[1]
MARKER = '# Fire Axolotl built-in companion\nDIRS += ["aion"]\n'


def replace_once(path, old, new):
    text = path.read_text()
    if new in text:
        return
    if text.count(old) != 1:
        raise ValueError(f'Upstream changed: expected exactly one anchor in {path}')
    path.write_text(text.replace(old, new, 1))


def replace_preferences_block(path, markup, anchor='<!-- Browser layout -->'):
    begin = '<!-- Fire Axolotl preferences begin -->'
    end = '<!-- Fire Axolotl preferences end -->'
    text = path.read_text()
    block = begin + '\n' + markup.rstrip() + '\n' + end
    if begin in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError('Duplicate or incomplete Aion preferences markers')
        before, rest = text.split(begin, 1)
        _, after = rest.split(end, 1)
        path.write_text(before + block + after)
        return
    # Migrate the initial overlay so adding controls never creates duplicate IDs.
    text, count = re.subn(r'<groupbox id="aionLayoutGroup"[\s\S]*?</groupbox>\s*', '', text)
    if count > 1 or text.count(anchor) != 1:
        raise ValueError('Unexpected native preferences structure')
    path.write_text(text.replace(anchor, block + '\n' + anchor, 1))


def remove_legacy_preferences(path):
    text = path.read_text()
    text = re.sub(r'<!-- Fire Axolotl preferences begin -->[\s\S]*?<!-- Fire Axolotl preferences end -->\s*', '', text)
    text = re.sub(r'<groupbox id="aionLayoutGroup"[\s\S]*?</groupbox>\s*', '', text)
    path.write_text(text)


def replace_app_startup_identity(path):
    # Keep the application guard; xpcshell must not start the desktop browser.
    replace_once(path, 'application={ec8030f7-c20a-464f-9b0e-13a3a9e97384}', 'application={75450dd9-387d-4289-8b23-7ad6609fa530}')
    replace_once(path, '#   browser:        {ec8030f7-c20a-464f-9b0e-13a3a9e97384}', '#   Fire Axolotl:   {75450dd9-387d-4289-8b23-7ad6609fa530}')


def prepare_windows_installer(source, branding):
    path = branding / 'branding.nsi'
    text = path.read_text()
    values = {
        'BrandFullNameInternal': 'Fire Axolotl', 'BrandFullName': 'Fire Axolotl',
        'CompanyName': 'Fire Axolotl',
        'URLInfoAbout': 'https://github.com/kaansavukduran/fire-axolotl',
        'HelpLink': 'https://github.com/kaansavukduran/fire-axolotl/issues',
        'URLSystemRequirements': 'https://github.com/kaansavukduran/fire-axolotl/blob/main/docs/BUILD.md',
        'URLManualDownload': 'https://github.com/kaansavukduran/fire-axolotl/releases',
        'URLStubDownloadX86': '', 'URLStubDownloadAMD64': '', 'URLStubDownloadAArch64': '',
        'CertNameDownload': 'Fire Axolotl', 'CertIssuerDownload': '',
    }
    for key, value in values.items():
        text, count = re.subn(r'(?m)^!define\s+' + key + r'\s+"[^"]*"\s*$', f'!define {key} "{value}"', text)
        if count != 1:
            raise ValueError(f'Unexpected Windows installer branding: {key}')
    path.write_text(text)
    defines = source / 'browser/installer/windows/nsis/defines.nsi.in'
    for key, old, new in [('AppName', 'Firefox', 'FireAxolotl'), ('DDEApplication', 'Firefox', 'FireAxolotl'), ('AppRegName', 'Firefox', 'FireAxolotl'), ('BrandProductName', 'Firefox', 'Fire Axolotl')]:
        text = defines.read_text()
        text, count = re.subn(r'(?m)^!define\s+' + key + r'\s+"' + re.escape(old) + r'"$', f'!define {key} "{new}"', text)
        if count != 1 and not re.search(r'(?m)^!define\s+' + key + r'\s+"' + re.escape(new) + r'"$', text):
            raise ValueError(f'Unexpected Windows integration namespace: {key}')
        defines.write_text(text)
    shutil.copyfile(ROOT / 'branding/aion.ico', branding / 'firefox64.ico')
    for name in ['wizHeader.bmp', 'wizHeaderRTL.bmp', 'wizWatermark.bmp']:
        shutil.copyfile(ROOT / 'branding/windows' / name, branding / name)


def replace_nsis_function(path, name, body):
    pattern = r'^Function ' + re.escape(name) + r'\n.*?^FunctionEnd$'
    text, count = re.subn(pattern, lambda _match: f'Function {name}\n{body}\nFunctionEnd', path.read_text(), flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise ValueError(f'Unexpected Windows installer function: {name}')
    path.write_text(text)


def prepare_windows_installer_privacy(source):
    base = source / 'browser/installer/windows'
    for name in ['app.tag', 'stub.tag']:
        replace_once(base / name, 'Title="Mozilla Firefox"', 'Title="Fire Axolotl"')
    installer = base / 'nsis/installer.nsi'
    uninstaller = base / 'nsis/uninstaller.nsi'
    replace_nsis_function(installer, 'SendPingIfApplicable', '  Return')
    replace_nsis_function(uninstaller, 'un.SendUninstallPing', '  Return')
    replace_nsis_function(uninstaller, 'un.onGUIEnd', '  ${un.OnEndCommon}')
    replace_nsis_function(installer, 'CustomAbort', '  MessageBox MB_YESNO|MB_ICONEXCLAMATION "$(MOZ_MUI_TEXT_ABORTWARNING)" IDYES +1 IDNO +2\n  Return\n  Abort')
    survey = '!define MUI_FINISHPAGE_SHOWREADME\n!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED\n!define MUI_FINISHPAGE_SHOWREADME_TEXT $(UN_SURVEY_CHECKBOX_LABEL)\n!define MUI_FINISHPAGE_SHOWREADME_FUNCTION un.Survey'
    replace_once(uninstaller, survey, '; Fire Axolotl has no uninstall survey.')
    replace_once(installer, 'WriteRegDWORD HKCU ${MOZ_LAUNCHER_SUBKEY} "$INSTDIR\\${FileMainEXE}|Telemetry" 1', 'WriteRegDWORD HKCU ${MOZ_LAUNCHER_SUBKEY} "$INSTDIR\\${FileMainEXE}|Telemetry" 0')


def embed_ublock(source):
    import zipfile
    xpi, corresponding_source = fetch_all()
    directory = source / 'browser/extensions/ublock-origin'
    addon = directory / 'addon'
    if addon.exists():
        shutil.rmtree(addon)
    addon.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(xpi) as archive:
        archive.extractall(addon)  # fetch_all already validated every path and hash.
    (directory / 'moz.build').write_text('JAR_MANIFESTS += ["jar.mn"]\n')
    entries = ['browser.jar:']
    for item in sorted(addon.iterdir()):
        suffix = '/**' if item.is_dir() else ''
        target = item.name + ('/' if item.is_dir() else '')
        entries.append(f'  builtin-addons/ublock-origin/{target} (addon/{item.name}{suffix})')
    (directory / 'jar.mn').write_text('\n'.join(entries) + '\n')
    extensions = source / 'browser/extensions/moz.build'
    rule = '# Fire Axolotl unmodified uBlock Origin\nDIRS += ["ublock-origin"]\n'
    if rule not in extensions.read_text():
        extensions.write_text(extensions.read_text() + '\n' + rule)
    destination = source / 'browser/app/distribution/sources'
    destination.mkdir(exist_ok=True)
    shutil.copyfile(corresponding_source, destination / corresponding_source.name)
    shutil.copyfile(COMPONENT_CACHE / 'ublock-origin.json', destination / 'ublock-origin.json')
    with zipfile.ZipFile(xpi) as archive:
        (destination / 'uBlock-Origin-LICENSE.txt').write_bytes(archive.read('LICENSE.txt'))
    distribution = destination.parent / 'moz.build'
    rule = '\n# Fire Axolotl corresponding component source and license\nFINAL_TARGET_FILES.distribution.sources += [\n' + ''.join(f'    "sources/{name}",\n' for name in sorted((p.name for p in destination.iterdir()), key=str.lower)) + ']\n'
    current = distribution.read_text()
    begin = '# Fire Axolotl corresponding component source and license'
    if begin in current:
        current = re.sub(re.escape(begin) + r'[\s\S]*?\]\n', '', current)
    distribution.write_text(current.rstrip() + '\n' + rule)
    return {'id': UBLOCK_PIN['id'], 'version': UBLOCK_PIN['version'], 'sha256': sha256(xpi), 'corresponding_source_sha256': sha256(corresponding_source)}


def prepare(source):
    source = Path(source).resolve()
    pinned = json.loads((ROOT / 'upstream.json').read_text())
    actual = (source / 'browser/config/version_display.txt').read_text().strip()
    if actual != pinned['version']:
        raise ValueError(f'Expected Firefox {pinned["version"]}, found {actual}; review the overlay before updating')
    for patch_file in ['service-request-proxy.json', 'remote-app-family.json', 'windows-agent-policy.json']:
        patch = json.loads((ROOT / 'browser/native' / patch_file).read_text())
        replace_once(source / patch['file'], patch['old'], patch['new'])
    extension_dir = source / 'browser/extensions/aion'
    extension_dir.mkdir(exist_ok=True)
    package(extension_dir / 'aion@fire-axolotl.browser.xpi')
    shutil.copytree(ROOT / 'browser/extension', extension_dir / 'addon', dirs_exist_ok=True)
    (extension_dir / 'moz.build').write_text('JAR_MANIFESTS += ["jar.mn"]\n')
    jar = ['browser.jar:']
    for item in sorted((ROOT / 'browser/extension').iterdir()):
        if item.is_dir():
            jar.append(f'  builtin-addons/aion/{item.name}/ (addon/{item.name}/**)')
        else:
            jar.append(f'  builtin-addons/aion/{item.name} (addon/{item.name})')
    (extension_dir / 'jar.mn').write_text('\n'.join(jar) + '\n')
    extensions = source / 'browser/extensions/moz.build'
    text = extensions.read_text()
    if MARKER not in text:
        extensions.write_text(text + '\n' + MARKER)

    branding = source / 'browser/branding/fireaxolotl'
    if branding.exists():
        marker = branding / '.fire-axolotl-overlay'
        if not marker.is_file():
            raise ValueError('Existing custom branding directory has no overlay marker; refusing to replace it')
        shutil.rmtree(branding)
    shutil.copytree(source / 'browser/branding/unofficial', branding)
    (branding / '.fire-axolotl-overlay').write_text('Owned by scripts/prepare_source.py\n')
    (branding / 'configure.sh').write_text('MOZ_APP_DISPLAYNAME="Fire Axolotl"\nMOZ_MACBUNDLE_ID=org.fireaxolotl.browser\n')
    for path in [branding / 'locales/en-US/brand.ftl', branding / 'locales/en-US/brand.properties']:
        text = path.read_text().replace('Nightly', 'Fire Axolotl')
        text = text.replace('-brand-product-name = Firefox', '-brand-product-name = Fire Axolotl')
        text = text.replace('-vendor-short-name = Mozilla', '-vendor-short-name = Fire Axolotl')
        path.write_text(text)

    for size in [16, 32, 48, 64, 128]:
        shutil.copyfile(ROOT / f'branding/icon-{size}.png', branding / f'default{size}.png')
    for filename in ['firefox.ico', 'document.ico']:
        shutil.copyfile(ROOT / 'branding/aion.ico', branding / filename)
    prepare_windows_installer(source, branding)
    prepare_windows_installer_privacy(source)
    for filename in ['firefox.icns', 'document.icns']:
        if (branding / filename).exists():
            shutil.copyfile(ROOT / 'branding/aion.icns', branding / filename)
    content = branding / 'content'
    for filename in ['about.png', 'about-logo.png', 'about-logo@2x.png', 'about-logo-private.png', 'about-logo-private@2x.png']:
        shutil.copyfile(ROOT / 'branding/icon-256.png', content / filename)
    # Keep inherited asset filenames so upstream manifests remain valid.
    import base64
    encoded = base64.b64encode((ROOT / 'branding/icon-256.png').read_bytes()).decode()
    icon_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><image width="256" height="256" href="data:image/png;base64,{encoded}"/></svg>\n'
    for filename in ['about-logo.svg']:
        (content / filename).write_text(icon_svg)
    wordmark = '<svg xmlns="http://www.w3.org/2000/svg" width="310" height="60" viewBox="0 0 310 60"><text x="4" y="43" font-family="sans-serif" font-size="38" fill="context-fill">Fire Axolotl</text></svg>\n'
    for filename in ['about-wordmark.svg', 'firefox-wordmark.svg']:
        (content / filename).write_text(wordmark)
    for filename, size in [('VisualElements_150.png', 256), ('VisualElements_70.png', 128), ('PrivateBrowsing_150.png', 256), ('PrivateBrowsing_70.png', 128)]:
        shutil.copyfile(ROOT / f'branding/icon-{size}.png', branding / filename)

    (branding / 'pref/firefox-branding.js').write_text((ROOT / 'browser/preferences/fire-axolotl.js').read_text())
    replace_once(source / 'browser/moz.configure', 'imply_option("MOZ_APP_VENDOR", "Mozilla")', 'imply_option("MOZ_APP_VENDOR", "Fire Axolotl")')
    replace_once(source / 'browser/moz.configure', 'imply_option("MOZ_APP_ID", "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}")', 'imply_option("MOZ_APP_ID", "{75450dd9-387d-4289-8b23-7ad6609fa530}")')
    replace_app_startup_identity(source / 'browser/components/BrowserComponents.manifest')
    prefs = source / 'browser/components/preferences'
    shutil.copyfile(ROOT / 'browser/native/aion-layout.js', prefs / 'aion-layout.js')
    for locale in ['tr', 'en']:
        shutil.copyfile(ROOT / f'browser/extension/_locales/{locale}/messages.json', prefs / f'aion-{locale}.json')
    replace_once(prefs / 'jar.mn', '   content/browser/preferences/main.js\n', '   content/browser/preferences/main.js\n   content/browser/preferences/aion-layout.js\n   content/browser/preferences/aion-en.json\n   content/browser/preferences/aion-tr.json\n')
    # main.inc is an inert General-pane template in redesigned preferences.
    # Put our independently categorized group outside that legacy template.
    remove_legacy_preferences(prefs / 'main.inc.xhtml')
    replace_preferences_block(prefs / 'preferences.xhtml', (ROOT / 'browser/native/aion-layout.inc.xhtml').read_text(), '#include main.inc.xhtml')
    replace_once(prefs / 'preferences.xhtml', '  <script src="chrome://browser/content/preferences/preferences.js"/>', '  <script src="chrome://browser/content/preferences/preferences.js"/>\n  <script src="chrome://browser/content/preferences/aion-layout.js"/>')
    base = source / 'browser/base'
    for filename in ['aion-chrome.js', 'aion-chrome.css']:
        shutil.copyfile(ROOT / 'browser/native' / filename, base / 'content' / filename)
    shutil.copytree(ROOT / 'browser/extension/fonts', base / 'content/aion-fonts', dirs_exist_ok=True)
    entries = '\n'.join(['        content/browser/aion-chrome.js (content/aion-chrome.js)', '        content/browser/aion-chrome.css (content/aion-chrome.css)', '        content/browser/aion-fonts/ (content/aion-fonts/**)'])
    replace_once(base / 'jar.mn', 'browser.jar:\n', 'browser.jar:\n' + entries + '\n')
    chrome_assets = '  <link rel="stylesheet" href="chrome://browser/content/aion-chrome.css"/>\n  <script src="chrome://browser/content/aion-chrome.js"/>\n'
    replace_once(base / 'content/browser.xhtml', '</head>', chrome_assets + '</head>')
    replace_once(prefs / 'preferences.xhtml', '</head>', chrome_assets + '</head>')
    nsi = branding / 'branding.nsi'
    nsi.write_text(nsi.read_text().replace('Mozilla Developer Preview', 'Fire Axolotl').replace('"mozilla.org"', '"Fire Axolotl"'))
    (source / '.mozconfig').write_text((ROOT / 'browser/mozconfig').read_text())
    distribution = source / 'browser/app/distribution'
    shutil.copyfile(ROOT / 'browser/policies.json', distribution / 'policies.json')
    policy_rule = '\n# Fire Axolotl privacy defaults\nFINAL_TARGET_FILES.distribution += ["policies.json"]\n'
    build_file = distribution / 'moz.build'
    text = build_file.read_text()
    if policy_rule not in text:
        build_file.write_text(text + policy_rule)
    # Upstream only packages distribution/* for BUILT_BY_MOZILLA. Our native
    # runtime directory is not enough: retain privacy policy and corresponding
    # source in independent installer archives as well.
    package_manifest = source / 'browser/installer/package-manifest.in'
    package_rule = '\n; Fire Axolotl policy and corresponding component source\n@RESPATH@/distribution/policies.json\n@RESPATH@/distribution/sources/*\n'
    if package_rule not in package_manifest.read_text():
        package_manifest.write_text(package_manifest.read_text() + package_rule)
    ublock = embed_ublock(source)
    receipt = {'upstream': pinned, 'overlay_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'overlay_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()), 'companion_sha256': hashlib.sha256((extension_dir / 'aion@fire-axolotl.browser.xpi').read_bytes()).hexdigest(), 'components': {'ublock-origin': ublock}, 'status': 'source-prepared-not-built'}
    (source / 'fire-axolotl-build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Prepared {source}; this is not a compiled browser')
    return source


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    prepare(parser.parse_args().source)
