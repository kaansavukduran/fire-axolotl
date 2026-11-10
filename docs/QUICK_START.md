# Fire Axolotl kullanım kılavuzu

Bu kılavuz Windows geliştirici ön sürümünde bulunan işlevleri anlatır. Güncel kurulum bağlantısı [ana sayfada](../README.md), çalışan arayüz görüntüleri [burada](UI_PREVIEW.md). İmzalı otomatik güncelleme henüz yoktur; bu sürüm kararlı günlük kullanım için tamamlanmış sayılmaz.

## İlk açılış ve görünüm

Windows'ta **Setup.exe** dosyasını çalıştırıp kurulum sihirbazını izle; Başlat menüsünden **Fire Axolotl** aç. Kaynak ZIP'lerini veya motor arşivini indirmen gerekmez. Program kendi profilini kullanır.

Yeni profilde tarayıcı koyu temada ve sekmeler üstte açılır. **Menü → Ayarlar → Görünüm** içindeki Fire Axolotl kontrollerinden üst, sol veya sağ sekmeleri seçebilirsin. Aynı yerde araç çubuğu düzenleyicisini açabilir, tarayıcı yazı tipini OpenDyslexic veya Lexend yapabilirsin. Font değişikliği sitelerin yazılarını kendiliğinden değiştirmez.

Sitelerin kendi teması korunur. Tarayıcıya uyan sitelerin açık/koyu tercihini Görünüm'den seçebilirsin; sayfalar zorla karartılmaz. Ana arayüz dilini **Ayarlar → Diller** üzerinden değiştir. 153.7 tabanlı ön sürüm, Firefox'un yayımladığı 103 masaüstü dilini içerir; seçici dilleri kendi adlarıyla gösterir. Tarayıcı isterse **Uygula ve yeniden başlat** düğmesini kullan. Aion araçları ve eklediğimiz yeni Görünüm kontrolleri şu an Türkçe/İngilizcedir; oyunun dili ayrıca seçilir.

## Aion Koşusu

Yeni sekmede **Başlat** düğmesine bas. Oyun alanındayken **Boşluk** veya dokunma ile zıpla, **Esc** ile duraklat. Sekme değiştirdiğinde oyun duraklar. Buzda donma ve ateşte çizgi film tarzı kül animasyonu bulunur. İnternet gerekmez; rekor bu tarayıcı profilinde saklanır.

**Ayarlar → Görünüm** bölümünde oyunu gizleyebilir, dilini değiştirebilir ve rekoru sıfırlayabilirsin. Başka bir yeni sekme eklentisi seçersen onun sayfası açılır.

## Yerleşik araçlar

Araç çubuğundaki **Aion simgesine** bas. Ayrı eklenti kurmadan şu araçlara erişirsin:

- **Konteynerler:** Aynı sitede iş ve kişisel hesaplarını ayrı tutmak için kullan. Aion → Konteynerler'den ad verip alan oluştur, ardından seçip sayfayı o alanda aç. Sayfaya veya bağlantıya **sağ tık → Konteynerde aç → alan adı** ile de erişebilirsin. Asıl sekme açık kalır; çerezler ve giriş oturumları ayrılır. Bu özellik VPN değildir. Geçici alandaki son sekme kapatılınca yalnızca o alan temizlenir; indirmelerin ve geçmişin silinmez. Siteleri otomatik alanlara atama henüz yoktur.
- **Video:** Sayfadaki erişilebilir video için 0,25×–4× hız seç, uygula veya normal hıza dön. Gerçek çözünürlüğü okuyabilirsin. Kalite isteği deneysel YouTube desteğidir; Netflix veya bütün siteler için çözünürlük garantisi vermez.
- **Çift altyazı:** Kendi VTT/SRT dosyalarını özgün ve çevrilmiş altyazı alanlarına yükleyip göster. Bu işlem otomatik altyazı çevirisi değildir.
- **Çeviri:** **Aion → Çeviri → Cihazda çeviri aracını aç** düğmesine bas. Açılan yerel çeviri sekmesine metni yapıştırıp kaynak/hedef dili seç. Firefox'un açık kaynak çeviri motoru desteklediği dillerde cihazda çalışır; dil modelleri ilk kullanımda internetten indirilir. İndikten sonra o dil çiftiyle çevrimdışı çeviri yapılabilir. Ayrı bir sohbet yapay zekâsı veya önceden yüklenmiş sohbet modeli bulunmaz.
- **Seçili metin ve altyazı:** Metne sağ tıklayıp Aion çeviri aracını açabilir veya panelde seçili metni/erişilebilir altyazı satırını alabilirsin. Paneldeki isteğe bağlı dış çeviri alanını kullanmak için önce **Çeviri hizmeti ayarları** üzerinden kendi HTTPS hizmetini seçip izin ver. Metin yalnızca gönderme eyleminde o hizmete gider. Bu alanın hizmet ayarı, cihazda çeviri aracını kullanmak için gerekli değildir.
- **Görselle arama:** Görsele sağ tıkla ve sağlayıcı seç. Görsel adresi yalnızca bu seçimde sağlayıcıya gönderilir. Aion ayarlarından kapatılabilir.

uBlock Origin tarayıcıyla birlikte etkindir; kendi araç çubuğu simgesinden yönetilir. Parolalar, yer imleri, geçmiş ve okuyucu görünümü Firefox temelindeki kendi menülerinden kullanılır. Bitwarden hesabı veya DeepL aboneliğiyle otomatik bağlantı kurulmaz.

Aion 0.2 araç paneli geniş pencerede 760 piksele kadar açılır. **Geniş ekranda aç** düğmesi araçları normal bir sekmeye taşır; Çeviri, Konteynerler ve Video arasında geçebilirsin. Video ve konteyner işlemleri başlangıçta seçtiğin web sekmesini kullanır; üzerinde çalışılan sekme panelde gösterilir. Taslak metin ve seçili konteyner yalnızca tarayıcı oturumu boyunca korunur; normal ayar yedeğine yazılmaz.

## Karakterler ve kişisel ayarlar

Aion panelindeki **Yol arkadaşları → Karakter panelini aç** bölümünden Aion, kuzu, kurt veya baykuş seç. Animasyonlar bütün karakterin resim karelerinden oynar. Panel kurulumda kendiliğinden açılmaz; duraklatma ve işletim sisteminin azaltılmış hareket tercihi desteklenir.

Kendi PNG karakterini veya kare şeridini eklemek, dışa aktarmak ve silmek için [karakter kılavuzunu](CHARACTERS.md) izle. Karakterler cihazdaki profilinde tutulur.

Aion panelindeki **Ayarlar** düğmesi; araç dili, tema, ölçek, çeviri hizmeti ve JSON ayar yedeğine gider. Kişisel karakter pikselleri normal ayar yedeğine dahil değildir; karakteri ayrıca dışa aktar.

## Sürüm ve sınırlar

Yeni ön sürümler [GitHub Releases](https://github.com/kaansavukduran/fire-axolotl/releases) üzerinden elle indirilir. Bu aşamada Authenticode imzası ve otomatik güncelleme yoktur. Güvenlik korumalarını kapatma; dosya bütünlüğünü sürümdeki SHA-256 özetiyle karşılaştırabilirsin.

Gerçek hesapla Sync doğrulaması, yeni Aion metinlerinin diğer dillere çevirisi ve kalan eksikler [özellik eşlemesinde](FEATURES.md) takip edilir. Açılış testlerinin geçmesi bu hizmetlerin tamamlandığı anlamına gelmez.
