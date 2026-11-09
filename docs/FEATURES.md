# Özellik eşlemesi / Feature map

Hedef, özellikleri tarayıcıyla birlikte sunmaktır. Marka adları yalnızca kullanıcının mevcut araçlarını tanımlamak içindir; bu projeyle ilişkili oldukları anlamına gelmez. / The goal is built-in functionality. Names identify the user's current tools and do not imply affiliation.

| Mevcut araç / Existing tool | Fire Axolotl yaklaşımı / Approach | Bu aşamadaki durum / Current state |
| --- | --- | --- |
| Bitwarden | Firefox parola yöneticisi temel alınır. Bitwarden hesabı, kasa eşitlemesi ve özel kasa özellikleri ayrı bir entegrasyon ve lisans incelemesi gerektirir. / Start with Firefox password management; Bitwarden sync needs a separate reviewed integration. | Yerleşik Firefox yeteneği korunur; Bitwarden eşdeğerliği yok. / Native passwords preserved, no Bitwarden parity. |
| DeepL | Cihazda çalışan Firefox sayfa/seçim çevirisi korunur. İsteğe bağlı hizmet bağlantısı açık onayla çalışır. / Preserve Firefox local translation; external services require explicit user action. | Aion'da LibreTranslate uyumlu seçili metin akışı var; DeepL hizmeti ve canlı ses çevirisi eklenmedi. / Selected-text flow implemented; DeepL and live transcription pending. |
| DuckDuckGo Search & Tracker Protection | Firefox ETP ve kullanıcı tarafından seçilen arama motoru. / Firefox ETP and user-selected search engine. | Upstream korumalar korunur; tüm DuckDuckGo özelliklerinin kopyası değildir. / Preserved upstream protection, not complete feature parity. |
| Enhancer for YouTube | Ortak video kumandası, ileride site bağdaştırıcıları. / Shared controls plus site adapters. | Hız, deneysel kalite isteği, çözünürlük ve altyazı var. Diğer iyileştirmeler bekliyor. / Speed, experimental quality, resolution and captions implemented; remaining features pending. |
| Firefox Multi-Account Containers | Firefox contextual identities altyapısı. / Native contextual identities. | Oluşturma ve mevcut sayfayı ayrı alanda açma var; site kuralları ve otomatik yönlendirme bekliyor. / Create/open implemented; site rules pending. |
| Global Speed | Yerleşik video kumandası. / Built-in video controls. | Ana belgedeki erişilebilir videolarda hız var. Ses, kısayol ve tüm iframe kapsamı bekliyor. / Accessible main-document video speed implemented; audio, hotkeys and all-frame support pending. |
| Netflix 1080p UA | Servisin sunduğu kalite seçeneklerine uyumlu site bağdaştırıcısı. / Adapter respecting service capabilities. | Netflix bağdaştırıcısı yok. DRM, sertifikasyon, hesap ve hizmet koşulları incelenmeli. / Not implemented; DRM, certification and service terms require review. |
| Search by Image | Kullanıcının seçtiği arama sağlayıcısına açık eylemle görsel/URL gönderimi. / Explicit image/URL submission to a chosen provider. | Bekliyor. / Pending. |
| Temporary Containers | Son sekme kapandığında sadece ilgili geçici kimliği temizleme. / Remove only the relevant temporary identity after its last tab closes. | Uygulandı; indirmeleri veya geçmişi silmez. / Implemented; downloads/history remain. |
| uBlock Origin | Lisansı doğrulanmış açık kaynak engelleme motoru ve filtre listeleri, kaynak bildirimleriyle birlikte. / Reviewed open-source blocker and filter lists with attribution. | Henüz paketlenmedi; Firefox ETP, uBlock Origin eşdeğeri değildir. / Not bundled; Firefox ETP is not equivalent to uBlock Origin. |
| Dark Reader, kapalı / disabled | İsteğe bağlı sayfa koyu modu; Aion teması ayrı. / Optional page dark mode, independent of Aion theme. | Aion temaları var; web sayfalarını dönüştürme bekliyor. / Companion themes implemented; page conversion pending. |
| QR Code, kapalı / disabled | Cihazda çalışan URL/metin QR üretimi. / Local URL/text QR generation. | Bekliyor. / Pending. |

Ekrandaki önerilen eklentiler kurulu listeye dahil sayılmadı. / Recommended add-ons in the screenshot are not treated as installed requirements.

## Ek istekler / Additional requests

- Sekmeler üstte, solda veya sağda: kaynak katmanında yerel tercih arayüzü. / Native top/left/right tab-layout controls.
- Video tercihi: otomatik, 720p, 1080p, 1440p, 2160p, sunulan en yüksek kalite. Tercih videonun gerçekten o kalitede oynadığının kanıtı değildir. / Saved preference does not prove actual playback resolution.
- Çift altyazı: yerel VTT/SRT zaman damgalarına göre oynatma. Tüm videolarda canlı ses tanıma ve otomatik altyazı çevirisi sonraki aşama. / Local dual captions implemented; universal transcription/translation pending.
  Katman, normal belge ve kapsayıcı tam ekran düzenleri içindir. Video öğesinin doğrudan yerel tam ekranı ve başka kaynaktan iframe oynatıcıları ayrıca uyarlanmalıdır. / The overlay targets normal documents and container fullscreen; native video-element fullscreen and cross-origin iframe players need further adaptation.
- Firefox benzeri güncelleme: imzalı MAR, kanal/mimari seçimi, veri koruma ve iki sürümle gerçek yükseltme testi zorunlu. / Signed MARs, channel/architecture targeting, data preservation and a real upgrade test are required.
