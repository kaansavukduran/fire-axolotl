# Aion0.3 doğrulaması

[Windows kurulum/yayın](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42892753032) ve [Linux kurulum/yayın](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42892758797) başarılı. Paketleme kaydı `b6f39f35ccdb2ff7f00b0fb790c0f22ba41745b9`;153.7 motorları aynı sabit kaynaklardan korunur.

- Her kurulu üründe **70 mevcut +9 araç +9 yeni sekme =88 senaryo**, ayrıca gerçek yerel/çevrimdışı EN→TR çıkarımı geçti.
- Yeni9: üst/arama/yer imleri varsayılanı, paketli arka plan, gizle/geri getir ve yeniden açma, gerçek Vercel düğmesi, iki ayrı geçici çerez alanı, yalnızca sahip olunan son alanın temizliği, gerçek duvar kağıdı ayarı, dar pencere ve gerçek restartta kişisel düzenin korunması.
- Her iki CI kurulumunda normal ağ/TLS ile yeni sekme kontrolleri geçti. Buluttaki ayrı yerel kontrolde sadece sentetik profile sağlanan proxy/CA kullanıldı; ürün güvenliği değiştirilmedi. Vercel kontrolü gerçek gezinmeyi doğrular; tüm Godot oynanışını Firefox'ta sınadığı iddia edilmez. Her yayın canlı build.json/HTML eşleşmesini ayrıca denetler. Linux yayın denetiminde canlı oyun0.7.0 /a538d77aa9f43a53 idi.
- Windows gerçek0.2→0.3 Setup yükseltmesi NSS parola, yer imi, konteyner, kelime, PNG, dil/font/sekme/rekoru korudu. Önceki profilde kaldırılmış indirme düğmesi de geri eklenmedi; yeni varsayılanlar kişisel araç çubuğunun üstüne yazmadı. Yeni native çeviri bağlantısı da çalıştı.
- Türkçe Görünüm ekranındaki **Önerilen üst düzeni uygula** düğmesi yerelde gerçek tıklamayla sınandı; üst/arama/yer imleri dönerken bağımsız font tercihi korundu. Gerçek TR ve dar ekran görüntüleri [UI_PREVIEW](UI_PREVIEW.md) içinde.
- 27 Node +39 Python ve kaynak/izin/varlık kontrolleri geçti. İki yeni Node kontrolü: yalnızca sahip olunan geçici alanların temizliği/hata geri alma ve sıradan sitenin oyun köprüsünü kullanamaması/sabit URL/kaynak konteyneri.

İmzalı otomatik güncelleme, Authenticode, gerçek hesap Sync ve özellik eşlemesindeki diğer açıklar sürer. Aşağıdaki kayıtlar önceki aşamalardır.

# Aion 0.2 doğrulaması · 2026-11-10

- [Windows kurulum/yayın](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42881924559) ve [Linux kurulum/yayın](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42881930851). Paketleme kaydı `bde5110227ae29ef054d8471f72b01ed6918d5f4`; aynı 153.7 motor pinleri korunur.
- Her platformda 70 mevcut senaryo, ayrıca **9 gerçek araç senaryosu** geçti: geniş yerel popup, normal düğmeyle tam sekme açma, kaynak sekmeye video işlemi, kişisel/iş çerez ayrımı, gerçek sağ tık konteyner/seçili metin menüleri, yerel çeviri açma, klavye, TR/EN ve OpenDyslexic/%200 dar görünüm; sıradan sitenin ayrıcalıklı aracı açamaması.
- Her iki kurulu tarayıcı kendi normal ağ/TLS ayarlarıyla dil modelini indirdi: **Hello world → Merhaba dünya**. Ardından tarayıcı çevrimdışına alınıp yeni bir metinle **Good morning → Günaydın** doğrulandı. Sohbet modeli veya önceden indirilmiş çeviri modeli paketlendiği iddia edilmez. Bu iki sentetik örnek tüm dillerin kalitesini veya her web sitesini doğrulamaz.
- Windows gerçek önceki 153.7/Aion0.1 Setup → Aion0.2 Setup yükseltmesini geçti. Sentetik parola, yer imi, konteyner, kelimeler, özel PNG ve tercihler korundu; aynı profilde yeni yerel çeviri köprüsü de çalıştı. Bu, elle Setup yükseltmesidir; MAR/otomatik güncelleme değildir.
- `npm test`: 25 Node + 39 Python kontrolü. `npm run check`: JavaScript, manifest/izinler ve 129 TR/EN anahtarı. Yeni native köprü yalnızca kendi Aion sayfasından sabit yerel çeviri adresini açar; çağıran URL/kod/dosya yolu veremez. Yeni WebExtension izni eklenmedi; TLS, süreç kum havuzu ve dış eklenti imza kontrolleri korunur.
- Kamuya açık dosya doğrulaması ve özel kaynak yedeğinin geri okuma makbuzları çalışma alanında tutulur. Aynı SHA-256'lı değişmeyen büyük motor kaynakları önceki tam doğrulamayla eşleştirilir; değişen yayın dosyaları yeniden indirilip hashleri karşılaştırılır. Profiller ve ham ağ kayıtları yayınlanmaz.

