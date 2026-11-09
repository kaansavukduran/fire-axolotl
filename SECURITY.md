# Güvenlik / Security

Fire Axolotl şu anda geliştirici önizlemesidir. Bağımsız kurulum, güvenli güncelleme ve güvenlik denetimi tamamlanmadan günlük kullanım için önerilmez. / Fire Axolotl is a developer preview. Independent installation, secure updating and security review must be completed before everyday use.

## Korunan sınırlar / Preserved boundaries

- Firefox kaynak motoru, işlem yalıtımı, site yalıtımı, TLS sertifika doğrulaması, izleyici koruması ve indirme korumaları temel alınır. Motor güvenlik korumalarını kapatan bir tercih eklenmez. / Preserve upstream process/site isolation, TLS verification, tracking and download protections.
- Üçüncü taraf eklenti ve dil paketi imza doğrulaması açık kalır. Aion, derleme içindeki kaynaklardan yerleşik modül olarak yüklenir. / Third-party extension and language-pack signature checks remain enabled; Aion is a packaged built-in.
- Aion, başlangıçta bütün siteleri okuma izni istemez. Video ve seçim araçları açık kullanıcı eylemiyle etkin sekmede çalışır. / No mandatory all-sites read permission; page access requires an explicit action on the active tab.
- Konteyner, depolama ve ağ işlemleri yalnızca Aion'un kendi panel/ayar sayfalarından gelen mesajları kabul eder. Web sayfasından gelen içerik mesajları bu yetkileri kazanamaz. / Privileged actions accept messages only from the companion UI, not content scripts or pages.
- Çeviri yalnızca seçilen HTTPS alan adına, izin kontrolünden sonra, kimlik bilgileri olmadan gider. Yönlendirme takip edilmez, bekleme süresi sınırlıdır. Uzak kod çalıştırılmaz. / Translation checks the explicit HTTPS-origin permission, omits credentials, refuses redirects, times out and never executes remote code.
- Sayfa metinleri ve altyazılar HTML olarak işlenmez; metin düğümleri kullanılır. / Page and subtitle text is rendered as text, not HTML.
- İçe aktarılan yedek ağ izni vermez ve güvenilen çeviri adresini değiştirmez. / Backup imports neither grant network permission nor replace the trusted endpoint.

## Sınırlar / Limits

Konteynerler bir VPN değildir. Geçici konteynerin temizlenmesi indirilen dosyaları ve geçmişi silmez. Reklam/izleyici koruması tam zararlı yazılım koruması anlamına gelmez. Sitelerin bütün video oynatıcıları ve DRM sistemleri desteklenmez. / Containers are not a VPN; temporary cleanup does not erase downloads/history. Blocking is not complete malware protection. Site players and DRM support vary.

Safe Browsing, CDM/Widevine, Sync ve diğer Mozilla/üçüncü taraf hizmetlerinin bağımsız ürün üzerindeki erişim, anahtar, lisans ve çalışma koşulları sürümden önce doğrulanmalıdır. Tercihin açık olması hizmetin sorunsuz çalıştığının kanıtı değildir. / Service access, keys, licensing and actual behavior must be verified for an independent product; enabled preferences do not prove functionality.

## Sürüm kapısı / Release gate

Geliştirme yapılandırması güncelleyiciyi kapatır; Mozilla'nın güncellemesini bağımsız ürüne yanlışlıkla kurmak çözüm değildir. Kararlı paketler; projeye ait imzalama, güncelleme hizmeti ve eski sürümden veri koruyarak yükseltme testi tamamlanmadan yayımlanmamalıdır. / Stable packages are blocked until project signing, update hosting and a data-preserving upgrade test are complete.

Gizli veri içeren güvenlik raporlarını herkese açık issue olarak paylaşmayın. Depoda özel güvenlik bildirimi etkinleştirilirse GitHub Security → Report a vulnerability yolunu kullanın. / Do not put sensitive reports in public issues. Use GitHub private vulnerability reporting if enabled for this repository.
