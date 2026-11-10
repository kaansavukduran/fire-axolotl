# Güncel başarılı test kapısı hedefi: Windows yeniden doğrulama

- Motor ve kaynak run 42791204074, kaynak SHA 9d564dced55dc4816cc4aeb57387ba1643f007ed olarak korunur. Testler [42808841079](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42808841079) üzerinde, 6ca1932d36605aa327ea005c2474aa8f0cae1ec4 doğrulama kaynaklarıyla yeniden koşar. Workflow ID 413213938; path windows-revalidate.yml. Yayın başarılı doğrulama SHA/run’ını ve aynı ZIP/Setup/source hashlerini zorunlu tutar.
- Yayın indiricisi native payload ve tam kaynağı 42791204074’ten, test kanıtını 42808841079’dan alır. Motor girdileri değişmemiştir. Doğrulama tamamlanmadan Windows hazır/yayımlandı denmez.

# Derlenmiş Windows paketinin ayrı yeniden doğrulaması

- 42791204074: gerçek NSIS installer, 11 açılış ve 4 restart başarılı. Windows OS hareket azaltma tercihi açıkken E2E animasyon beklediği için 434. satırda durdu. Test profili normal hareketi 0, azaltılmış hareketi 1 ile ayrı ve açıkça doğrular; ürün/OS tercihi değiştirilmez.
- `windows-revalidate.yml` sabit 42791204074/9d564dc paketini ve kaynaklarını indirir. `windows_revalidate.py` depo/dal/commit/workflow, başarılı compile/package/installer/source adımları, değişmemiş motor girdileri, native paket güvenliği ve tam kaynak makbuzunu denetler. 11/4/34/11/5 testleri bu gerçek pakette yeniden koşar. Motor yeniden derlenmez.
- Yayın yalnızca başarılı, kesin SHA/ID ile sabitlenen yeniden doğrulama çalıştırmasını kabul eder. İndirilen ZIP, Setup ve motor kaynağının özetleri bu çalıştırmanın makbuzuyla birebir eşleşmelidir. Kaynak/paket eski build run’ından, başarılı test kanıtı yeni doğrulama run’ından gelir. Kurulu Windows paketinin ayrı testleri de zorunlu kalır.

# Güncel Windows run: 42791204074

- Native kaynak `9d564dced55dc4816cc4aeb57387ba1643f007ed`; [42791204074](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42791204074). CRLF testi ve gerçek installer artifact yolu düzeltildi; JSON ve üç artifact pini bu yeni çalıştırmaya eşlendi.
- 42772444157 başarısız tarihsel kayıttır; native 11 ve restart 4 geçmesine rağmen integration başlangıcında durduğundan yayıma uygun değildir. Yeni run ve kurulu Windows kontrolleri tamamlanmadan Setup hazır sayılmaz.

# Windows CRLF doğrulaması ve installer artifact yolu

- Native run 42772444157: derleme/paketleme, 11 ilk açılış ve 4 gerçek yeniden başlatma geçti. Entegrasyon başlangıcındaki kaynak karşılaştırması Windows CRLF nedeniyle durdu. Artifact 13745750409 içindeki gerçek root omni.ja modülünde düzeltilmiş kodun bulunduğu, LF normalize edilince eski kodun bulunmadığı doğrulandı. Test yalnızca CRLF→LF normalizasyonu ekler; kod ve davranış denetimleri korunur.
- Upstream packager.mk make-package hedefi Windows installer'ı zaten üretir. Önceki artifact glob'u eski install/sea yoluna bakıp installer'ı kaçırıyordu. Doğru dosya dist/*.installer.exe; dosya sayısı/boyutu paketleme sonrası ayrıca doğrulanır. XPT yardımcı ZIP'i native tarayıcı ZIP'i olarak yüklenmez.
- Tam kaynak artifact 13745107512 bu denemede testlerden önce korunmuştur. Yeni native run, yayın JSON ve artifact pinleriyle eşlenmeden yayımlanamaz. Eski başarısız run yayın için kabul edilmez.

- Son yerel doğrulama: snapshot yardımcısıyla native smoke 11 geçti. Dil seçicisi için yalnızca görünürlük beklemek yeterli değildi; test artık UI.init sonrası render edilen sürüm alanını bekler. Ürün verileri/izinleri değiştirilmez.

# Güncel Windows doğrulama çalıştırması

