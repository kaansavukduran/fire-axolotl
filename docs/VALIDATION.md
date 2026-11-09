# Doğrulama / Validation

2026-11-09, Europe/Istanbul. Geliştirici önizlemesi; güvenlik sertifikasyonu veya kararlı sürüm değildir.

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

Güvenli imzalı güncelleme ve iki sürüm arasında veri koruma; Windows/macOS/ARM/mobil paketler; bütün Firefox dilleri ve dil paketi değiştirme; gerçek Mozilla hesabı/Sync; Safe Browsing/CDM hizmet erişimi; canlı YouTube/Netflix kalite davranışı; dış HTTPS çeviri hizmetiyle uçtan uca işlem; bütün iframe oynatıcıları; ekran okuyucuyla insan testi; bağımsız güvenlik/ağ incelemesi. Eksik özellikler [FEATURES.md](FEATURES.md) içinde saklanır.

Signed upgrades, other platforms, complete locales, actual account/service access, live streaming adapters, external translation, all-frame support, human accessibility review and independent security review remain pending. Passing tests does not certify a browser as malware-proof.

Actions sonuçlarını ilgili commit'in çalıştırmalarından kontrol et. Workflow dosyasının bulunması, başarıyla tamamlandığı anlamına gelmez.
