# Aion 0.2 araçları

Aşağıdaki görüntüler gerçek 153.7 Linux tarayıcısında yeni 0.2 UI katmanından alındı; çizim veya arayüz maketi değildir. Sayfa, metin ve konteyner adları sentetik test verileridir. Adres çubuğundaki çizgili işaret otomasyon göstergesidir.

## Geniş çalışma alanı

Araç çubuğundaki Aion paneli 760 piksele kadar açılır. **Geniş ekranda aç** araçları normal sekmeye taşır. Çeviri, Konteynerler ve Video ayrı görevlerdir; başlangıçta seçilen web sekmesi üstte belirtilir. Bu görüntü tam sekme görünümüdür.

![Aion 0.2 Türkçe geniş çalışma alanı](screenshots/02-local-workspace-tr.png)

## Cihazda çeviri

**Aion → Çeviri → Cihazda çeviri aracını aç** yerel Firefox çeviri sayfasına gider. Desteklenen dillerin modelleri ilk kullanımda indirilir; ayrı sohbet modeli kurulu değildir. Aşağıdaki “Good morning → Günaydın” sonucu, ilk model indirmesi ve başka bir metnin çevirisi sonrasında tarayıcı çevrimdışına alınarak elde edildi.

![İnternet kapalıyken yeni metnin yerel çevirisi](screenshots/02-local-translation-offline.png)

## Büyük yazı ve dar pencere

Türkçe, OpenDyslexic, yüzde 200 yazı ölçeği ve dar pencerede alanlar alt alta yerleşir. Bunlar isteğe bağlı erişilebilirlik ayarlarıdır.

![Yüzde 200 ölçekli dar çalışma alanı](screenshots/02-local-workspace-tr-200.png)

[Kullanım kılavuzu](QUICK_START.md) · [Doğrulama ve sürüm durumu](VALIDATION.md)

Aşağıdaki Windows görüntüleri önceki 0.1 sürümünün yeni sekme, görünüm ve dil özelliklerini gösterir.

# Önceki Windows 0.1 arayüzü

2026-11-10. Bu görüntüler yayımlanmış Windows x64 Setup'ın kurduğu gerçek tarayıcıdan alındı: [başarılı kurulum/test/yayın](https://github.com/kaansavukduran/fire-axolotl/actions/runs/42849921106). Görüntülerin kaynak kanıt arşivinin SHA-256 özeti `2b967f0fd3cbeeccbf38d232c5f8cae9302aa4c4437388d0c2890ccbb2faf837`; ZIP CRC ve pikseller değiştirilmeden kopyalama doğrulandı. Bunlar taslak arayüz görselleri değildir.

Adres çubuğundaki çizgili işaret WebDriver otomasyonunun göstergesidir. Türkçe/Arapça örneklerindeki OpenDyslexic ve sağ sekmeler seçilmiş test ayarlarıdır; varsayılan font sistem fontu, sekmeler üsttedir. Yerel gizlilik ilkeleri nedeniyle Ayarlar'da görünen “kuruluşunuz tarafından yönetiliyor” bildirimi uzaktaki bir kuruluşu belirtmez.

## Yeni sekme ve Aion Koşusu

Oyun kullanıcı **Başlat** deyince çalışır. Boşluk/dokunma ile zıplama, buz/ateş animasyonları, sekme değiştirince duraklatma, yerel rekor ve gizleme bulunur. Bu erken başlangıç karesinde normal arama alanı henüz yükleniyor; arama motoru ve tıklama/klavye devri ayrıca doğrulandı.

![Windows'ta üst sekmeler, koyu yeni sekme ve Aion Koşusu](screenshots/1537-windows-newtab.png)

## Sekme konumu ve normal ayarlar

Görünüm bölümündeki yerel kontrollerden üst, sol veya sağ konum seçilir. Normal araç çubuğu düzenleyicisi, bağımsız site renk tercihi ve tarayıcı fontu korunur.

![Varsayılan üst sekmeler ve Görünüm kontrolleri](screenshots/1537-windows-tabs-top.png)

![İsteğe bağlı sağ sekmeler](screenshots/1537-windows-tabs-right.png)

## Diller ve erişilebilirlik

Ana tarayıcı 103 resmî Firefox masaüstü dilini içerir. Aion'un yeni metinleri Türkçe/İngilizcedir. Aşağıda normal Ayarlar seçicisiyle Türkçe ve Arapçaya geçiş sonrası gerçek pencereler görülür; Arapça sağdan sola yerleşim ve yeniden başlatma testini de geçti.

![Türkçe ayarlar; seçilmiş OpenDyslexic ve sağ sekmeler](screenshots/1537-windows-settings-tr.png)

![Arapça sağdan sola arayüz](screenshots/1537-windows-settings-ar.png)

## Karakterler

Aion, kurt, kuzu ve baykuş kendi bütün gövdeli PNG karelerinden oynatılır. Panel isteğe bağlıdır; kendi PNG karakterini ekleme, duraklatma ve yerel yedekleme bulunur.

![Baykuşun okuma karesi ve Türkçe karakter kontrolleri](screenshots/1537-windows-companion.png)

[İndir ve kullan](QUICK_START.md) · [Test sonuçları ve açık işler](VALIDATION.md). İmzalı otomatik güncelleme ve Authenticode henüz yoktur; bu sürüm geliştirici önizlemesidir.