- Native kaynak `a56d740acf86f57fd6892234c29ce9a2e12debf7`; [run 42772444157](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42772444157). 42729988254 ilk motor paketini üretti fakat screenshot testinde başarısız oldu; yayın için kabul edilmez.
- Yayın JSON ve üç artifact indirme pini yeni run’a eşlendi. Tam başarılı native testler ve gerçek Setup kurulumu geçmeden yayın yapılamaz. Nesne cache anahtarı korunur; gizlilik, TLS, sandbox ve imza denetimleri değiştirilmedi.

# Windows derleme sonrası ekran görüntüsü hatası

- Run 42729988254 motoru ve ZIP/native NSIS paketini başarıyla üretti. Native smoke ilk 7 kontrolü geçti; yan panel açıldıktan sonraki screenshot, Windows headless compositor `Unable to capture screenshot` hatasıyla durdu. Bu nedenle run başarısız ve yayın yapılmadı. Native payload artifact 13731801476 korundu; D:/o cache 1659208500 bayt olarak başarıyla kaydedildi.
- Ekran görüntüsü yardımcısı yalnızca bu belirli yakalama hatasında en çok 3 kez, 250ms arayla dener. Kalıcı ve ilgisiz hatalar yine testi durdurur. İki hata davranış testi ayrı Selenium ortamında koşar; ürünün güvenlik ayarları değiştirilmez.
- Tam ilgili kaynak arşivi artık testlerden önce saklanır. Sonraki test hatasında motor kaynağı kaybolmaz. Yeni native çalıştırma en-US/tr ve sağ sekme düzeltmesi dahil güncel main kaynaklarını kullanır. Yayın pinleri yeni run başladıktan sonra onun kesin SHA/ID'sine eşlenmelidir.

# Native Türkçe dil desteği / Native Turkish localization

- Native arayüz için en-US ve sabit özetli Türkçe dil kaynakları paketlenir; `intl.locale.requested` varsayılanı boş bırakılarak işletim sistemi tercihi izlenir. Kullanıcının dil seçimi değiştirilmez. Diğer Firefox dillerinin dağıtımı henüz tamamlanmadı.
- Dil paketinin eski denemesindeki `default_locale` alanı langpack şemasınca reddediliyordu. Düz metin ad/açıklama ve bağımsız kimlikle düzeltildi. Özgün çeviriler/atıflar korunur; değiştirilmiş türevde Mozilla imzaları taşınmaz. Harici paket imza denetimleri açık kalır. Kaynak XPI + MPL + türetme betiği/pin/marka kaynakları ayrı `fire-axolotl-localization-source.zip` içinde dağıtılır.
- Gerçek derlenmiş Linux forkunda native Ayarlar seçicisi TR→EN ve iki gerçek süreç yeniden başlatma dahil 5 senaryoyu geçti. Dil, dikey sekmeler, OpenDyslexic ve oyun rekoru korundu. Özel Görünüm etiketleri canlı dil değişimine uyar.
- Doğrudan üst→sağ sekme seçiminde eşzamanlı pref gözlemcisi seçim kutusunu sıfırlayabiliyordu. İşlem başında seçilen konum saklanır; bu yol native dil/persistans testinde doğrulandı.
- Windows paketleme aynı derlenmiş motorun yalnızca browser/omni.ja veri kaynaklarını günceller: çeviri verisi, katalog girdisi ve tek OS-dil varsayılanı. Motor, ilkeler ve mevcut Aion/imzalı uBO korunur. Kaynak farkı koruyucusu yalnızca incelenen kaynak hazırlama ve tercih eklemelerini kabul eder. Kurulu Windows'ta 5 native dil senaryosu yeni zorunlu yayın kapısıdır.
- 22 Node + 18 Python kontrolü geçti. Yeni katmanda önceki native smoke 11 geçti; son entegrasyon/oyun sonuçları ayrı kaydedilir. Native Windows 42729988254 derlemesi devam ediyor; Setup henüz üretilmedi. Native workflow değiştirilmedi, yeni motor derlemesi başlatılmadı.

# Aion yeni sekme oyunu / Aion new-tab game

- Görünüm yerleşimi: Lit `setting-pane.name` özelliği HTML niteliğine yansıtılmadığından eski `[name=...]` seçicisi paneli bulamıyordu. JS özelliğiyle seçilir; özel grup artık native Görünüm panelinden sonra yerleşir. Gerçek forkta sıralama ve 11 native smoke geçti; installed smoke bu sıralamayı da denetler. Sekme/font/gizlilik işlevleri korunur. Boşluk basılı tutulurken tekrarlanan olaylar da sayfayı kaydırmaz.
- Güncel native kaynak `7bbc53a6a388476ecd9c3e4a795f75bf834a2196`; [Windows çalıştırması 42729988254](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42729988254) kısa kök ve cache ile başlatıldı. Yayın JSON ve üç artifact indirme pini bu run’a eşlendi. Bu kayıt sırasında derleme sürüyor; Windows Setup henüz yok. Önceki 5d/427099 derlemesi başarısız tarihsel kayıttır.

