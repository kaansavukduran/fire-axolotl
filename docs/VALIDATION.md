# Doğrulama / Validation

Tarih / Date: 2026-11-09. Geliştirici önizlemesi / developer preview.

## Geçen kontroller / Passed

- `npm run check`: JavaScript sözdizimi, iki dilde çeviri anahtarları, yerel sekme arayüzü metinleri, manifest ve sınırlı izin modeli. / Syntax, localization, native-control strings, manifests and limited permissions.
- `npm test`: 12 Node testi ve 4 Python testi. Kimlik/yetki sınırları, şüpheli URL'ler, bağımsız ayarlar, tekrarsız ilerleme, geçici konteyner sahipliği, altyazı zamanları, bozuk kaynak özeti, tekrarlanabilir XPI ve kaynak katmanı güncellendiğinde yinelenmeyen yerel kontroller. / 16 unit/regression checks.
- `tests/gecko_e2e.py`: hash doğrulamalı Firefox **153.6.0esr**, geckodriver **0.37.1** üzerinde **21** arayüz/entegrasyon senaryosu. / 21 real-Gecko interface/integration scenarios.
- Türkçe/İngilizce, Lexend, yüksek kontrast/koyu tema, bağımsız yazı boyutu, elle %135, klavye adımı, dar ekranda %200 ve ayrı sıfırlamalar. / Bilingual UI, font/theme, independent text size, manual/keyboard scale, narrow 200% layout and independent resets.
- Sayfa yeniden açıldığında ayarlar, gerçek Firefox konteyneri, tekrarsız kelime defteri, ilerleme kapalıyken ana işlevler ve çevrimdışı ayarlar. / Page-reopen persistence, actual containers/vocabulary and offline operation.
- Araç çubuğu eylemiyle gerçek `activeTab` izni, gerçek WebM dosyasında **1,35×**, gerçek **320×180** çözünürlük, altyazı satırı, çift altyazı ve katmanı kaldırma. / Real permission grant, speed/resolution, caption extraction and overlay lifecycle using an original synthetic fixture.
- Üst/sol/sağ sekme kontrolü: kaynak modülü Firefox'un gerçek ayar belgesine test düzeneğiyle eklendi; yalnızca henüz upstream ikilide bulunmayan yerel kaynaklar sağlandı. Gerçek tercihler ve fiziksel sekme konumu doğrulandı. / Source control injected into the real preferences document with local-resource fixtures; real native preference/layout behavior verified.
- OpenDyslexic Aion'da ve gerçek araç çubuğu/adres çubuğunda yüklendi. Yerel yazı kaynakları test düzeneğiyle sağlandı. Web sayfasının kendi yazı tipi ve CSS arka planı korundu; renk tercihi medya sorgusu koyu/açık seçeneklerini ve koyu tarayıcıyı takip etti. Araç çubuğu düzenleyicisi gerçek kontrol üzerinden açıldı. / Native font, preserved site CSS/fonts, independent color preferences, dark-theme following and toolbar editor verified.
- Gizlilik ilkesi ayrı bir test Firefox kopyasına yüklendi; telemetri yüklemesinin kilitli kapalı, sponsorlu içeriğin kapalı ve Mozilla hesabı yeteneğinin açık kaldığı kontrol edildi. Asıl test ikilisi veya kullanıcının tarayıcı kurulumu değiştirilmedi. / Policy tested in an isolated runtime copy, preserving the original binary and user installations.
- Güncel kaynak katmanı, gerçek Mozilla dosyalarının küçük bir kopyasında iki kez uygulanıp yeni kontrollerin ve kaynakların tek kez paketlendiği doğrulandı. / Overlay update/idempotence verified on real source files without interrupting the long build.
- Firefox kaynak arşivi SHA-512 doğrulandı. Kaynak katmanı uygulandı; `mach configure` geçti. / Source archive verified, overlay applied and native configure passed.
- `scripts/check_upstream.py`: kontrol anında ESR pini günceldi. / ESR pin current at check time.

Firefox testleri süreç korumaları veya TLS doğrulaması kapatılmadan çalıştırıldı. Ortamın komut kum havuzu Firefox'un kendi süreçlerini başlatamadığı için test çalıştırıcısı izin verilen dış yürütme yolunda çalıştırıldı; bu ürün ayarı değildir. / Browser isolation and TLS verification were not disabled. The test runner used the approved outer execution path because the command sandbox could not start Firefox child processes.

## Henüz doğrulanmayanlar / Not yet verified

Tam kaynak derlemesinden çıkan bağımsız tarayıcının ilk açılışı ve paketlenmesi; bütün işletim sistemleri; imzalı iki gerçek tarayıcı sürümü arasında veri koruyan güncelleme; tarayıcının yeniden başlatılmasında bütün kayıtların korunması; canlı YouTube/Netflix kalite davranışı; gerçek HTTPS çeviri hizmetiyle uçtan uca gönderim; gerçek Mozilla hesabı/Sync; bütün dil paketleri ve yeni Aion metinlerinin bütün dillere çevirisi; tüm iframe ve yerel video tam ekranları; ekran okuyucuyla insan testi ve bağımsız güvenlik/ağ denetimi.

Independent compiled browser startup/packaging, all target operating systems, signed two-version upgrades, full-browser restart persistence, live streaming-site quality, actual external translation service, every iframe/native fullscreen case, human screen-reader review and independent security audit remain unverified. Actual account/Sync and complete language-pack/new-string coverage also remain unverified. Passing companion tests is not a browser security certification.

Actions, aynı kaynak testlerini ve gerçek Firefox testlerini yeni gönderimlerde yeniden çalıştırır. Sonuçlar ilgili commit'in Actions sayfasından kontrol edilmelidir. / Actions repeats repository and Gecko tests for new commits; inspect the specific commit's runs.