İmzalı otomatik güncelleme/Authenticode, gerçek hesap Sync, kalan hizmet erişimi ve [özellik eşlemesindeki](FEATURES.md) açıklar sürer. Aşağıdaki 0.1 ve 153.6 kayıtları tarihseldir.

# Önceki 0.1 / 153.7 doğrulaması · 2026-11-10

- [Windows x64 yayın ve kurulum](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42849921106) ve [Linux yayın ve kurulum](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42849928004) başarılı. Her kurulu üründe **11 açılış + 4 süreç yeniden başlatma + 34 entegrasyon + 11 oyun + 10 dil = 70 senaryo** geçti.
- Windows tam motor derlemesi [42828049949](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42828049949), kaynak `a6560b7fe2a42d7602001d11641e722ac087d297`. Linux tam motor derlemesi [42827574889](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42827574889), kaynak `ec13e3f64fe973ead7f2b14381e2d3a08c7e1bd6`. Her iki paketleme kaydı `0759fae4b09e5cf27f709a1496eea3a23d1c33df`; motor yeniden derlenmeden yalnızca doğrulanmış UI/dil katmanı uygulanır ve tüm değişmeyen dosyalar kontrol edilir.
- 103 resmî dilin yerel varlığı, bağımsız dil kimlikleri, DE/JA/AR/TR/EN normal seçici geçişi, Arapça RTL ve gerçek süreç yeniden başlatmalarında sekme/font/oyun rekorunun korunması geçti. Aion'un yeni metinleri TR/EN ile sınırlıdır.
- Windows gerçek offline Setup temiz kuruldu; kurulu **80 dosya** ZIP ile eşleşti. Microsoft imzaları/hashleri, CRT import kapanışı ve gerçek XUL'u app-local CRT ile yükleyen statik test geçti. Sistem CRT/güvenlik dosyaları değiştirilmedi. Kaldırma profili ve varsayılan tarayıcı seçimini korudu.
- Gerçek eski 153.6 Setup → yeni 153.7 Setup aynı kurulum dizinine uygulandı. Sentetik NSS parola, yer imi, konteyner, kelime, özel PNG, dil, sekme konumu, font, rekor ve Unicode işaret dosyası korundu. Bu test gerçek hesaba ait veri kullanmaz ve imzalı MAR/otomatik güncelleme değildir.
- Linux AppImage çalıştırma ve iki paketin dosya karşılaştırması, gerçek `.deb` kurulumu ve kurulu tarayıcı testleri geçti. Yayımlanmış tüm dosyaların sunucu SHA-256 özetleri, ZIP CRC ve tam kaynak akışının özeti ayrıca indirildikten sonra doğrulandı.
- Ağ kaydı yerel HTTP kontrol isteğiyle doğrulandı; 30 saniyelik yeni profil/yeni sekme örneğinde bilinen Mozilla telemetri/çalışma/sponsor uçları görülmedi. İlk yayın raporunun URL listesi yanıt başlığındaki adresleri de içerebilir; listedeki her URL gerçek bağlantı girişimi sayılmaz. Ayrı salt okunur [42854557684](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42854557684) Windows ve Linux üzerinde geçti; aynı yayımlanmış hashli dosyalar yalnızca `nsHttp uri=` kanal kayıtlarından yeniden değerlendirildi. Ham günlükler/profiller yayımlanmaz. Bu örnek tüm gezinme veya zamanlanmış trafik denetimi değildir.
- Yerel 153.7 tarayıcıda gerçek SearchService varsayılan motoru, arama düğmesinin yerelleştirilmiş metni ve gerçek tıklama/klavye ile adres çubuğuna odak/yazı devri doğrulandı. Gerçek kullanıcı sorgusu gönderilmedi. Upstream arama ortaklık parametreleri korunur; bağımsız hizmet anlaşmaları doğrulanmış değildir.

