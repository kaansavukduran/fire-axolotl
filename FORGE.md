# Türkçe yerelleştirme taslağı / Turkish localization draft

- Dal: `codex/native-turkish-localization`
- Taban: `main`, `32ac4df618156f1d57aac21a15645f842e75b139`
- 2026-11-09, Europe/Istanbul
- Yerel kaynak hazırlama ve 44 saniyelik artımlı derleme geçti; yeni built-in Türkçe etkinleşme testi geçmedi. Bu dal main ile birleştirilmez veya sürüm olarak dağıtılmaz.
- Çalışma ortamı unavailable oldu. Kaynaklar bu dala korunarak taşındı. Tanı, lisans ve sıradaki native test: [docs/LOCALIZATION_DRAFT.md](docs/LOCALIZATION_DRAFT.md).
- Yeni dalın ZIP/bundle/commit makbuzu Actions artifact'iyle hazırlanır. Özel Drive aktarımı ortam kesintisi nedeniyle bekliyor; önceki main yedekleri korunur.

# Fire Axolotl devir noktası / Handoff

- Depo: https://github.com/kaansavukduran/fire-axolotl
- Dal: `main`
- Tarih: 2026-11-09, Europe/Istanbul
- Aşama: gerçek bağımsız Linux x64 geliştirici derlemesi açılıyor; günlük kullanım için kararlı sürüm yok.
- Bu dosyayı içeren commit, ilgili kaynak kaydıdır. Güncel kullanıcı isteği sırası [docs/ROADMAP.md](docs/ROADMAP.md) içinde.

## Kapsam

Ücretsiz gerçek Firefox forku; Aion markası, gömülü araçlar, koyu tarayıcı, kullanıcı seçimine bağlı üst/sol/sağ sekmeler, bağımsız site tercihi ve fontlar, diller/Sync, güvenli güncelleme. Yeni profilde sekmeler **üstte** olmalı. Seçilmiş sol/sağ düzen başlangıçta sıfırlanmaz.

Yanlışlıkla başka uygulamaya ait spor/beslenme/RPG menüsü istekleri durduruldu; o projede kod değişikliği veya push yapılmadı. Kullanıcı yalnızca uygun karakter fikrinin tarayıcıya alınmasını istedi.

## Uygulanan ve doğrulanan

Firefox ESR 153.6.0esr tam kaynak derlemesi tamamlandı. Ayrı `FireAxolotl` kimliği, BrowserGlue başlangıç kaydı ve WebDriver tarayıcı ailesi tanıması düzeltildi. Etkin ilke sözlüğünü dizi sayan upstream ServiceRequest hatası düzeltildi. Yerel ayarlar Görünüm'e yerleştirildi; Hesap/Sync'e taşmıyor.

Aion ve resmî uBlock Origin 1.76.0 native yerleşik olarak otomatik yükleniyor. uBO sürüm/hash/Git alt kaynakları sabit, GPL tam ilgili kaynak arşivi mevcut; yeniden üretimde 665 dosya eşleşti. Konteynerler, video hızı/çözünürlüğü, VTT/SRT çift altyazı ve video öğesinin kendi tam ekranında çizim, seçili metin çeviri akışı, görsel sağ tık araması, kelime defteri, görünüm/font/ölçek, isteğe bağlı ilerleme/yedek var.

İsteğe bağlı karakter yan panelinde Aion/kuzu/kurt/baykuş bütün gövde resim dizileri var. Kullanıcı yerel PNG kare şeridi ekleyebilir, durdurabilir, silebilir ve ayrı karakter yedeğini geri alabilir. İşletim sisteminin hareket azaltma tercihi korunur. ChatGPT Pet koleksiyonundaki kullanıcıya ait Aion yalnızca okundu; koleksiyon değiştirilmedi.

Kontroller: `npm run check`; 19 Node + 9 Python testi; gerçek derlenmiş forkta 11 native smoke + 34 entegrasyon + 4 süreç yeniden başlatma senaryosu; ayrıca upstream test düzeneğinde 34 senaryo geçti. Ayrıntılar [docs/VALIDATION.md](docs/VALIDATION.md). Otomasyonun güvenlik hizmetlerini kapatan toplu tercihleri uygulanmaz; yalnızca dosya girdisi için gereken Marionette tercihi ayrı test profillerinde açılır.

