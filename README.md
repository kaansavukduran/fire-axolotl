# Fire Axolotl

<img src="branding/icon-256.png" width="128" height="128" alt="AI-generated Aion axolotl icon">

**Daha az eklenti, daha fazla kontrol. / Fewer extensions, more control.**

Firefox ESR kaynak kodunu temel alan, Aion karakteriyle kişiselleştirilen ücretsiz bir tarayıcı projesi. Fire Axolotl, Mozilla veya ürünleriyle resmi olarak bağlantılı değildir. Firefox, Mozilla Foundation'ın ticari markasıdır.

Free browser project based on Firefox ESR source, with an Aion companion. Fire Axolotl is not officially associated with Mozilla or its products. Firefox is a trademark of the Mozilla Foundation.

**Durum / Status: geliştirici önizlemesi, henüz günlük kullanım için dağıtılan bir tarayıcı değil. / Developer preview, not a released browser for everyday use.**

Bu depo; doğrulanmış Firefox kaynağını indiren derleme katmanını, özgün markalamayı, yerleşik Aion modülünü ve sekme konumu için yerel ayarları içerir. Motorun tüm geçmişini bu küçük depoya kopyalamak yerine kaynak sürümü ve SHA-512 özeti `upstream.json` içinde sabitlenir. Gömülü modül tarayıcı derlenirken paketlenir; son kullanıcının ayrı eklenti kurması hedeflenmez. Geliştirme sırasında aynı modül geçici eklenti olarak denenebilir.

This repository contains a pinned Firefox source build overlay, original branding, the built-in Aion module, and native tab-layout settings. The upstream version and SHA-512 are locked in `upstream.json`; the complete engine history is not duplicated here. The companion is embedded at browser build time. A temporary add-on package is available for development, not as a browser installer.

## Bu aşamada eklenenler / Implemented in this stage

- Kalıcı ve son sekme kapanınca temizlenen geçici konteynerler. / Persistent and temporary containers cleaned up after their last tab closes.
- Video hızını 0,25×–4× ayarlama, gerçek video çözünürlüğünü okuma. / 0.25×–4× video speed and actual decoded resolution.
- YouTube için deneysel kalite isteği; her sitede ve her abonelikte kalite garantisi değildir. / Experimental YouTube quality requests; no universal resolution guarantee.
- Yerel VTT/SRT dosyalarından çift altyazı, mevcut altyazı satırını alma. / Dual local VTT/SRT captions and current cue capture.
- Açık kullanıcı eylemiyle seçili metin çevirisi; isteğe bağlı, kullanıcının seçtiği HTTPS hizmeti. / Explicit selected-text translation through an optional user-chosen HTTPS service.
- Türkçe/İngilizce Aion arayüzü, dört tema, %80–%200 arayüz ölçeği, bağımsız yazı boyutu ve Lexend. / Turkish/English Aion UI, four themes, 80%–200% interface scale, independent text size and Lexend.
- JSON yedekleme/geri yükleme, isteğe bağlı üç gerçek eyleme dayalı keşif ilerlemesi. / JSON backup/restore and optional milestones based on three real actions.
- Kaynak katmanında üst/sol/sağ sekme konumu seçimi. / Native top/left/right tab layout in the source overlay.

İstenen eklentilerin tek tek kapsamı ve eksikleri: [Özellik eşlemesi / Feature map](docs/FEATURES.md).

## Geliştirici önizlemesini dene / Try the developer companion

Python 3.12 ve Node.js 22 veya daha yenisi gerekir. / Requires Python 3.12 and Node.js 22 or newer.

```sh
git clone https://github.com/kaansavukduran/fire-axolotl.git
cd fire-axolotl
npm run check
npm test
npm run package
```

1. Güncel Firefox'u aç. / Open an up-to-date Firefox installation.
2. Adres çubuğuna `about:debugging#/runtime/this-firefox` yaz. / Enter `about:debugging#/runtime/this-firefox` in the address bar.
3. **Geçici Eklenti Yükle / Load Temporary Add-on** düğmesine bas.
4. `dist/fire-axolotl-0.1.0-developer-addon.xpi` dosyasını seç. / Select that file.
5. Eklentiler menüsünden Aion'u araç çubuğuna sabitle, simgesine bas. / Pin Aion to the toolbar from the Extensions menu, then click its icon.
6. Normal bir web sekmesinde konteyner veya video aracını dene. Ayarlar düğmesi dil ve görünümü açar. / Test on a regular web tab. The Settings button opens language and appearance controls.

Geçici yükleme Firefox kapanınca kaldırılır. Bu yöntem sekme yerleşimi kaynak değişikliğini kurmaz ve tam tarayıcı derlemesi değildir. / Temporary installation is removed when Firefox exits. It does not apply native tab-layout changes or install a compiled browser.

## Firefox kaynağından derleme / Build from Firefox source

[Derleme ve platform durumu / Build and platform status](docs/BUILD.md) dosyasını izle. İndirilen kaynak doğrulanır, ardından Aion kaynakları `omni.ja` içindeki Firefox yerleşik modül sistemine eklenir. Eklenti imza doğrulaması kapatılmaz.

```sh
python3 scripts/fetch_source.py
python3 scripts/prepare_source.py work/upstream/firefox-153.6.0
cd work/upstream/firefox-153.6.0
./mach bootstrap --application-choice browser --no-system-changes
./mach build
./mach run
./mach package
```

Kaynak ve kurulum dosyası aynı şey değildir. İmzalı güncelleyici, Windows/macOS/Android/iPhone paketleri ve iki gerçek sürümle güncelleme testi tamamlanmadan kararlı sürüm yayımlanmayacak. / Source preparation is not a browser binary. Stable releases require signed updates, platform installers and a real two-version upgrade test.

## Güvenlik, gizlilik ve lisanslar / Security, privacy and licenses

- [Güvenlik modeli / Security model](SECURITY.md)
- [Veri akışları / Data flows](PRIVACY.md)
- [Lisanslar ve marka sınırları / Licensing and branding](docs/LICENSING.md)
- [Üçüncü taraf bildirimleri / Third-party notices](THIRD_PARTY_NOTICES.md)
- [Son doğrulanan devir noktası / Handoff](FORGE.md)

Yeni kaynak kodu MPL-2.0 lisanslıdır. Üçüncü taraf bileşenlerin lisansları korunur. Projenin ücretsiz dağıtılması, açık kaynak lisanslarının izin verdiği ticari kullanımı yasaklamaz. Tarayıcıya “virüs bulaşmaz” veya “hiç veri göndermez” garantisi verilmez.

New source code is under MPL-2.0. Third-party components retain their licenses. Free distribution does not prohibit commercial uses permitted by open-source licenses. No claim of absolute malware protection or zero network communication is made.