İmzalı otomatik güncelleme, Authenticode, gerçek hesap/Sync ve CDM/Safe Browsing hizmet erişimi, canlı servis video kalite bağdaştırıcıları, Aion metinlerinin tüm dillere çevirisi ve [özellik eşlemesindeki](FEATURES.md) açıklar sürüyor. Bu geliştirici önizlemesi kararlı günlük kullanım veya virüs bağışıklığı sertifikası değildir. Aşağıdaki sonuçlar **153.6 tarihsel kayıtlarıdır**.

# Tarihsel Windows x64 ön sürümü · 2026-11-10

- [Sürüm](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.1.0-dev.20261110-windows); motor kaynağı `9d564dced55dc4816cc4aeb57387ba1643f007ed`, paketleme/etiket hedefi `535b6e2a5279bfb7037f20dbda98e0d5afc42b14`.
- Motor run 42791204074; değiştirilmemiş motor girdileri ve kesin ZIP/Setup/source özetleriyle başarılı native yeniden doğrulama 42808841079. Native 11 açılış + 4 restart + 34 entegrasyon + 11 oyun + 5 dil senaryosu geçti.
- Gerçek temiz NSIS kurulumu [42810293175](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42810293175) içinde yapıldı. Bütün kurulu paket dosyaları güncel ZIP ile eşleşti. Kurulu programda aynı 65 senaryo, bağımsız profil kökü ve devre dışı default-agent doğrulandı. Kaldırma, profil verisini ve varsayılan tarayıcı seçimini korudu.
- İlk yayın denemesinde taslak yeni oluşturulduktan sonra liste okuması gecikti; yalnızca yayın işi yeniden koştu. Son akış başarılı, 14 asset sunucu SHA-256 özetleriyle yayımlandı. Gelecek yayınlarda taslak kimliği doğrudan oluşturma API yanıtından alınır.
- Authenticode imzası, otomatik güncelleyici, gerçek Windows 10/11 insan testi, gerçek hesap Sync/CDM/Safe Browsing hizmet erişimi ve diğer diller henüz tamamlanmadı. Testler kötü amaçlı yazılımlardan bağışıklık garantisi değildir.

# Doğrulama / Validation

2026-11-09, Europe/Istanbul. Geliştirici önizlemesi; güvenlik sertifikasyonu veya kararlı sürüm değildir.

## Yayımlanan kurulumlar / Published installers

[v0.1.0-dev.20261109](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.1.0-dev.20261109) Linux x86_64 ön sürümü yayımlandı. [Yayın akışı 42682284085](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42682284085) başarılı: 29 birim/gerileme testi, gerçek AppImage açılışı ve iki paketin native dosya eşleşmesi için 4 kontrol; Ubuntu 24.04 üzerinde gerçek `.deb` kurulumu ardından 11 açılış ve 4 süreç yeniden başlatma senaryosu.

