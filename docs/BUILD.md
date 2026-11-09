# Derleme ve dağıtım / Build and distribution

Python 3.12+, Node 22+ ve Firefox'un ilgili platform için resmi derleme araçları gerekir. Bootstrap, ağdan büyük araç zincirleri indirir. Tam derleme için en az 16 GB RAM ve yaklaşık 60 GB boş alan önerilir. / Requires Python 3.12+, Node 22+ and Mozilla's platform build prerequisites. Bootstrap downloads large toolchains. Recommended: at least 16 GB RAM and approximately 60 GB free disk.

Kaynak indirme betiği SHA-512 doğrulaması yapar ve dolu hedef dizine çıkartma yapmaz. `upstream.json` sürümü değiştirildiğinde yeni özeti resmi Mozilla kaynağından kontrol et, kaynak değişikliklerini gözden geçir ve testleri yeniden çalıştır. Günlük Actions kontrolü yeni ESR sürümünde hata vererek bakım ihtiyacını görünür kılar; bu bir otomatik yama veya anında güvenlik garantisi değildir.

The source fetcher verifies SHA-512 and refuses non-empty destinations. Review source changes and checksums on every upstream update. A daily Actions job fails when the ESR pin becomes stale; it does not automatically patch or guarantee immediate maintenance.

## Kaynak katmanı / Source overlay

`scripts/prepare_source.py`:

1. Beklenen `version_display.txt` sürümünü doğrular. / Verifies the expected version.
2. Aion ve doğrulanmış uBlock Origin modüllerini `builtin-addons` kaynaklarına ekler; uBO'nun tam ilgili kaynaklarını dağıtım dizinine koyar. / Adds Aion and verified uBO through the native registry and ships uBO's corresponding source.
3. Unofficial markalamadan bağımsız Fire Axolotl varlıklarını üretir; Mozilla kaynak telif bildirimlerini korur. / Creates independent branding while retaining upstream source notices.
4. Ayrı uygulama kimliği, adı, profil yolu ve uzak süreç adı kullanır. / Uses a separate app identity, profile path and remoting name.
5. Yeni ayarlar düzeninde Ayarlar → Görünüm, eski düzende Genel bölümüne sekme, font, site rengi ve araç çubuğu kontrollerini ekler. / Adds controls to Appearance in redesigned settings, General in legacy settings.
6. Etkin ilkelerle proxy kaynağı okunurken oluşan upstream sözlük/dizi hatasını düzeltir. / Fixes upstream policy-dictionary handling in ServiceRequest proxy-source detection.
7. BrowserGlue başlangıç kaydını yeni uygulama kimliğine bağlar; uzaktan otomasyonun tarayıcı ailesi denetiminin kendi kimliğimizi tanımasını sağlar. Başka Gecko uygulamalarına ait kontroller korunur. / Updates BrowserGlue's app-startup guard and remote browser-family recognition for the independent application ID.

`Native Linux developer build (not a stable release)` adlı elle başlatılan Actions akışı; tam kaynak derlemesi, ayrı profilde `tests/native_smoke.py`, gerçek paket denetimi ve bütün uygulanmış motor kaynaklarının arşivlenmesini birleştirir. Yerel test geçmezse tarayıcı paketi yüklemez. Akışın depoda bulunması, başarılı bir derleme veya yayımlanmış sürüm anlamına gelmez. / The manual native workflow builds, tests and packages the actual fork with full applied source. A workflow definition is not evidence of a successful build.

```sh
AION_NATIVE_BINARY=/path/to/obj-fire-axolotl/dist/bin/fire-axolotl AION_GECKODRIVER=/path/to/geckodriver python3 tests/native_smoke.py
python3 scripts/verify_native_package.py /path/to/fire-axolotl-version.en-US.linux-x86_64.tar.xz
python3 scripts/archive_applied_source.py /path/to/prepared-source dist/fire-axolotl-applied-source.tar.zst
```

