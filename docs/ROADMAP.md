# Kullanıcı isteklerinin takibi / User requirements

Sıra, ilk konuşmadaki tarayıcı isteklerini izler. “Kısmi”, kullanılabilir bir bölümün bulunduğunu fakat isteğin tamamlanmadığını belirtir. Bir özelliği kaynakta korumak, bütün ağ hizmetlerinin bağımsız üründe doğrulandığı anlamına gelmez.

| Sıra | İstek | Durum ve sonraki adım |
| --- | --- | --- |
| 1 | Ücretsiz, açık kaynak gerçek Firefox forku ve güvenlik korumaları | 153.7 Windows/Linux gerçek kurulumları yayımlandı; her birinde 70 senaryo geçti. Kararlı dağıtım için imzalı güncelleme ve hizmet/ağ denetimi açık. |
| 2 | Eklenti kurmadan konteynerler | Kalıcı/geçici alanlar var; siteye otomatik alan atama kuralları açık. |
| 3 | Video hızlandırma | Erişilebilir ana belge videosunda var; ses, kısayollar ve bütün iframe'ler açık. |
| 4 | Video altyazısı, metin ve açılır içerik çevirisi | Yerel çift altyazı, mevcut satırı alma ve açık eylemle seçili metin çeviri akışı var. Otomatik altyazı çevirisi, canlı ses ve tüm açılır içerikler açık. |
| 5 | Aion karakterli özgün logo ve marka | Varlıklar ve kaynak bildirimleri var. Mozilla ile bağlantı iddiası yok. |
| 6 | Üst/sol/sağ seçilebilir sekmeler | Native testler geçti. Son düzeltmeye göre yeni profil varsayılanı üstte; kullanıcı seçimi yeniden açılışta korunur. |
| 7 | Firefox benzeri uygulama içi güncelleme | Elle Windows Setup 153.6 → 153.7 yükseltmesi ve veri koruma geçti. Açık: projeye ait imzalı MAR, sunucu, kanal/mimari ve uygulama içi imzalı yükseltme. Geliştirme yapısında güncelleyici kapalı. |
| 8 | Telif/lisanslara uygun ücretsiz dağıtım | MPL ve üçüncü taraf bildirimleri var; uBO'nun sabit kaynakları ve GPL kaynak arşivi dağıtılıyor. Bağımsız hizmet koşulları ve marka incelemesi devam eder. |
| 9 | Bitwarden, DeepL, DDG, YouTube araçları, uBO, görsel arama, karanlık sayfa, QR | Tek tek durumlar [FEATURES.md](FEATURES.md) içinde. Tam eşdeğerlik iddiası yok; tamamlanmayanlar listeden çıkarılmaz. |
| 10 | Hizmetin sunduğu daha yüksek video kalitesini seçme | Tercih ve deneysel YouTube isteği var. Netflix bağdaştırıcısı ve canlı hizmet testleri açık; DRM/abonelik sınırları aşılmaz. |
| 11 | Sade varsayılanlar, araç çubuğunu özelleştirme | Native düzenleyici, düğmeler, arama kutusu, boşluklar ve sıfırlama korunur. Ek hazır düzenler açık. |
| 12 | Koyu tarayıcı; sitenin temasını kullanıcıya bırakma | Gerçek medya sorgusu/CSS testleri geçti. Zorla sayfa karartma ayrı ve henüz açık. |
| 13 | Font ve disleksi seçeneği | Native font, OpenDyslexic/Lexend, ayrı Aion ölçeği/yazı boyutu var. Sitelerin fontu kendiliğinden değiştirilmez. |
| 14 | Firefox'un bütün dilleri, istediği zaman değiştirme | 103 resmî Firefox masaüstü dili paketlendi; normal seçici, DE/JA/AR/TR/EN, gerçek yeniden başlatma ve RTL testleri geçti. Aion'un TR/EN dışı çevirileri açık. |
| 15 | Firefox hesabı ve Sync | Kaynak ve hesap yeteneği korunur. Gerçek hesapla giriş/cihazlar arası eşitleme açık. |
| 16 | Firefox özellikleri; telemetri ve reklam ölçümü kapalı | İlkeler native profilde doğrulandı; 30 saniyelik başlangıç/yeni sekme ağ örneği alındı. Mozilla güvenlik/ayar/hizmet ve uBO filtre bağlantıları korunur. Kapsamlı ağ incelemesi ve bağımsız hizmet erişimi açık. |
| 17 | Kullanılabilir paket ve gerçek arayüz | Derlenmiş tarayıcı ekranları var. Günlük kullanım için kararlı sürüm henüz yok. Platformlar [BUILD.md](BUILD.md) içinde. |
| 18 | İsteğe bağlı karakterler ve kullanıcı karakteri ekleme | Aion/kuzu/kurt/baykuş resim kareleri, duraklatma, azaltılmış hareket, yerel PNG, silme ve yedek geri alma geçti. |
| 19 | Yeni sekmede özgün piksel Aion zıplama oyunu | 48 karelik pafta; Başlat, Boşluk/dokunma, Esc, buz/ateş/kül, yerel rekor, gizleme ve TR/EN. Gerçek engel aşma ve kazanılmış rekor dahil normal derlenmiş tarayıcıda 11 kontrol geçti. Arama/boş yeni sekme tercihleri korunur. Windows kurulu paket testi yayın kapısıdır. |
| 20 | Windows Setup.exe | [Windows x64 geliştirici ön sürümü](https://github.com/kaansavukduran/fire-axolotl/releases/tag/v0.1.0-dev.20261110-windows) yayımlandı. Gerçek Setup kurulumu, bütün paket dosyalarının eşleşmesi, kurulu uygulamada 65 senaryo, ayrı profil ve veri koruyan kaldırma geçti. Authenticode ve otomatik güncelleme açık. |

Yanlışlıkla başka uygulama için gönderilen spor, besin seçici ve RPG menüsü değişiklikleri bu projeye taşınmaz. Kullanıcının son düzeltmesiyle yalnızca tarayıcıya uygun karakter fikri kapsamda kaldı.

Driver Booster / WinOptimizer tarama, onarma ve sürücü güncelleme talepleri de kullanıcı tarafından yanlış proje olarak geri çekildi; Fire Axolotl kapsamına dahil değildir.

Öncelik: gerçek dağıtım arşivi doğrulaması → dil/hizmet uyumluluğu → imzalı güncelleme → açık özellik eşlemesi → platform paketleri. Her aşamada kanıt ve kalan sınırlar [VALIDATION.md](VALIDATION.md) içinde güncellenir; bir süreç yeniden başlatma testi, sürüm yükseltme testi yerine sayılmaz.
