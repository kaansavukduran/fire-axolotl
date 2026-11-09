# Fire Axolotl devir noktası / Handoff

- Depo / Repository: https://github.com/kaansavukduran/fire-axolotl
- Dal / Branch: `main`
- Doğrulanan kod kaydı / Validated code commit: `3b3282293224446e38c5f4c5fc484f978499cd6a`
- Tarih / Date: 2026-11-09, Europe/Istanbul
- Ürün aşaması / Product stage: geliştirici önizlemesi; kararlı tarayıcı veya kurulum dosyası henüz yayımlanmadı. / Developer preview; no stable browser or installers published.

## Kapsam / Scope

Kullanıcı, ücretsiz dağıtılacak gerçek bir Firefox forku istiyor. Aion aksolotl karakterli özgün marka, Türkçe/İngilizce, seçilebilir üst/sol/sağ sekmeler, sevdiği eklentilerin kurulum gerektirmeyen karşılıkları ve Firefox benzeri güvenli güncelleme temel hedefler. Tam eklenti eşlemesi `docs/FEATURES.md` içinde. Aion referanslarının ChatGPT ile üretildiği kullanıcı tarafından doğrulandı. / Free Firefox fork, independent Aion identity, bilingual UI, selectable tab placement, built-in equivalents of the requested tools and secure browser updates.

## Yapılanlar ve doğrulama / Implemented and validated

Firefox ESR `153.6.0esr` kaynak/hash pini, kaynak indirme ve hazırlama betikleri; Aion yerleşik modülü; kalıcı/geçici konteynerler; hız ve çözünürlük; yerel çift altyazı; açık eylemle isteğe bağlı HTTPS çeviri; kelime defteri; görünüm/erişilebilirlik; yedek; isteğe bağlı ilerleme; yerel sekme konumu kontrolü; araç çubuğu düzenleyicisi; OpenDyslexic; varsayılan koyu tema; site CSS’ine müdahale etmeyen bağımsız renk tercihi; telemetri/sponsor kapatma ilkeleri; CI, gerçek Firefox test akışı ve günlük ESR tazelik kontrolü.

`npm run check`, 16 birim/gerileme testi, 21 gerçek Firefox arayüz/entegrasyon senaryosu ve `mach configure` geçti. Ayrıntılı kanıt ve sınırlar `docs/VALIDATION.md` içinde. Testler süreç güvenliğini veya TLS doğrulamasını kapatmadı. / Checks, 16 unit/regression tests, 21 real-Gecko interface/integration scenarios and native configure passed; see the validation document for limits.

## Çalışma alanındaki tam derleme / Long native build in the workspace

Bu devir notu yazılırken tam derleme devam ediyordu. / Full source compilation was still running when this note was written.

Arayüz gösterimi sırasında yeniden kontrol edildi: bağımsız çalıştırılabilir dosya henüz oluşmamıştı ve derleme devam ediyordu. `docs/UI_PREVIEW.md` içindeki yeni ekranlar, geçici Aion modülü ve yerel kaynak kontrolü test düzeneğinden alınmıştır; tamamlanmış ürün olarak gösterilmemelidir. / Rechecked during UI preview capture: no independent executable yet; screenshots document the working test preview, not a finished product.

- Kaynak / Source: `/workspace/work/upstream-source/firefox-153.6.0`
- Log: `/workspace/work/mach-build.log`
- Configure log: `/workspace/work/mach-configure.log`
- Araçlar / Toolchains: `/workspace/work/mozbuild`, `/workspace/work/cargo`, `/workspace/work/rustup`
- İlk build komut oturumu / initial command session: `86227`
- Derleme, Aion modülünün son küçük düzeltmelerinden önce hazırlanmış kopyayla başladı. Tam derleme bittiğinde **güncel kaynak katmanını yeniden uygula ve artımlı derle**. / The initial prepared tree predates the last companion fixes. Refresh the overlay and rebuild incrementally before validating or packaging.

```sh
cd /workspace/fire-axolotl
python3 scripts/prepare_source.py /workspace/work/upstream-source/firefox-153.6.0
cd /workspace/work/upstream-source/firefox-153.6.0
PATH=/workspace/work/cargo/bin:$PATH CARGO_HOME=/workspace/work/cargo RUSTUP_HOME=/workspace/work/rustup MOZBUILD_STATE_PATH=/workspace/work/mozbuild XDG_CACHE_HOME=/workspace/work/cache python3 mach build
```

Devam etmeden önce mevcut süreç ve son log durumunu incele; aynı derlemeyi eşzamanlı ikinci kez başlatma. / Inspect the live process/log first; do not start a competing build.

## Son kapsam ekleri / Latest scope additions

Firefox’un bütün dilleri ve yerleşik özellikleri hedeflenir; yeni Aion metinleri şu an Türkçe/İngilizcedir. Gerçek Mozilla hesabıyla giriş/Sync ve bütün dil paketleri henüz doğrulanmadı. Yerel gizlilik ilkesi telemetriyi, çalışmaları, reklam ilişkilendirmesini ve sponsorlu önerileri kapatırken hesap/Sync yeteneğini ve güvenlik hizmetlerini korur. / Target all Firefox languages/features; new strings remain TR/EN and real account/language-pack validation is pending.

İlk gönderimin yedeği doğrulanan özel Drive klasöründedir: https://drive.google.com/drive/folders/1hQIvdaWDiM0I1c77mkUEhYhdOCqTbdmw . Her yeni başarılı push için ayrı commit eşleşmeli ZIP/bundle/makbuz ekle. / Preserve prior backups and add a fresh commit-matched backup after each successful push.

## Öncelikli sonraki işler / Next priorities

1. Tam derlemeyi tamamla, güncel modülü yeniden paketle, gerçek bağımsız tarayıcıyı yeni Fire Axolotl profilinden aç. Yerleşik modülün kullanıcı kurulumu olmadan yüklenmesini doğrula. / Finish native build and verify built-in loading in a fresh, separate profile.
2. Uygulama kimliğini, markalamanın bütün platform varlıklarını ve tam Türkçe tarayıcı dil paketlemesini doğrula. / Verify identity, all branding assets and full Turkish browser localization.
3. Projeye ait imzalı güncelleme altyapısını kur; iki gerçek pakette veri koruyarak yükseltme testi yap. Geliştirme `.mozconfig` dosyasındaki kapalı güncelleyiciyle kararlı sürüm yayımlama. / Implement signed updates and a real upgrade test; no stable release with the development updater disabled.
4. Eklenti eşlemesindeki eksikleri sırayla tamamla. uBlock/Bitwarden veya diğer kodlar alınmadan lisans/sürüm/özet envanterini güncelle. Netflix kalite/DRM veya DeepL eşdeğerliğini uygulanmış gibi gösterme. / Complete mapped gaps with provenance and licensing; do not claim unsupported integrations.
5. Windows Setup.exe, Linux AppImage/.deb, macOS imzalı/notarized .dmg, Android imzalı APK ve iPhone TestFlight/App Store akışlarını doğrula. Henüz hiçbiri hazır değil. / Validate all platform installers and store flows; none are ready yet.

Her başarılı push sonrası `python3 scripts/backup.py` ile kaynak ZIP, bütün erişilebilir Git geçmişi ve commit makbuzu oluştur; kullanıcının Drive hedefindeki `fire-axolotl` klasörüne yükleyip doğrula. Özel anahtarları yedekleme. / Back up every successful push to the user's private Drive destination, excluding private keys.