- Son gözden geçirmede gerçek bir klavye zıplamasıyla engel aşıldı ve kazanılan rekor yeni sekmede korundu. Arama kutusu kapalıyken oyun görünür; kullanıcının tamamen boş yeni sekme seçimi korunur. `native_runner.py` artık 11 senaryoyu geçti; kurulu Windows yayın kapısı da 11 ister. Son yerel birim toplamı 22 Node + 16 Python; önceki 11 native smoke + 4 restart da oyun katmanıyla geçti.
- Windows çalıştırması 42709930229, 117m derleme sonunda `goog_cc_scream_network_controller_gn/...obj` için "No rule to make target" hatası verdi; ZIP/Setup üretilemedi. Uzun Windows kökünün göreli nesne yollarıyla birleşmesi incelendi. Sonraki kaynak `D:/s/firefox-153.6.0`, nesneler `D:/o`; uzun kaynak/çıktı kökleri kaldırıldı. Tam birim sonuç henüz yeni çalıştırmadan bekleniyor.
- Native workflow dosyası main'e değişince kontrollü olarak yeni motor derlemesi başlar; yayın ön kontrolü yalnızca tam sabitlenen başarılı main/manual veya main/push çalıştırmasını kabul eder. Yeni run başladıktan sonra `windows-release.json` ve artifact indirme pinlerini onun kesin kaynak SHA/run ID'sine güncelle. Başarısız eski run ile yayın yapılamaz.
- Yeni native denemede tamamlanmış/yarım nesneler `actions/cache` ile saklanır; cache kaydı başarısız olsa da derlenmiş ve test edilmiş paketi geçersiz kılmaz. Kaynak/çıktı kökü sabit kalır. Oyun native kaynakta zaten aynıysa kaynak katmanı ve ZIP değişmeden korunur; dış SFX yeniden markalanırken iç 7z/NSIS yükü de korunabilir.
- Kullanıcının Aion ana referansı ve paftasından uygulama için özgün piksel pafta üretildi: `browser/native/aion-runner/aion-runner.png`, 6 sütun × 8 satır, 48 kare. PNG değiştirilmeden saklanır; kaynak/özet `PROVENANCE.json` içinde. Google Dino kodu veya varlıkları kullanılmadı.
- Firefox'un mevcut araması ve kısayolları korunur; normal `about:newtab` / `about:home` sayfasına ayrı kart eklenir. Başlat, Boşluk/dokunma, Esc, sekme geçişinde duraklatma, buz/ateş/kül, yerel rekor, gizle, native Görünüm ayarlarında göster/TR/EN/rekor sıfırlama var. Başka eklentinin yeni sekmesine müdahale edilmez; web sayfalarına aktör yüklenmez.
- Gerçek yayımlanmış Linux motorunun ayrı kopyasına yalnızca `browser/omni.ja` arayüz kaynakları uygulandı. `tests/native_runner.py` normal tarayıcıda 9 senaryoyu geçti. Görüntüler `docs/screenshots/aion-runner-*.png`; taslak/maket değildir. 22 Node ve 16 Python kontrolü beklenen güncel toplamdır; son çalıştırmayı kayıtla doğrula.
- `runner_overlay.py` motor/politika/yerleşik eklenti değişikliklerini reddeder; kaynak hazırlama betiğinde yalnızca 3 kaynak kopyalama satırını kabul eder. Değişen her arayüz kaynağı ve değişmeden kalan native dosyalar hash ile denetlenir. Windows ZIP ve Setup aynı arayüz yükünü kullanmalı; kurulu oyunun 9 testi yayın öncesi zorunludur.
- Windows SFX kabuğu [42723028131](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42723028131) ile VS 2022 üzerinde başarıyla derlendi. LZMA SDK 18.05 kaynak/atfı korunur, Aion simgesi ve kendi ürün adı kullanılır. Oyun için 7z arşivi tekrar paketlenir; iç native NSIS setup.exe değiştirilmez. Kurulum testi bütün kurulu dosyaları güncel ZIP ile karşılaştırır.
- Shell GitHub kimliğinin süresi doldu; bağlı GitHub uygulaması kullanılabilir. Yeni kaynak gönderimini bu uygulamanın blob/tree/commit/ref API'siyle tamamla; `source-sync.yml` ürettiği tam Git bundle'ını indirip yerel dalı ve per-push Drive yedeğini kesin commit'e eşle. Ana motor derlemesini yeniden başlatma.

