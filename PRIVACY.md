# Veri akışları / Data flows

Bu belge mevcut Aion modülünü ve kaynak katmanındaki gizlilik ilkelerini anlatır; tüm Firefox ağ trafiğinin bağımsız denetimi tamamlanmış değildir. / This describes the companion and source-layer privacy policies; it is not a completed independent audit of all browser traffic.

`browser/policies.json` ve varsayılan tercihler, kullanım telemetrisi, Firefox çalışmaları, sponsorlu öneriler, özel reklam ilişkilendirmesi ve otomatik çökme raporu gönderimini kapatır. Temel telemetri ve sponsorlu içerik tercihleri kilitlenir. Paket, ilkeleri normal `distribution/policies.json` yolundan yükler. Firefox'un ayarlarda yönetim ilkesi gösterebilmesi bu projenin yerel gizlilik yapılandırmasından kaynaklanır; uzaktaki bir kuruluşla bağlantı kurulması anlamına gelmez. / The shipped local policy disables telemetry, studies, sponsored recommendations, private ad attribution and automatic crash submissions. The native policy indicator reflects local configuration, not a remote organization connection.

Mozilla hesabı ve Sync korunur ve isteğe bağlıdır. Kullanıcı giriş/eşitleme başlattığında kimlik doğrulama ve seçilen eşitleme verileri Mozilla hizmetlerine iletilir; sunucular bağlantı metaverilerini görebilir. Güvenlik listeleri, dil paketi/model indirmeleri ve güncellemeler de ağ bağlantıları gerektirebilir. Telemetriyi kapatmak, bu seçilen işlevlerin hiçbir sunucuyla konuşmadığı anlamına gelmez. / Optional account/Sync, security services, language downloads and updates still need network connections and expose normal connection metadata. They are separate from telemetry and advertising collection.

| Eylem / Action | Veri / Data | Hedef / Destination |
| --- | --- | --- |
| Aion ayarlarını değiştirme / Change settings | Dil, görünüm, ölçek, yazı ve tercihler / language, appearance and preferences | Bu profilin yerel depolaması / local profile storage |
| Kelime kaydetme / Save vocabulary | Kullanıcının seçtiği metin / user-selected text | Yerel depolama ve kullanıcının indirdiği yedek / local storage and exported backup |
| Konteyner oluşturma/açma / Create/open container | Konteyner kimliği, mevcut sekme adresi / identity and active URL | Firefox konteyner sistemi; açılan site normal bağlantı alır / native containers; normal site navigation |
| Geçici konteyner / Temporary container | Modülün oluşturduğu geçici kimlikler / temporary identities owned by the companion | Yerel depolama; son sekmede sadece bu kimlikler temizlenir / local storage; only owned identities are cleaned |
| Hız/çözünürlük / Speed/resolution | Video durumu / video state | Etkin sayfa; Aion'a ait ağ gönderimi yok / active page; no companion network request |
| Altyazı dosyası / Caption file | Seçilen VTT/SRT / selected VTT/SRT | Etkin sayfadaki yerel katman; yükleme yok / local overlay, no upload |
| Metni veya altyazı satırını alma / Capture selection/cue | En fazla 5.000 karakter / at most 5,000 characters | Aion paneli; henüz çeviri hizmetine gönderilmez / companion panel only |
| “Gönder ve çevir” / “Send and translate” | Görünen metin, hedef dil, normal bağlantı IP bilgisi / visible text, target language and connection IP | Kullanıcının seçtiği HTTPS sağlayıcısı / user-chosen HTTPS provider |
| “Güncellemeleri kontrol et” / “Check for updates” | Normal GitHub HTTP isteği / normal GitHub request | GitHub Releases API |
| JSON yedeği / JSON backup | Aion ayarları, kelime defteri ve keşif ilerlemesi / settings, vocabulary, progress | Kullanıcının indirdiği yerel dosya / user-downloaded local file |
| Görselle arama / Image search | Sağ tıklanan görselin adresi / image URL | Yalnızca kullanıcının seçtiği Google Lens, Bing, TinEye veya Yandex sekmesi / only the explicitly chosen provider tab |
| Karakter ekleme / Import character | PNG pikselleri, ad ve kare düzeni / PNG pixels, name and frame layout | Bu profilin yerel IndexedDB alanı; karakter yedeği ayrı dışa aktarılır / local profile IndexedDB; separate user-exported backup |

Yerleşik uBlock Origin, engelleme için site isteklerine erişir ve seçilen filtre listelerini kendi sunucularından/CDN'lerinden güncelleyebilir. Aion'un sınırlı sayfa erişimiyle ayrı bir bileşendir. İzin, kaynak ve lisans ayrıntıları [bileşen envanterindedir](docs/COMPONENTS.md). / Built-in uBO needs request access and can update selected lists from their servers/CDNs; its permissions are separate from Aion's.

Karakter paneli isteğe bağlıdır ve kurulumda açılmaz. Web sayfalarına içerik betiği yerleştirmez, gezinme etkinliğine göre otomatik hareket seçmez ve kişisel görselleri bir hizmete yüklemez. Karakter eklemek veya görünüm değiştirmek keşif ilerlemesi kazandırmaz. / The optional sidebar stays closed at install, does not inject into pages, does not select activities from browsing behavior and never uploads personal images. Importing a character or changing appearance awards no progress.

Aion'a telemetri, reklam SDK'sı, zorunlu hesap veya otomatik sayfa/ses gönderimi eklenmedi. Modülün dışında, Firefox'un mevcut ağ hizmetleri ve ziyaret edilen siteler kendi veri akışlarına sahiptir. Bunlar ürünün kararlı sürüm gizlilik bildiriminde ayrıca doğrulanmalıdır. / Aion adds no telemetry, ad SDK, mandatory account, or automatic page/audio submission. Upstream services and visited sites have separate data flows requiring review before stable release.

Yedek dosyası parola, geçmiş veya çerez içermez; kullanıcı tarafından kaydedilmiş kişisel metin içerebilir. Yedekleme görünümü gerçek ziyaretleri veya görevleri tamamlandı olarak işaretlemez. / Backups exclude passwords, history and cookies, but may contain personal vocabulary text. Previews do not mark real actions complete.