## Çalışma alanı

- Kaynak: `/workspace/work/upstream-source/firefox-153.6.0`
- Native ikili: `obj-fire-axolotl/dist/bin/fire-axolotl`
- İlk tam derleme logu: `/workspace/work/mach-build.log` (175m57s, başarılı)
- Son native derleme logu: `/workspace/work/mach-remote-family-build.log`
- Paket logu: `/workspace/work/mach-package-with-policy.log`
- Native raporlar: depo `work/native-test-artifacts/`, `work/native-e2e-artifacts/`
- Otomasyon profilleri: depo `work/native-test-profiles/`; bunları yayımlama.

Önemli paketleme düzeltmesi: upstream, `distribution/*` dosyalarını yalnızca BUILT_BY_MOZILLA için paketliyordu. Kendi paket manifestimiz gizlilik ilkesini ve bileşen kaynaklarını açıkça dahil eder. Çalışma dizininde ilkenin bulunması tek başına dağıtım arşivinin doğru olduğunu kanıtlamaz. `scripts/verify_native_package.py` bunu denetler.

Kaynak katmanı veya commit değişince makbuzu yenile ve yalnızca gerekli artımlı derlemeyi çalıştır. Aynı kaynak ağacında rakip build başlatma. Tam uygulanmış kaynak arşivi, nesne/cache dizinlerini dışarıda bırakır. Eksik/yarım arşivi dağıtma.

## Kalan sıradaki işler

1. **Tamamlandı:** gerçek Linux paketi ayrı klasöre çıkartılıp yeni profilde 11 senaryoyu geçti; bütün uygulanmış motor kaynakları arşivlendi. Tarayıcının iki ve kaynağın on bir kayıpsız aktarım parçası özel Drive'dan geri okunarak doğrulandı. Özetler `docs/VALIDATION.md` içinde. GitHub asset yüklemesi HTTP 401 verdi; Release taslağı yayımlanmadı. İndirme yayını için bu yetkilendirme sorunu hâlâ açık.
2. Yerelleştirme: bütün Firefox dilleri hedeflenir; mevcut native deneme paketi en-US, Aion TR/EN. Dil paketlerini ve çalışma anında değiştirmeyi bağımsız kimlikle doğrula.
3. Mozilla hesabı/Sync, Safe Browsing ve CDM hizmet erişimi: tercih/ilke testinden ayrı gerçek davranış denetimi gerekli. Ortamda bazı Mozilla ağ istekleri başarısız; çalışıyor varsayma.
4. Projeye ait imzalı güncelleme hizmeti, MAR sertifikaları, kanal/mimari, iki gerçek sürümle veri koruma ve bozuk imza/kesik indirme testleri. `--disable-updater` ile kararlı sürüm çıkarma.
5. [docs/FEATURES.md](docs/FEATURES.md) açıklarını sırayla tamamla. Bitwarden/DeepL eşdeğerliği, Netflix kalite, tüm iframe'ler ve QR henüz tamamlanmış değildir.
6. Diğer platformlar ve bağımsız güvenlik/erişilebilirlik incelemesi. Sahte Setup.exe, .dmg, APK veya iPhone paketi üretme.

## Git ve yedek

Her başarılı push sonrası `python3 scripts/backup.py`: kaynak ZIP, bütün erişilebilir Git geçmişi bundle'ı ve UTC/İstanbul tarihli commit makbuzu. Kullanıcının özel proje klasörüne yükle; geri indirip SHA-256, ZIP CRC ve git bundle doğrula. Önceki yedekleri koru; gizli anahtarları dahil etme.

Hedef: https://drive.google.com/drive/folders/1hQIvdaWDiM0I1c77mkUEhYhdOCqTbdmw (ebeveyn `1cZxRqTob2e53E6ilMkND782KhIwXnMVJ`). Yalnızca sahip izni ve paylaşılmamış durum yeniden kontrol edildi.