Native kaynak `0f94fea2429d578015acc0a6494fe8c2dbd5223a`, paketleme kaynağı/etiket `92e30af0ac76f6aafbd322f9c78b0e68926af98f`. Native CI `42666129157` ayrıca tam derleme, 11 açılış, 34 entegrasyon ve 4 yeniden başlatmayı geçti. Release içindeki `release-manifest.json`, `release-validation.json` ve `SHA256SUMS` yayımlanan dosyalara aittir. Aşağıdaki eski yerel derleme özetleri CI dosyalarının özeti olarak kullanılmamalıdır.

The actual Linux prerelease installers passed the publication workflow. Automatic updates are disabled; native chrome is en-US and Aion is TR/EN. Other platforms, all locales, real-account Sync and live protection/DRM service verification remain incomplete.

## Geçen kontroller / Passed

- `npm run check`: JavaScript sözdizimi, manifest/izinler, 111 arayüz çeviri anahtarı, karakter dosya özetleri ve animasyon sınırları.
- `npm test`: **19 Node + 9 Python**, toplam **28** birim/gerileme testi. Yetkili UI göndereni, şüpheli URL, konteyner sahipliği, çeviri izni, altyazı, PNG/grid, görsel arama, kaynak pini, tekrarlanabilir XPI ve kaynak katmanı geçişleri.
- Firefox **153.6.0esr** tam motor derlemesi tamamlandı. Ürün kimliği `{75450dd9-387d-4289-8b23-7ad6609fa530}`, adı `FireAxolotl`; bağımsız profil ve uygulama kaynakları kullanılıyor.
- `tests/native_smoke.py`: **11** senaryo. Yeni profilde üst sekmeler/koyu tema; kurulum gerektirmeyen etkin Aion ve uBO; gizlilik ilkeleri; Safe Browsing ve imza doğrulama tercihleri; hesap yeteneği; derlenmiş proxy düzeltmesi; dört karakter; gerçek üst/sol/sağ düzen; yerel OpenDyslexic; Hesap/Sync bölümünden ayrı Görünüm ayarları.
- `tests/gecko_e2e.py`, **compiled-fork** modu: **34** senaryo, gerçek bağımsız ikili üzerinde. Geçici eklenti kurulmadı ve yerel ürün kodu enjekte edilmedi. Gerçek istek engelleme, konteyner, kelime defteri, çevrimdışı ayarlar, TR/EN, font/ölçek, dar ekranda %200, gerçek video izni/hızı/çözünürlüğü, çift altyazı ve video öğesinin kendi tam ekranı, yerel görsel menüsü, font/site tercihi, araç çubuğu ve karakter içe/dışa aktarma test edildi.
- `tests/native_restart.py`: **4** senaryo. Tam tarayıcı süreci kapatılıp aynı ayrı profille açıldı; seçilmiş sol sekmeler, font, Places yer imi, dil, konteyner, kelime defteri ve IndexedDB'deki kişisel PNG korunup yeniden çizildi. Bu, iki sürüm arasında imzalı güncelleme testi değildir.
- Aynı **34** entegrasyon senaryosu ayrı upstream Firefox test düzeneğinde de geçti. Bu mod, Aion'u geçici kurar ve yerel kaynakları test belgesine ekler; native testlerin yerine geçmez.
- uBlock Origin **1.76.0** resmî paket özeti ve Git kaynakları sabitlendi. Tam ilgili kaynak arşivinden yeniden üretim, **665** dosyada eşleşti. Mozilla imzaları ve öneri makbuzu kaynak karşılaştırmasının dışındadır; manifest JSON olarak karşılaştırılır. Ayrıntılar [COMPONENTS.md](COMPONENTS.md).
- `scripts/check_upstream.py`: kontrol anında ESR ve uBO sürüm/özet pinleri güncel.
- `mach package` ile gerçek Linux x64 `.tar.xz` üretildi. `verify_native_package.py` ürün kimliğini, tam gizlilik ilkesini, uBO envanterini, GPL bildirimini ve ilgili kaynak arşivinin özetini doğruladı. Arşiv ayrı klasöre çıkartıldı; oradaki ikili yeni profilde aynı **11** native smoke senaryosunu geçti. AppImage/.deb veya imzalı otomatik güncelleme değildir.
- Derlenen ürünün kaynak kaydı: `0f94fea2429d578015acc0a6494fe8c2dbd5223a`. Linux arşivi **115236228 bayt**, SHA-256 `c6315a0f745f33ada02523a96dc52f3110dd241f1fd7a40b5cd497421501c4e2`.
- Tam uygulanmış motor kaynak arşivi **1024371110 bayt**, SHA-256 `1c5385b89ad52b362ae5dc9abcd5b4ad8411c67034ad91b37a70dcc876a957a0`. Akışla taranan **511062** girdi içinde commit makbuzu, paket manifesti, Aion/uBO ve lisanslar doğrulandı; derleme nesneleri dışarıda tutuldu.
- Özel Drive aktarımında tarayıcı iki, tam motor kaynağı on bir kayıpsız parçaya ayrıldı. Bütün parçalar Drive'dan geri okunup boyut/SHA-256 ile karşılaştırıldı. Yeniden birleştirme özeti özgün arşivle eşleşti. Kaynak ZIP/Git bundle yedeği bu büyük motor arşivinden ayrıdır ve ayrıca doğrulandı.

