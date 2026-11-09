# Veri akışları / Data flows

Bu belge mevcut Aion modülünü anlatır; tüm Firefox ağ trafiğinin denetlendiği iddiasını taşımaz. / This describes the current Aion companion, not an audit of all upstream browser traffic.

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

Aion'a telemetri, reklam SDK'sı, zorunlu hesap veya otomatik sayfa/ses gönderimi eklenmedi. Modülün dışında, Firefox'un mevcut ağ hizmetleri ve ziyaret edilen siteler kendi veri akışlarına sahiptir. Bunlar ürünün kararlı sürüm gizlilik bildiriminde ayrıca doğrulanmalıdır. / Aion adds no telemetry, ad SDK, mandatory account, or automatic page/audio submission. Upstream services and visited sites have separate data flows requiring review before stable release.

Yedek dosyası parola, geçmiş veya çerez içermez; kullanıcı tarafından kaydedilmiş kişisel metin içerebilir. Yedekleme görünümü gerçek ziyaretleri veya görevleri tamamlandı olarak işaretlemez. / Backups exclude passwords, history and cookies, but may contain personal vocabulary text. Previews do not mark real actions complete.