# Windows geliştirmesi / Windows development

- Driver Booster / WinOptimizer tarama, onarma ve sürücü güncelleme talepleri kullanıcı tarafından yanlış proje olarak geri çekildi; tarayıcı kapsamına dahil değildir.
- Dış 7z kurulum kabuğundaki Firefox simgesi tespit edildi. `windows_sfx.py`, paketteki kamu malı LZMA SDK kaynağından Aion simgeli kendi kabuğumuzu derler; native 7z yükünün tamamını değiştirmeden korur. İlgili SDK kaynağı ve özet makbuzu ayrıca dağıtılır. Windows'ta gerçek derleme/kurulum sonucu henüz bekleniyor; motor çalıştırması iptal edilmez.
- Güncel hedef: Windows x64 için gerçek tam motor derlemesi ve kullanıcı hesabına kurulan çevrimdışı `Setup.exe`. Linux ön sürümü korunur; Windows dosyası mevcut olduğu varsayılmaz.
- `native-windows.yml`, Windows Server 2022 üzerinde doğrulanmış MozillaBuild 4.2.1, sabit geckodriver ve aynı Firefox kaynak katmanını kullanır. Defender dışlaması eklenmez; TLS, tarayıcı kum havuzu ve eklenti imzaları kapatılmaz.
- Derlenen ZIP, sonraki paketleme/test hatasında motoru yeniden derlemek gerekmemesi için ayrı artifact olarak saklanır. Gerçek Windows'ta 11 ilk açılış, 4 yeniden başlatma ve 34 entegrasyon kontrolü zorunludur.
- Windows kullanıcı kurulumu kendi uygulama/dizin/kaldırma kimliğini kullanmalı; Firefox profilini taşımamalı, kendini varsayılan tarayıcı yapmamalı ve kaldırmada kullanıcı profillerini silmemeli.
- Authenticode sertifikası ve imzalı güncelleme kanalı henüz yoktur. Yalnızca açıkça etiketlenmiş geliştirici Pre-release çıkarılabilir. `Setup.exe` üretimi ve temiz kurulum doğrulanmadan Windows hazır denmez.
- Windows'ta Git satır sonları hem kök depoda hem uBO/uAssets kaynak indirmesinde korunur; npm test keşfi Windows komut satırına uyarlandı. Yerelde 19 Node + 14 Python kontrolü geçti.
- `windows-preview-release.yml` yalnızca sabitlenmiş, başarılı main/manual native çalıştırmasının dosyalarını kullanır. Kurulum paketi ve tüm native dosya özetleri, Başlat kısayolu, ayrı varsayılan profil, 11/4/34 kurulu program senaryosu ve veri koruyan kaldırma geçmeden yayın işi başlamaz.
- Native bootstrap artık MozillaBuild giriş kabuğunda çalışır; sessiz configure hatalarının tanısı `windows_mach.py` ile korunur. Dev Drive önerisi CI'da kapalıdır; güvenlik hizmetleri kapatılmaz.
- Windows default-agent ilke okuyucusunun JSON anahtarındaki büyük/küçük harf hatası kaynak katmanında düzeltildi. `DisableDefaultBrowserAgent` gönderilir; gerçek Windows servisindeki `agentDisabled()` kurulum testinde doğrulanmalıdır.
- Son native kaynak: `5d48bca1cda33484c4346bc1f22ff9831314f19a`; [Windows çalıştırması 42709930229](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42709930229). Sonucu bağlantıdan denetle; bu kayıt yazılırken native build sürüyordu.
- `MOZ_AUTOMATION`, VCS içermeyen doğrulanmış kaynak arşivlerini reddettiği için bu geliştirici derlemesinde kullanılmaz. Bootstrap `--no-system-changes` ve `--no-interactive` ile çalışır.
- Native NSIS kurulum/kaldırma ping çağrıları, dış anketler ve launcher telemetri kaydı kapatıldı. SFX açılış başlığı da Fire Axolotl. İlgili kaynak yaması gerçek upstream NSIS dosyalarının ayrı kopyasında iki kez uygulanarak denetlendi.
- Başarılı native çalıştırma, Windows temiz kurulum/yayın akışını otomatik başlatır. Akış yalnızca yukarıdaki kaynak/run pinini kabul eder; native kaynak sonradan değişmişse yayın durur. Authenticode ve otomatik güncelleme hâlâ tamamlanmadı.

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
