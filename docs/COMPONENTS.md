# Yerleşik üçüncü taraf bileşenler / Built-in third-party components

## uBlock Origin 1.76.0

Resmî, değiştirilmemiş Firefox paketi kullanılır. Kimlik `uBlock0@raymondhill.net`; SHA-256, kaynak commit'leri, bütün alt modüller ve lisans `components.json` içinde sabittir. Raymond Hill ve katkıcılarının bildirimleri, uBlock markası, imza dosyaları ve bağımlılık lisansları korunur. Projemize ait bir engelleme motoru olarak sunulmaz.

Use the unmodified official Firefox package, with pinned digest, complete source/submodule revisions and upstream attribution. uBlock Origin remains an independently licensed component, not an engine authored by Fire Axolotl.

- Ana kod: **GPL-3.0-or-later**. Filtreler, kitaplıklar, fontlar ve simgeler kendi korunmuş lisanslarını taşır. / Main code: GPL-3.0-or-later; retain each list/library/font/icon license.
- `scripts/fetch_components.py`, paketi doğrular; beklenmeyen kimliği, bozuk özeti ve güvenli olmayan arşiv girdilerini reddeder. Firefox derlemesi, uBO'yu Aion'dan ayrı bir yerleşik modül olarak ekler. / Validate identity, hash and archive paths before embedding uBO separately from Aion.
- Paketlenen filtreler, sabitlenmiş uAssets kaynaklarıyla **bayt bayt karşılaştırılır**. Tercih edilen düzenlenebilir filtre kaynakları da arşivdedir. / Compare bundled assets byte for byte with pinned uAssets build inputs; include editable filter sources.
- `distribution/sources/`, tam ilgili uBO kaynak arşivini, envanteri ve GPL metnini tarayıcı paketiyle birlikte taşır. Kaynak arşivi derleme betiklerini, bütün alt modülleri, uAssets main/prod ağaçlarını ve özgün imzalı paketi içerir. / Ship corresponding source, inventory and GPL text alongside the binary.
- `scripts/verify_component_source.py`, bu arşivden uBO'yu yeniden üretir. **665 dosya** karşılaştırılır: manifest ayrıştırılmış JSON olarak, diğerleri bayt olarak eşleşir. Mozilla'nın imzaları ve öneri belgesi ayrı tutulur; bunlar proje tarafından yeniden üretilemez. / Rebuild and compare 665 files; Mozilla signing/recommendation data is excluded and manifest serialization formatting is ignored.

```sh
python3 scripts/fetch_components.py
python3 scripts/verify_component_source.py
```

Engelleme için uBO'nun bütün sitelerdeki istekleri görme ve değiştirme izni gerekir. Bu yetki Aion'un isteğe bağlı sayfa erişiminden ayrıdır. Kullanıcı uBO'nun kendi panelinden site istisnalarını, filtreleri ve liste güncellemelerini yönetir. Yerleşik paketleme, bileşenin yetkilerini ortadan kaldırmaz.

uBO needs access to site requests to block them. Its permissions are separate from Aion's limited, on-demand page access. Site exceptions, lists and update settings remain available through uBO's own interface.

uBO'nun otomatik filtre güncellemeleri, seçili listelerin sunucularına/CDN'lerine ağ isteği yapabilir. Bunlar Firefox telemetrisi değildir; “hiçbir sunucuya bağlanmaz” iddiası kullanılmaz. Derlemeye konan ilk listeler sabittir; kullanıcının daha sonra aldığı liste güncellemeleri farklı olabilir. Günlük bakım kontrolü yeni uBO sürümünü görünür kılar, otomatik olarak güvenilir sayıp kurmaz.

Filter updates can contact selected list servers/CDNs. Bundled initial lists are pinned; subsequent user updates can differ. Daily freshness checks request review of new engine releases rather than silently installing them.

## Doğrulamanın sınırı / Validation limit

Gerçek Firefox testinde resmî imza normal kurulumla doğrulanır; yerel kuralın bir betik isteğini sunucuya ulaşmadan engellediği sınanır. Ayrı native koşularda tam derlenmiş Fire Axolotl'ın kendi kimliğiyle uBO'yu etkin yerleşik bileşen olarak yüklediği, gerçek isteği engellediği ve dağıtım arşivinin ilgili kaynakları taşıdığı da doğrulandı. Sonuçlar [VALIDATION.md](VALIDATION.md) içinde.

The stock-Firefox test verifies signed installation. Separate compiled-fork tests now verify native built-in loading and real blocking, while package verification checks corresponding-source delivery. These checks do not certify every filter or website.