Standart `mach bootstrap`, `mach build`, `mach run` ve `mach package` girişleri kullanılır. `--disable-updater`, imzalama anahtarları ve gerçek güncelleme hizmeti hazır olmadığı için geliştirme yapılandırmasındadır. Bu yapılandırmayla üretilen dosya kararlı günlük kullanım paketi olarak yayımlanmamalıdır. / The development config disables the updater until independent signing and update hosting exist; do not publish that build as a stable daily-use browser.

## Platform durumu / Platform status

| Platform | Hedef / Target | Durum / Status |
| --- | --- | --- |
| Windows x64 / ARM64 | İmzalı Setup.exe / signed Setup.exe | Henüz derlenmedi, temiz kurulum ve imzalama bekliyor. / Build, signing and clean-install validation pending. |
| Linux x64 / ARM64 | AppImage, mümkünse .deb / AppImage and preferably .deb | x64 tam kaynak derlemesi, `.tar.xz` ve arşivden açılış geçti. AppImage/.deb ve ARM64 henüz üretilmedi. / x64 source build, tar package and extracted-package startup passed; AppImage/.deb and ARM64 pending. |
| macOS Apple Silicon / Intel | Developer ID imzalı ve notarized .dmg / signed, notarized .dmg | macOS derleyici ve Apple imzalama hesabı gerekli. / macOS build host and Apple signing required. |
| Android | Ayrı kimlik ve kalıcı imzayla APK / separate identity and stable signing | GeckoView tabanlı mobil ön yüz henüz oluşturulmadı. / GeckoView mobile front end pending. |
| iPhone | App Store / TestFlight | iOS ön yüz, uygun motor/dağıtım koşulları, Apple hesabı ve inceleme gerekli. Masaüstü kaynağı doğrudan iPhone paketi değildir. / Requires an iOS front end, applicable engine/distribution terms, Apple account and review. |
| Web | Ürün web sitesi ayrı olabilir. / A separate product website is possible. | Web sayfası Firefox motorlu kurulu tarayıcının yerine sunulmaz. / A web page is not a substitute for the installed browser. |

## Güncelleme teslim koşulları / Update release requirements

1. Mozilla güvenlik yamalarını al, kaynak pinini ve uygulama sürümünü birlikte izle. / Track browser and upstream versions separately.
2. Projeye özel MAR imzalama sertifikalarını derlemeye yerleştir; özel anahtarları Git veya Drive kaynak arşivlerine koyma. / Embed project-specific public MAR certificates; never archive private keys.
3. HTTPS üzerinden doğru platform/mimari/kanal güncelleme XML'i ve imzalı MAR dosyası sun. / Host targeted update XML and signed MAR files over HTTPS.
   Windows/macOS ve yazılabilir Linux kurulumlarında Firefox güncelleyicisi temel alınabilir. Salt okunur AppImage için imzalı tam dosya değişimi, .deb için uygun paket kanalı ayrıca tasarlanmalıdır. / Writable desktop installations may use the native updater; read-only AppImages need signed whole-image replacement, and .deb packages need their package-channel update strategy.
4. Kullanıcı kontrolü, değişiklik notları, boyut, “Güncelle ve yeniden başlat” ve “Daha sonra” akışını Firefox güncelleyicisine bağla. / Connect the user flow to the native updater.
5. Eski imzalı paketi temiz kur, örnek kayıtlarla yeni imzalı pakete uygulama içinden yükselt. Parolalar, konteynerler, ayarlar ve kelimeler korunmalı. Kesik indirme ve hatalı imzada kurulum başlamamalı. / Validate a real two-package upgrade, data preservation and failure handling.
6. Bütün platformların doğrulama sonuçlarını ve doğrudan indirmeleri Release sayfasında yayımla. Mağaza bağlantılarını da ekle. / Publish verified installers and store links in Releases.
   İlgili sürümün bütün uygulanmış kaynaklarını ve lisans bildirimlerini de arşivle; yalnızca değişiklik listesi veya ileri tarihli bir indirme bağlantısına güvenme. / Archive complete corresponding applied source and notices for that release rather than relying only on patches or future download availability.

Bu maddeler tamamlanmadan “Firefox gibi güncelleme çalışıyor” iddiası kullanılmaz. / Do not claim Firefox-like updates work until verified.
