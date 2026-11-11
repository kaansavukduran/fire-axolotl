# SPDX-License-Identifier: MPL-2.0
"""Collect tested installers, complete source and user-facing release instructions."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
CONFIG = json.loads((ROOT / 'release.json').read_text())


def main():
    incoming = ROOT / 'work/release-inputs'
    for path in incoming.iterdir():
        if path.is_file():
            shutil.copyfile(path, DIST / path.name)
    release_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    version = CONFIG['version']
    upstream = json.loads((ROOT / 'upstream.json').read_text())['version']
    source = DIST / f'fire-axolotl-{version}-packaging-source.zip'
    subprocess.run(['git', 'archive', '--format=zip', '--prefix=fire-axolotl/', f'--output={source}', release_commit], cwd=ROOT, check=True)
    files = {}
    for path in sorted(DIST.iterdir()):
        if path.is_file() and not path.name.endswith('.sha256'):
            with path.open('rb') as stream:
                files[path.name] = {'sha256': hashlib.file_digest(stream, 'sha256').hexdigest(), 'bytes': path.stat().st_size}
    evidence = {'browser_source_commit': CONFIG['source_commit'], 'packaging_commit': release_commit, 'native_run': CONFIG['native_run_id'], 'release_workflow_run': os.environ.get('GITHUB_RUN_ID'), 'files': files, 'checks': {}}
    for name, path in {'appimage': 'work/installer-test-artifacts/results.json', 'installed_browser': 'work/installed-native-test-artifacts/results.json', 'installed_restart': 'work/native-test-artifacts/restart-results.json', 'integration': 'work/native-e2e-artifacts/results.json', 'game': 'work/runner-test-artifacts/results.json', 'languages': 'work/localization-test-artifacts/results.json'}.items():
        evidence['checks'][name] = json.loads((ROOT / path).read_text())
    if len(evidence['checks']['appimage']['passed']) < 4 or len(evidence['checks']['installed_browser']['passed']) < 11 or len(evidence['checks']['installed_restart']['passed']) < 4:
        raise ValueError('Installer validation is incomplete')
    checks = evidence['checks']
    checks['network'] = json.loads((ROOT / 'work/network-test-artifacts/results.json').read_text())
    if not checks['network']['passed'] or not checks['network']['log_canary_verified'] or checks['network']['forbidden_hosts']:
        raise ValueError('Installed default-network sampling failed or lacked a real local HTTP canary')
    if checks['integration']['mode'] != 'compiled-fork' or len(checks['integration']['passed']) < 34 or checks['game']['mode'] != 'compiled-fork-normal-newtab' or len(checks['game']['passed']) < 11 or not checks['game'].get('full_game') or not checks['game'].get('offline_first_launch_verified') or not checks['game'].get('isolated_principal_verified') or checks['languages']['mode'] != 'compiled-fork-native-languages' or len(checks['languages']['passed']) < 10:
        raise ValueError('Installed integration, game or native-language validation is incomplete')
    checks['tools_workspace'] = json.loads((ROOT / 'work/tools-test-artifacts/results.json').read_text(encoding='utf-8'))
    checks['native_translation'] = json.loads((ROOT / 'work/translation-test-artifacts/results.json').read_text(encoding='utf-8'))
    if len(checks['tools_workspace']['passed']) < 9 or not checks['native_translation']['passed'] or not checks['native_translation'].get('offline_inference_verified'):
        raise ValueError('Actual tools UI or native offline translation verification is incomplete')
    checks['newtab_workspace'] = json.loads((ROOT / 'work/newtab-test-artifacts/results.json').read_text(encoding='utf-8'))
    checks['external_game'] = json.loads((ROOT / 'work/game-link-verification.json').read_text())
    if len(checks['newtab_workspace']['passed']) < 9 or checks['external_game']['url'] != 'https://aionendlessrun.vercel.app/' or not checks['external_game']['tls_verification']:
        raise ValueError('New-tab UX and current official game link must pass')
    (DIST / 'release-manifest.json').write_text(json.dumps(evidence, indent=2) + '\n')
    notes = f'''Fire Axolotl 0.4.0 geliştirici önizlemesi / developer preview

**Bu kararlı günlük kullanım sürümü değildir. Otomatik güncellemeler kapalıdır.**
**Not a stable daily-use release. Automatic updates are disabled.**

Aion0.4: Aion Endless Run 0.12.0 tam oyun tarayıcının içindedir (Vercel build 7967f676d171a832). Oyunu başlat’a tıkla; ilk açılışta bile internet gerekmez. Oyunun kendi menüsü, dört karakteri, ayarları ve kayıtları vardır. Gizle düğmesi kaldırıldı; Görünüm tercihi ve geri getirme seçeneği korundu. Tam ekran düğmesi var. Oyun tarayıcı verisi izni olmayan ayrı bir yerleşik bileşende çalışır ve güncellemeleri tarayıcı paketleriyle gelir.

Önceki0.2:760px araç paneli, üç görev bölümü ve tam sekmede çalışma alanı; oturumluk metin taslağı; sağ tık konteyner/çeviri seçenekleri. Firefox'un yerel çeviri aracını açan düğme; gerçek EN→TR çeviri ve model yüklendikten sonra çevrimdışı tekrar doğrulandı. Ayrı sohbet modeli veya önceden indirilmiş çeviri modeli paketlenmez.

Gerçek Firefox ESR {upstream} derlemesi; ayrı Fire Axolotl kimliği ve profili. Varsayılan koyu görünüm ve üst sekmeler; isteğe bağlı sol/sağ sekmeler, yerleşik Aion/uBlock Origin, konteynerler, video araçları ve yerel karakterler. Ana tarayıcı resmî 103 masaüstü dilini içerir; normal dil seçicisi, Almanca/Japonca/Arapça ve sağdan sola arayüz dahil 10 dil/yeniden başlatma senaryosu geçti. Aion araçlarının ve yeni sekme oyununun dil seçimi ayrıdır.

| Platform | İndirme / Download | Durum / Status |
| --- | --- | --- |
| Linux x86_64 | `fire-axolotl-{version}-linux-x86_64.AppImage` | Ubuntu 24.04 test hedefi; GTK/masaüstü kitaplıkları gerekir. / Tested target: Ubuntu 24.04 with desktop libraries. |
| Ubuntu 24.04 amd64 | `fire-axolotl-{version}-linux-amd64.deb` | Gerçek paket kurulumu, ilk açılış ve yeniden başlatma test edildi. / Actual installation and 70 installed-browser scenarios tested. |
| Windows x64 | [Ayrı Windows sürümleri](https://github.com/{CONFIG["repository"]}/releases) | Bu Linux paketi Windows kurulumu değildir. Eski 153.6 motoru güncel güvenlik sürümü sayılmaz. |
| macOS | Henüz yok / Not available | Mac derlemesi, Developer ID ve notarization bekliyor. |
| Android | Henüz yok / Not available | Mobil ön yüz ve imzalı APK bekliyor. |
| iPhone | Henüz yok / Not available | iOS ön yüz, Apple hesabı ve TestFlight/App Store akışı bekliyor. |

### Linux AppImage

AppImage'i indir. İndirilen dosyanın bulunduğu klasörde sağ tıkla, **Terminalde aç** seçeneğini seç ve çalıştır:

```sh
chmod +x fire-axolotl-{version}-linux-x86_64.AppImage
./fire-axolotl-{version}-linux-x86_64.AppImage
```

FUSE kullanılamıyorsa / If FUSE is unavailable:

```sh
APPIMAGE_EXTRACT_AND_RUN=1 ./fire-axolotl-{version}-linux-x86_64.AppImage
```

### Ubuntu .deb

`.deb` dosyasını indir, aynı klasörde terminali aç ve kur:

```sh
sudo apt install ./fire-axolotl-{version}-linux-amd64.deb
fire-axolotl-preview
```

Başarı kontrolü: pencere Fire Axolotl adıyla açılmalı; yeni profilde sekmeler üstte olmalı ve Aion araç çubuğundan açılabilmeli. Ayarlar → Görünüm yerel sekme/font kontrollerini içerir. Aion ayarlarında Türkçe/İngilizce seçilebilir.

Verify that Fire Axolotl opens with top tabs and a working Aion toolbar action. Use a new Fire Axolotl profile; do not point this preview at a personal Firefox profile. Close open work before manually changing packages. Package checksums provide integrity information; a project-signed automatic update channel is not implemented.

Yeni sekmede tam Aion Endless Run: Oyunu başlat, sonra oyunun kendi menüsünü kullan. Dil/ses/hareket/kayıtlar oyunun ayarlarından yönetilir. Eski mini oyun rekoru profilde silinmeden saklanır. Native Settings and the game passed installed-browser tests; no temporary add-on is required.

### Kaynaklar ve doğrulama / Source and validation

Tam uygulanmış motor kaynağı `fire-axolotl-applied-source.tar.zst`; launcher/paketleme kaynakları `fire-axolotl-{version}-packaging-source.zip`; AppImage runtime, LGPL FUSE kaynağı ve derleme/yine bağlama betikleri `fire-axolotl-{version}-appimage-support-source.tar.gz` içindedir. uBO'nun ilgili kaynakları ve GPL bildirimi ayrıca tarayıcının `distribution/sources` dizinindedir. Ek dil verileri `native-ui-overlay.json` içinde tek tek özetlenir. Motorun derlendiği ham kaynak arşivine ek olarak `fire-axolotl-localization-source.zip`, 102 özgün XPI, MPL lisansı, katalog pinleri ve türetme betiklerini içerir; native çalıştırılabilir dosyalar değiştirilmez. Bileşen lisansları korunur.

Complete applied engine source, separate packaging/launcher source, and AppImage runtime/library source materials accompany the binaries. Runtime/library notices are embedded in both Linux packages. `SHA256SUMS` and `release-manifest.json` record sizes, digests and test evidence. `sha256sum -c SHA256SUMS --ignore-missing` checks the files downloaded into the same directory.

Browser source: `{CONFIG['source_commit']}`. Packaging source: `{release_commit}`. [Successful native build and 11 startup + 34 integration + 4 restart checks](https://github.com/{CONFIG['repository']}/actions/runs/{CONFIG['native_run_id']}). Installer first launch and persistence were checked separately before this publication.

The built-in release check follows the stable channel; use the Releases page for manual preview downloads. Signed updates, full localization of new Aion strings, real-account Sync, live Netflix/DRM/quality adapters and other mapped features remain incomplete. See [the feature map](https://github.com/{CONFIG['repository']}/blob/{release_commit}/docs/FEATURES.md) and [requirements](https://github.com/{CONFIG['repository']}/blob/{release_commit}/docs/ROADMAP.md). No universal quality-forcing or malware-immunity claim is made. Fire Axolotl is independent of Mozilla.
'''
    (DIST / 'RELEASE-NOTES.md').write_text(notes)
    (DIST / 'SHA256SUMS').write_text(''.join(f'{hashlib.file_digest(path.open("rb"), "sha256").hexdigest()}  {path.name}\n' for path in sorted(DIST.iterdir()) if path.is_file() and path.name != 'SHA256SUMS'))
    print('Complete tested preview assembled at', release_commit)


if __name__ == '__main__':
    main()
