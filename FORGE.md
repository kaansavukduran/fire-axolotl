# Yayımlanan Linux ön sürümü / Published Linux preview

- **Yayımlandı:** [v0.1.0-dev.20261109](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.1.0-dev.20261109), 2026-11-09 19:28 UTC. Pre-release; Latest/kararlı değildir.
- Paketleme commit'i ve etiket hedefi `92e30af0ac76f6aafbd322f9c78b0e68926af98f`; native kaynak `0f94fea2429d578015acc0a6494fe8c2dbd5223a`.
- [Yayın akışı 42682284085](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42682284085) başarılı: 29 birim/gerileme, 4 AppImage/paket eşleşmesi, gerçek `.deb` kurulumu, kurulu programda 11 açılış ve 4 yeniden başlatma kontrolü. Native derleme ayrıca 34 entegrasyon senaryosunu geçti.
- 15 gerçek indirme dosyası: AppImage, `.deb`, native `.tar.xz`, tam motor/paketleme/destek kaynakları, lisans ve test makbuzları. Sunucu SHA-256 özetleri yayın öncesinde denetlendi.
- Doğrudan yerel asset yüklemesinin HTTP 401 engeli, yalnızca yayın işi için yetkili Actions kimliği kullanılarak çözüldü. Önceki yedekler korundu.
- Otomatik güncelleme kapalı, native arayüz en-US, Aion TR/EN. Diğer platformlar, diller, gerçek Sync/hizmet erişimi ve özellik eşlemesindeki açıklar devam ediyor.

## Yayın hazırlığının kaydı / Publication staging record

- Dal: `main`; native tarayıcı kaynağı `0f94fea2429d578015acc0a6494fe8c2dbd5223a`.
- İlk hedef: `v0.1.0-dev.20261109`, yalnızca Linux x86_64 geliştirici önizlemesi. Kararlı/Latest değildir; otomatik güncelleyici kapalıdır.
- Native GitHub çalıştırması `42666129157` tam derleme, 11 ilk açılış, 34 entegrasyon, 4 yeniden başlatma ve paket denetimini başarıyla tamamladı.
- Yeni paketleme için 29 birim/gerileme kontrolü ve gerçek AppImage girişinden 4 kurulum kontrolü yerelde geçti. AppImage Aion/uBO'yu etkin yerleşik bileşen olarak açtı; TR Aion ayarları ve iki paketin native dosya eşleşmesi doğrulandı.
- `.deb` temiz kurulumu ve kurulu programdan native testler, `Publish tested Linux developer preview` akışının zorunlu yayın kapısıdır. Bu aşamalar geçmeden Release yayımlanmaz.
- `release.json` kaynak commit/run/tag pinlerini; `linux-packaging.json` paketleme araçları ve runtime/kitaplık kaynak özetlerini tutar. Runtime/kitaplık lisansları paketlerde, ilgili kaynaklar ayrı destek arşivinde korunur.
- Yayın akışı yalnızca tamamlanmış, doğru depoya ait main/manual native çalıştırmasını kabul eder. Paketleme ve yayımlama işleri ayrıdır. Yalnızca yayımlama işi contents:write alır; eski yayımlanmış sürüm ve varlıklar değiştirilmez.
- Türkçe native kaynak denemesi PR #1'de ayrı kalır ve bu pakete girmez. Aion TR/EN, native tarayıcı en-US. Diğer işletim sistemleri ve özellik eşlemesindeki açıklar devam eder.
- Yayın akışı main'e gönderildikten sonra elle çalıştırılmalı; gerçek sonuç ve Release URL'si kontrol edilmeden yayın tamamlandı denmez. Her push ve yayımlanan sürüm için özel Drive yedeği gerekir.

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

1. **Tamamlandı:** Linux ön sürümü AppImage/`.deb`, tam ilgili kaynaklar ve özetlerle yayımlandı. Yukarıdaki yayın kaydı günceldir; aşağıdaki eski yerel arşiv özetleri ayrı doğrulama kaydıdır.
2. Yerelleştirme: bütün Firefox dilleri hedeflenir; mevcut native deneme paketi en-US, Aion TR/EN. Dil paketlerini ve çalışma anında değiştirmeyi bağımsız kimlikle doğrula.
3. Mozilla hesabı/Sync, Safe Browsing ve CDM hizmet erişimi: tercih/ilke testinden ayrı gerçek davranış denetimi gerekli. Ortamda bazı Mozilla ağ istekleri başarısız; çalışıyor varsayma.
4. Projeye ait imzalı güncelleme hizmeti, MAR sertifikaları, kanal/mimari, iki gerçek sürümle veri koruma ve bozuk imza/kesik indirme testleri. `--disable-updater` ile kararlı sürüm çıkarma.
5. [docs/FEATURES.md](docs/FEATURES.md) açıklarını sırayla tamamla. Bitwarden/DeepL eşdeğerliği, Netflix kalite, tüm iframe'ler ve QR henüz tamamlanmış değildir.
6. Diğer platformlar ve bağımsız güvenlik/erişilebilirlik incelemesi. Sahte Setup.exe, .dmg, APK veya iPhone paketi üretme.

## Git ve yedek

Her başarılı push sonrası `python3 scripts/backup.py`: kaynak ZIP, bütün erişilebilir Git geçmişi bundle'ı ve UTC/İstanbul tarihli commit makbuzu. Kullanıcının özel proje klasörüne yükle; geri indirip SHA-256, ZIP CRC ve git bundle doğrula. Önceki yedekleri koru; gizli anahtarları dahil etme.

Hedef: https://drive.google.com/drive/folders/1hQIvdaWDiM0I1c77mkUEhYhdOCqTbdmw (ebeveyn `1cZxRqTob2e53E6ilMkND782KhIwXnMVJ`). Yalnızca sahip izni ve paylaşılmamış durum yeniden kontrol edildi.