Native smoke, integration and process-restart tests use the real independently compiled fork. Raw reports are generated under `work/native-test-artifacts/` and `work/native-e2e-artifacts/`; browser profiles remain outside published evidence. Screenshots: [UI_PREVIEW.md](UI_PREVIEW.md).

## Test ortamının sınırları / Test environment

`remote.prefs.recommended=false`: WebDriver'ın Safe Browsing/izleyici koruması gibi hizmetleri kapatan toplu test tercihleri uygulanmaz. Önceki 21/33 senaryoluk koşular bu ayrımı içermiyordu; ürün güvenliğinin kanıtı olarak kullanılmamalıdır. Güncel native koşular etkin güvenlik tercihlerini ayrıca doğrular. `dom.file.createInChild=true`, yalnızca Marionette'in yerel dosya seçme testleri için ayrı otomasyon profillerinde açılır; ürün varsayılanı olarak dağıtılmaz. TLS doğrulaması veya tarayıcı süreç kum havuzu kapatılmadı.

Recommended automation preferences are opted out because they disable security services. Only Marionette's file-input capability is enabled in isolated test profiles. Neither TLS verification nor process isolation is disabled. The approved outer execution path is needed because the nested command sandbox cannot start Firefox children.

Testler yerel/sentetik içerikle çalışır. Görsel arama URL'si çevrimdışı açılır; gerçek görsel bir sağlayıcıya gönderilmez. Safe Browsing ve hesap tercihinin açık olması hizmetin gerçek ağda çalıştığını kanıtlamaz. Ortamda bazı Mozilla ağ çağrıları başarısız olmuştur; bağımsız ürün hizmet erişimi ayrıca doğrulanmalıdır.

## Açık işler / Remaining verification

İmzalı uygulama içi güncelleme ve MAR üzerinden veri koruma; macOS/ARM/mobil paketler; yeni Aion metinlerinin diğer dillere çevirisi; gerçek Mozilla hesabı/Sync; Safe Browsing/CDM hizmet erişimi; canlı YouTube/Netflix kalite davranışı; dış HTTPS çeviri hizmetiyle uçtan uca işlem; bütün iframe oynatıcıları; ekran okuyucuyla insan testi; bağımsız güvenlik/ağ incelemesi. Eksik özellikler [FEATURES.md](FEATURES.md) içinde saklanır.

Signed upgrades, other platforms, complete locales, actual account/service access, live streaming adapters, external translation, all-frame support, human accessibility review and independent security review remain pending. Passing tests does not certify a browser as malware-proof.

Actions sonuçlarını ilgili commit'in çalıştırmalarından kontrol et. Workflow dosyasının bulunması, başarıyla tamamlandığı anlamına gelmez.
