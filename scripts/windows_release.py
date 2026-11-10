# SPDX-License-Identifier: MPL-2.0
"""Validate the compiled Windows artifacts and publish a tested offline installer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

from verify_native_package import verify
from runner_overlay import check_source_delta, windows_archive
from localization import source_archive
from windows_runtime import augment as augment_windows_runtime

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'windows-release.json').read_text())
DIST = ROOT / 'dist/windows-release'
STEM = f'fire-axolotl-{CONFIG["version"]}-windows-x86_64'


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True, cwd=ROOT).strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def preflight():
    # Recheck immediately before both packaging and publication. A green build
    # from an older ESR must not become a newly recommended download.
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_upstream.py')], check=True)
    run = json.loads(gh('api', f'repos/{CONFIG["repository"]}/actions/runs/{CONFIG["native_run_id"]}'))
    expected = {'status': 'completed', 'conclusion': 'success', 'head_branch': 'main', 'head_sha': CONFIG.get('validation_commit', CONFIG['source_commit']), 'workflow_id': CONFIG['native_workflow_id'], 'path': CONFIG.get('native_workflow_path', '.github/workflows/native-windows.yml')}
    if run.get('event') not in {'workflow_dispatch', 'push'} or any(run.get(key) != value for key, value in expected.items()) or run['repository']['id'] != CONFIG['repository_id'] or run['head_repository']['id'] != CONFIG['repository_id']:
        raise ValueError('The reviewed successful Windows source build is required')
    if os.environ.get('GITHUB_EVENT_NAME') == 'workflow_run':
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        if event['workflow_run']['id'] != CONFIG['native_run_id']:
            raise ValueError('This completion event belongs to a different build')
    print('Successful reviewed Windows build provenance verified')


def inputs():
    frontend_delta = check_source_delta(CONFIG['source_commit'])
    incoming = ROOT / 'work/windows-inputs'
    zips = []
    for path in incoming.rglob('fire-axolotl-*.zip'):
        with zipfile.ZipFile(path) as archive:
            if any(name.endswith('/application.ini') for name in archive.namelist()):
                zips.append(path)
    installers = list(incoming.rglob('*.installer.exe'))
    if len(zips) != 1 or len(installers) != 1:
        raise ValueError('Expected one native Windows ZIP and one real full installer')
    DIST.mkdir(parents=True, exist_ok=True)
    native = DIST / f'{STEM}.zip'
    shutil.copyfile(zips[0], native)
    report = verify(native)
    setup = DIST / f'{STEM}-Setup.exe'
    shutil.copyfile(installers[0], setup)
    if setup.stat().st_size < 50_000_000 or setup.open('rb').read(2) != b'MZ':
        raise ValueError('Expected the full offline Windows installer')
    expected = json.loads((ROOT / 'upstream.json').read_text())
    source = incoming / 'fire-axolotl-windows-applied-source.tar.zst'
    parts = Path(str(source) + '.sha256').read_text().split()
    if source.stat().st_size < 100_000_000 or parts != [digest(source), source.name]:
        raise ValueError('Full corresponding Windows source/checksum missing')
    import zstandard
    receipt = None
    with source.open('rb') as raw, zstandard.ZstdDecompressor().stream_reader(raw) as stream:
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for member in archive:
                if member.name.removeprefix('./') == 'fire-axolotl-build.json':
                    receipt = json.load(archive.extractfile(member))
                    break
    if not receipt or receipt['overlay_commit'] != CONFIG['source_commit'] or receipt['overlay_dirty'] or receipt['upstream'] != expected:
        raise ValueError('Applied source does not match the reviewed native build')
    evidence = ROOT / 'work/windows-evidence'
    if 'engine_run_id' in CONFIG:
        validation = json.loads((evidence / 'native-test-artifacts/validation-inputs.json').read_text())
        expected = {'engine_run_id': CONFIG['engine_run_id'], 'source_commit': CONFIG['source_commit'], 'validation_commit': CONFIG['validation_commit'], 'native_zip_sha256': digest(zips[0]), 'installer_sha256': digest(installers[0]), 'source_sha256': digest(source), 'engine_inputs_unchanged': True}
        if validation != expected:
            raise ValueError('Native revalidation evidence does not match these exact preserved packages')
    checks = {key: json.loads((evidence / path).read_text()) for key, path in {'native': 'native-test-artifacts/results.json', 'restart': 'native-test-artifacts/restart-results.json', 'integration': 'native-e2e-artifacts/results.json'}.items()}
    validate_checks(checks)
    runtime = augment_windows_runtime(native)
    (DIST / 'windows-runtime-build.json').write_text(json.dumps(runtime, indent=2) + '\n')
    overlay = windows_archive(native)
    overlay['source_delta'] = frontend_delta
    overlay['overlay_commit'] = gh('api', f'repos/{CONFIG["repository"]}/git/commits/{os.environ["GITHUB_SHA"]}', '--jq', '.sha')
    report = verify(native)
    (DIST / 'newtab-ui-overlay.json').write_text(json.dumps(overlay, indent=2) + '\n')
    source_archive(native, DIST / 'fire-axolotl-localization-source.zip', overlay['localizations'])
    shutil.copyfile(source, DIST / source.name)
    (DIST / 'native-build-validation.json').write_text(json.dumps({'source_commit': CONFIG['source_commit'], 'native_run': CONFIG['native_run_id'], 'source_sha256': digest(source), 'package': report, 'checks': checks}, indent=2) + '\n')
    print('Native x64 payload, full source and compiled-fork evidence verified')


def validate_checks(checks):
    if (len(checks['native']['passed']) < 11 or len(checks['restart']['passed']) < 4
            or len(checks['integration']['passed']) < 34 or checks['integration']['mode'] != 'compiled-fork'
            or checks['native']['identity']['id'] != '{75450dd9-387d-4289-8b23-7ad6609fa530}'):
        raise ValueError('Required native Windows checks did not pass')


def assemble():
    checks = {key: json.loads((ROOT / path).read_text()) for key, path in {'native': 'work/installed-windows-test-artifacts/results.json', 'restart': 'work/native-test-artifacts/restart-results.json', 'integration': 'work/native-e2e-artifacts/results.json'}.items()}
    validate_checks(checks)
    installer = json.loads((ROOT / 'work/windows-installer-test/installation.json').read_text())
    uninstall = json.loads((ROOT / 'work/windows-installer-test/uninstallation.json').read_text())
    sfx = json.loads((DIST / 'windows-sfx-build.json').read_text())
    runtime = json.loads((DIST / 'windows-runtime-build.json').read_text())
    game = json.loads((ROOT / 'work/runner-test-artifacts/results.json').read_text())
    overlay = json.loads((DIST / 'newtab-ui-overlay.json').read_text())
    languages = json.loads((ROOT / 'work/localization-test-artifacts/results.json').read_text(encoding='utf-8'))
    if languages['mode'] != 'compiled-fork-native-languages' or len(languages['passed']) < 5:
        raise ValueError('Installed-browser native language and persistence checks missing')
    profile = json.loads((ROOT / 'work/windows-installer-test/profile-probe.json').read_text())
    fallback = json.loads((ROOT / 'work/windows-installer-test/runtime-fallback.json').read_text())
    if len(profile.get('verified_crt_modules', {})) != 3 or not runtime['crt_imports'] or not all(fallback.get(key) for key in ['local_crt_fallback_verified', 'core_library_loaded', 'prefer_system32_mitigation_enabled', 'probe_has_no_dynamic_crt_imports']):
        raise ValueError('Actual application-local Windows runtime loading was not verified')
    setup = DIST / f'{STEM}-Setup.exe'
    if sfx['frontend_zip_sha256'] != overlay['native_zip_sha256'] or not sfx['inner_nsis_preserved'] or sfx['installer_sha256'] != digest(setup) or sfx['icon_sha256'] != digest(ROOT / 'branding/aion.ico'):
        raise ValueError('Original-brand installer wrapper verification missing')
    if game['mode'] != 'compiled-fork-normal-newtab' or len(game['passed']) < 11:
        raise ValueError('Installed-browser new-tab game checks missing')
    if not installer['payload_verified'] or not uninstall['profiles_preserved'] or not uninstall['default_browser_preserved']:
        raise ValueError('Clean installation/uninstallation data protection not verified')
    commit = gh('api', f'repos/{CONFIG["repository"]}/git/commits/{os.environ["GITHUB_SHA"]}', '--jq', '.sha')
    subprocess.run(['git', 'archive', '--format=zip', '--prefix=fire-axolotl/', f'--output={DIST / (STEM + "-packaging-source.zip")}', commit], cwd=ROOT, check=True)
    (DIST / 'release-manifest.json').write_text(json.dumps({'browser_source_commit': CONFIG['source_commit'], 'packaging_commit': commit, 'native_run': CONFIG['native_run_id'], 'installer_run': os.environ['GITHUB_RUN_ID'], 'authenticode_signed': False, 'automatic_updates': False, 'checks': checks, 'installation': installer, 'uninstallation': uninstall, 'installer_wrapper': sfx, 'ui_overlay': overlay, 'newtab_game': game, 'native_languages': languages, 'windows_runtime': runtime, 'profile_probe': profile, 'runtime_fallback_probe': fallback}, indent=2) + '\n')
    notes = f'''Fire Axolotl Windows x64 geliştirici ön sürümü / developer preview

**Kararlı günlük kullanım sürümü değildir. Windows Authenticode imzası ve otomatik güncelleme henüz yoktur.**
**Not a stable daily-use release. No Windows Authenticode signature or automatic updater yet.**

Bu sürüm Firefox ESR 153.7.0esr motoruna günceller ve ilk Windows ön sürümündeki eksik Visual C++ runtime bağımlılığını giderir. Sabit sürüm/özet ve geçerli Microsoft imzaları doğrulanan x64 CRT dosyaları uygulama klasöründedir. Statik CRT kullanan bağımsız bir yükleyici, gerçek xul.dll dosyasının paket içindeki CRT kopyalarıyla yüklenebildiğini doğrular. Normal tarayıcının uyumlu, daha yeni System32 kopyasını tercih eden Firefox güvenlik ilkesi korunur ve yüklediği Microsoft modülleri ayrıca denetlenir. Sistem runtime'ını değiştirmez. Lisans/atıflar `distribution/sources/windows-runtime/` ve `about:license` içindedir.

This correction includes the unmodified, hash-pinned Microsoft x64 CRT alongside the application. Its Microsoft signatures, native PE import closure and actual loaded module paths are checked. A static-CRT probe loads the real xul.dll using the bundled dynamic CRT copies with PreferSystem32 enabled; normal Firefox may prefer a compatible newer signed system copy. The original preview required a preinstalled runtime; this package includes the required files locally. These Windows components have their own Microsoft redistribution terms and are not MPL source code.

### Windows'ta kurulum / Install on Windows

1. Aşağıdaki dosyalardan `{STEM}-Setup.exe` dosyasını indir. ZIP veya kaynak arşivleri kurulum için gerekli değildir.
2. İndirilenler klasörünü aç ve Setup.exe'ye çift tıkla. Fire Axolotl kurulum sihirbazındaki adımları izle.
3. Başlat menüsünde **Fire Axolotl** yazıp tarayıcıyı aç. Yeni profilde sekmeler üstte ve tarayıcı koyu temada açılmalı. Araç çubuğundaki Aion düğmesi yerleşik araçları açar.
4. Ayarlar → Görünüm sekme konumu ve arayüz fontunu içerir. Aion ayarlarında Türkçe/English seçilebilir. Ana tarayıcı Türkçe/English içerir; native Ayarlar ekranından seçilen dil yeniden başlatmada korunur.

Download and double-click the Setup.exe, follow the native installer, then open Fire Axolotl from Start. Fresh profiles use top tabs and dark chrome. Aion and uBlock Origin are built in. Native Settings switches main chrome between Turkish and English; Aion tools and game language remain independent choices.

Yeni sekmede **Aion Koşusu**: Başlat → oyun alanında Boşluk ile zıpla, Esc ile duraklat. Buzda donma ve ateşte çizgi film tarzı kül animasyonları vardır. Oyun çevrimdışı çalışır; rekor bu cihazda tutulur. Ayarlar → Görünüm’den gizle/göster, Türkçe/English seç veya rekoru sıfırla. Arama ve kısayollar korunur. Yeni sekmeyi değiştiren başka bir eklenti seçersen onun sayfası kullanılır.

**Aion Run** is an original offline pixel-art new-tab game. Press Start, focus the play area, then Space to jump or Esc to pause. Switching tabs pauses gameplay. Settings → Appearance controls visibility, Turkish/English and the local record.

Windows, imzasız geliştirici paketi için tanınmayan yayımcı/SmartScreen bildirimi gösterebilir. Güvenlik korumalarını kapatma. Bu ön sürümün Authenticode imzası yoktur; SHA-256 özeti dosya bütünlüğünü denetler, yayımcı imzasının yerine geçmez. Windows may identify this unsigned developer build as an unknown publisher. Keep security protections enabled. Checksums verify integrity, not publisher signing.

Kurulum mevcut Firefox'un yerine geçmez ve Firefox profilini kullanmaz. Kaldırma testi örnek profil verisini korudu. Kişisel Firefox profilini bu ön sürüme elle yönlendirme. Güncelleme elle yapılır; tarayıcıdaki kararlı kanal denetimi bu ön sürümü otomatik kurmaz.

| Platform | Durum / Status |
| --- | --- |
| Windows x64, Windows 10+ | Bu Setup.exe; temiz kurulum ve ilk açılış Windows Server 2022 CI üzerinde doğrulandı. / Installer/startup validated on Windows Server 2022. Human Windows 10/11 accessibility and SmartScreen review remains pending. |
| Windows ARM64 | Henüz yok / Not available |
| Linux x86_64 | [Önceki AppImage ve Ubuntu .deb sürümü](https://github.com/{CONFIG['repository']}/releases/tag/v0.1.0-dev.20261109) |
| macOS | Henüz yok / Not available |
| Android | Henüz yok / Not available |
| iPhone | Henüz yok / Not available |

### Kaynak ve doğrulama / Source and validation

Tam uygulanmış Windows motor kaynağı `fire-axolotl-windows-applied-source.tar.zst`; paketleme kaynakları `*-packaging-source.zip`; lisanslar native tarayıcıda `about:license` ve `distribution/sources` içindedir. `SHA256SUMS` bütün indirilebilir dosyaların özetlerini içerir. PowerShell'de `Get-FileHash .\\{STEM}-Setup.exe -Algorithm SHA256` çıktısını karşılaştırabilirsin.

Tam derleme sonrası ve kurulu tarayıcı üzerinde 11 açılış, 4 yeniden başlatma ve 34 entegrasyon senaryosu geçti. Temiz kurulum/kaldırmada profil ve varsayılan tarayıcı tercihinin korunması ayrıca denetlendi. TLS, kum havuzu, eklenti imzaları ve Windows güvenlik korumaları kapatılmadı.

Native source: `{CONFIG['source_commit']}`. Packaging source: `{commit}`. [Native Windows build](https://github.com/{CONFIG['repository']}/actions/runs/{CONFIG['native_run_id']}). [Installed-browser validation](https://github.com/{CONFIG['repository']}/actions/runs/{os.environ['GITHUB_RUN_ID']}).

Yeni sekme arayüzü, aynı derlenmiş motorun `browser/omni.ja` kaynaklarına uygulanmış incelenebilir veri katmanıdır. `newtab-ui-overlay.json` değişen her kaynak özetini ve değişmeden kalan native dosya sayısını kaydeder; tercih edilen kaynak ve yeniden üretme betikleri `*-packaging-source.zip` içindedir. Motor kaynağını açıp bu paketin `scripts/prepare_source.py` betiğini uygulayarak kaynak derlemesi yapılabilir. SFX kaynakları `windows-sfx-corresponding-source.zip` içindedir. Native executables, engine, policies, Aion and signed uBlock Origin are preserved. Pinned Turkish language data, its catalog entry and the OS-language default are added. Five installed native-language/persistence checks and the game checks gate publication. `fire-axolotl-localization-source.zip` includes original translations, MPL license, derivation recipe, pins and branding. The modified built-in does not retain Mozilla signature files; external language-package signature checks remain enabled.

Signed updates, complete locales, actual account Sync, live DRM/Netflix quality adapters and other [feature-map gaps](https://github.com/{CONFIG['repository']}/blob/{commit}/docs/FEATURES.md) remain incomplete. No malware-immunity or universal resolution-forcing claim. Fire Axolotl is independent of Mozilla; third-party licenses are preserved.
'''
    (DIST / 'RELEASE-NOTES.md').write_text(notes, encoding='utf-8')
    (DIST / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(DIST.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'))
    print('Tested Windows release assembled')


def publish():
    if os.environ.get('GITHUB_REPOSITORY') != CONFIG['repository'] or os.environ.get('GITHUB_REF_NAME') != 'main' or os.environ.get('GITHUB_EVENT_NAME') not in {'workflow_dispatch', 'workflow_run'}:
        raise ValueError('Only the reviewed main-branch release workflow may publish')
    preflight()
    manifest = json.loads((DIST / 'release-manifest.json').read_text())
    if manifest['browser_source_commit'] != CONFIG['source_commit'] or manifest['packaging_commit'] != os.environ['GITHUB_SHA']:
        raise ValueError('Release source provenance mismatch')
    expected = {}
    for line in (DIST / 'SHA256SUMS').read_text().splitlines():
        sha, name = line.split()
        if Path(name).name != name or name in expected or digest(DIST / name) != sha:
            raise ValueError('Invalid release checksum manifest')
        expected[name] = sha
    expected['SHA256SUMS'] = digest(DIST / 'SHA256SUMS')
    if set(expected) != {p.name for p in DIST.iterdir() if p.is_file()}:
        raise ValueError('Release file list mismatch')
    repo, tag = CONFIG['repository'], CONFIG['tag']
    releases = json.loads(gh('api', f'repos/{repo}/releases?per_page=100'))
    release = next((r for r in releases if r['tag_name'] == tag), None)
    if release and (not release['draft'] or release['target_commitish'] != os.environ['GITHUB_SHA']):
        raise ValueError('Preserve the existing release; do not overwrite it')
    if not release:
        # Use the creation response directly: the collection can briefly lag
        # behind a newly created draft and must not decide its identity.
        request = ROOT / 'work/release-draft-create.json'
        request.parent.mkdir(parents=True, exist_ok=True)
        request.write_text(json.dumps({'tag_name': tag, 'target_commitish': os.environ['GITHUB_SHA'], 'draft': True, 'prerelease': True, 'name': 'Fire Axolotl 0.1.0 · Windows x64 geliştirici ön sürümü', 'body': (DIST / 'RELEASE-NOTES.md').read_text(encoding='utf-8')}, ensure_ascii=False), encoding='utf-8')
        release = json.loads(gh('api', f'repos/{repo}/releases', '--method', 'POST', '--input', str(request)))
    present = {a['name']: a for a in release['assets']}
    for name, asset in present.items():
        if name not in expected or asset.get('digest') != 'sha256:' + expected[name]:
            raise ValueError('Existing draft asset differs; refusing to replace it')
    for path in sorted(DIST.iterdir(), key=lambda p: p.stat().st_size, reverse=True):
        if path.name not in present:
            gh('release', 'upload', tag, str(path), '--repo', repo)
    result = json.loads(gh('api', f'repos/{repo}/releases/{release["id"]}'))
    if {a['name'] for a in result['assets']} != set(expected) or any(a.get('digest') != 'sha256:' + expected[a['name']] for a in result['assets']):
        raise ValueError('Release upload incomplete or corrupt; keep the draft unpublished')
    gh('release', 'edit', tag, '--repo', repo, '--prerelease', '--latest=false', '--draft=false')
    result = json.loads(gh('api', f'repos/{repo}/releases/{release["id"]}'))
    if result['draft'] or not result['prerelease']:
        raise ValueError('Incorrect publication state')
    print(result['html_url'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preflight', 'inputs', 'assemble', 'publish'])
    globals()[parser.parse_args().mode]()
