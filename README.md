# Fire Axolotl

<img src="branding/icon-256.png" width="128" height="128" alt="AI-generated Aion axolotl icon">

**Daha az eklenti, daha fazla kontrol. / Fewer extensions, more control.**

Firefox ESR kaynak kodunu temel alan, Aion karakteriyle kişiselleştirilen ücretsiz bir tarayıcı projesi. Fire Axolotl, Mozilla veya ürünleriyle resmi olarak bağlantılı değildir. Firefox, Mozilla Foundation'ın ticari markasıdır.

Free browser project based on Firefox ESR source, with an Aion companion. Fire Axolotl is not officially associated with Mozilla or its products. Firefox is a trademark of the Mozilla Foundation.

**Durum / Status: ESR 153.7.0esr tabanlı Windows x64 ve Linux x86_64 geliştirici ön sürümleri yayımlandı. Kararlı günlük kullanım sürümü değildir; Authenticode imzası ve otomatik güncelleme yoktur. / Published developer previews; unsigned, automatic updates disabled.**

[Windows x64 Setup.exe indir](https://github.com/kaansavukduran/fire-axolotl/releases/download/v0.2.0-dev.20261110-windows/fire-axolotl-0.2.0-dev.20261110.1-windows-x86_64-Setup.exe) · [Windows sürüm notları](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.2.0-dev.20261110-windows) · [Linux AppImage / Ubuntu .deb](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.2.0-dev.20261110-linux)

Windows'ta yalnızca **Setup.exe** dosyasını indirip kurulum sihirbazını izle; Başlat menüsünden **Fire Axolotl** aç. Gerekli Microsoft x64 Visual C++ runtime dosyaları bu pakete lisans bildirimleriyle dahil edildi. Kaynak ZIP'lerini indirmen gerekmez. Önceki 153.6 önizlemeleri tarihsel dosyalardır; üzerlerine yazılmadı.

Yeni profilde koyu görünüm ve **üst sekmeler** bulunur. Ayarlar'dan üst/sol/sağ sekmeleri, tarayıcı fontunu ve site renk tercihini seçebilirsin. Ana tarayıcı Firefox'un **103 resmî masaüstü dilini** içerir; yeni Aion metinleri Türkçe/İngilizcedir. Yerleşik Aion/uBlock Origin, konteynerler, video araçları, isteğe bağlı karakterler ve çevrimdışı Aion Koşusu kullanıcı kurulumu olmadan gelir.

Aion **0.2**: 760px panel, tam sekme araç alanı, sağ tıkla konteyner açma ve görünür cihazda çeviri düğmesi. **Aion → Çeviri → Cihazda çeviri aracını aç** yolunu izle; dil modelleri ilk kullanımda indirilir. Ayrı sohbet modeli kurulu değildir.

Her iki platformda kurulu tarayıcı üzerinde **70 mevcut senaryo + 9 yeni araç senaryosu**, ayrıca gerçek İngilizce–Türkçe çıkarım ve internet kapalıyken yeni metin çevirisi geçti. Windows'ta gerçek 0.1 Setup → 0.2 Setup yükseltmesinde sentetik parola, yer imi, konteyner, kelimeler, karakter PNG'si ve ayarlar korundu. Bu elle kurulum testidir; imzalı otomatik güncelleme değildir. [Doğrulama ve sınırlar](docs/VALIDATION.md) · [Kullanım kılavuzu](docs/QUICK_START.md).

[Çalışan arayüzün ekran görüntüleri / Screenshots of the running interface](docs/UI_PREVIEW.md)

Bu depo; doğrulanmış Firefox kaynağını indiren derleme katmanını, özgün markalamayı, yerleşik Aion modülünü ve sekme konumu için yerel ayarları içerir. Motorun tüm geçmişini bu küçük depoya kopyalamak yerine kaynak sürümü ve SHA-512 özeti `upstream.json` içinde sabitlenir. Gömülü modül tarayıcı derlenirken paketlenir; son kullanıcının ayrı eklenti kurması hedeflenmez. Geliştirme sırasında aynı modül geçici eklenti olarak denenebilir.

Firefox'un yerleşik özellikleri, dil yönetimi ve isteğe bağlı Mozilla hesabı/Sync temel alınır. Telemetri, çalışmalar, sponsorlu öneriler ve reklam ilişkilendirmesi yerel ilkelerle kapatılır; güvenlik bağlantıları korunur. Ana tarayıcıda 103 dil paketlenmiştir. Yeni Aion metinlerinin TR/EN dışına çevrilmesi ve gerçek hesapla Sync doğrulaması henüz tamamlanmadı.

This repository contains a pinned Firefox source build overlay, original branding, the built-in Aion module, and native tab-layout settings. The upstream version and SHA-512 are locked in `upstream.json`; the complete engine history is not duplicated here. The companion is embedded at browser build time. A temporary add-on package is available for development, not as a browser installer.

## Bu aşamada eklenenler / Implemented in this stage

- Kaynak katmanında yerleşik uBlock Origin: resmî imzalı paket, sabit sürüm/özet ve tam ilgili kaynaklar. [Lisans, izin ve ağ ayrıntıları](docs/COMPONENTS.md). / Built-in uBlock Origin in the source overlay, with the official signed package, pinned provenance and corresponding source.
- İsteğe bağlı görsel sağ tık menüsü: Google Lens, Bing, TinEye ve Yandex; yalnızca seçtiğin sağlayıcıya açık eylemle görsel adresi gönderme. / Optional image context menu with explicit provider selection.
- İsteğe bağlı yerel karakter yan paneli: Aion, kuzu, kurt ve baykuş; bütün karakterin çizilmiş kareleri, okuma/çalışma animasyonları, özel PNG kare şeridi ekleme, duraklatma ve ayrı karakter yedeği. [Kullanım](docs/CHARACTERS.md). / Optional local animated companions, custom PNG sprite import, pause and character backup.
- Kalıcı ve son sekme kapanınca temizlenen geçici konteynerler. / Persistent and temporary containers cleaned up after their last tab closes.
- Video hızını 0,25×–4× ayarlama, gerçek video çözünürlüğünü okuma. / 0.25×–4× video speed and actual decoded resolution.
- YouTube için deneysel kalite isteği; her sitede ve her abonelikte kalite garantisi değildir. / Experimental YouTube quality requests; no universal resolution guarantee.
- Yerel VTT/SRT dosyalarından çift altyazı, videonun kendi tam ekranında yerel altyazı çizimi, mevcut altyazı satırını alma. / Dual local VTT/SRT captions, native video fullscreen text tracks and current cue capture.
- Açık kullanıcı eylemiyle seçili metin çevirisi; isteğe bağlı, kullanıcının seçtiği HTTPS hizmeti. / Explicit selected-text translation through an optional user-chosen HTTPS service.
- Varsayılan koyu görünüm, Türkçe/İngilizce Aion arayüzü, dört tema, %80–%200 arayüz ölçeği, bağımsız yazı boyutu, OpenDyslexic ve Lexend. / Default dark appearance, Turkish/English Aion UI, four themes, 80%–200% interface scale, independent text size, OpenDyslexic and Lexend.
- JSON yedekleme/geri yükleme, isteğe bağlı üç gerçek eyleme dayalı keşif ilerlemesi. / JSON backup/restore and optional milestones based on three real actions.
- Kaynak katmanında üst/sol/sağ sekmeler, Firefox araç çubuğu düzenleyicisi, bağımsız site renk tercihi ve yerel arayüz yazı tipi. / Native tab layout, toolbar customization, independent website color preference and native interface fonts.

Yeni profilde sekmeler varsayılan olarak **üsttedir**. Kullanıcının seçtiği sol/sağ düzen normal tercih olarak saklanır; başlangıçta zorla sıfırlanmaz. / New profiles default to top tabs; saved left/right choices are not forcibly reset.

Varsayılan tarayıcı koyudur. Sitelerin kendi tasarımı ve kaydettiğin tema seçimi korunur; yalnızca tarayıcı renk tercihini takip eden siteler koyu tercihi alır. Sayfalar zorla karartılmaz. Tarayıcı arayüzü için font seçmek web sitelerinin fontunu değiştirmez. / The browser defaults to dark. Site design and saved site choices stay intact; sites following browser preference receive dark. There is no forced recoloring, and native interface font changes do not override website fonts.

İstenen eklentilerin tek tek kapsamı ve eksikleri: [Özellik eşlemesi / Feature map](docs/FEATURES.md).

Bütün tarayıcı isteklerinin durumu ve sırası: [İstek takibi / Requirements](docs/ROADMAP.md). Linux x64 tam kaynak derlemesi artık açılıyor; [native test sonuçları](docs/VALIDATION.md) ayrı doğrulanıyor. Bu, güvenli otomatik güncellemenin veya diğer platformların hazır olduğu anlamına gelmez.

## Modülü kaynak kodundan dene / Try the companion from source

Tam tarayıcı için yukarıdaki Release bağlantısını kullan. Aşağıdaki adımlar yalnızca modül geliştirme içindir. / For the complete browser use the release above. The following steps are for module development only.

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
4. `dist/fire-axolotl-0.2.0-developer-addon.xpi` dosyasını seç. / Select that file.
5. Eklentiler menüsünden Aion'u araç çubuğuna sabitle, simgesine bas. / Pin Aion to the toolbar from the Extensions menu, then click its icon.
6. Normal bir web sekmesinde konteyner veya video aracını dene. Ayarlar düğmesi dil ve görünümü açar. / Test on a regular web tab. The Settings button opens language and appearance controls.

Geçici yükleme Firefox kapanınca kaldırılır. Bu yöntem sekme yerleşimi kaynak değişikliğini kurmaz ve tam tarayıcı derlemesi değildir. / Temporary installation is removed when Firefox exits. It does not apply native tab-layout changes or install a compiled browser.

## Firefox kaynağından derleme / Build from Firefox source

[Derleme ve platform durumu / Build and platform status](docs/BUILD.md) dosyasını izle. İndirilen kaynak doğrulanır, ardından Aion kaynakları `omni.ja` içindeki Firefox yerleşik modül sistemine eklenir. Eklenti imza doğrulaması kapatılmaz.

```sh
python3 scripts/fetch_source.py
python3 scripts/prepare_source.py work/upstream/firefox-153.7.0
cd work/upstream/firefox-153.7.0
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
- [Doğrulama sonuçları ve sınırlar / Validation results and limits](docs/VALIDATION.md)

Yeni kaynak kodu MPL-2.0 lisanslıdır. Üçüncü taraf bileşenlerin lisansları korunur. Projenin ücretsiz dağıtılması, açık kaynak lisanslarının izin verdiği ticari kullanımı yasaklamaz. Tarayıcıya “virüs bulaşmaz” veya “hiç veri göndermez” garantisi verilmez.

New source code is under MPL-2.0. Third-party components retain their licenses. Free distribution does not prohibit commercial uses permitted by open-source licenses. No claim of absolute malware protection or zero network communication is made.
