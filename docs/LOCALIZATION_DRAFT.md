# Yerel Türkçe çalışması / Native Turkish work in progress

Bu dal bir taslaktır; main ile birleştirilmez ve yeni sürüm olarak yayımlanmaz.

## Amaç / Goal

İlk native pakete kurulum gerektirmeyen Türkçe kaynaklarını eklemek, özgün Fire Axolotl adını korumak ve mevcut dil seçimini değiştirmeden cihaz dili/Türkçe ilk açılış tercihini sağlamak. Firefox'un diğer dilleri ve yeni Aion metinlerinin bütün dillere çevrilmesi ayrı açık işlerdir.

## Gerçekleşen doğrulama / Evidence

- Bağımsız native ürüne resmi Türkçe XPI normal imzalı kurulumla eklendi: active, appDisabled=false, signedState=2.
- Tam süreç yeniden başlatılınca appLocale=tr ve native settings-page-title=Ayarlar doğrulandı.
- Bu dalın kaynak katmanı yerelde uygulandı; artımlı native derleme 44 saniyede başarıyla tamamlandı.
- **Yeni yerleşik kayıt doğrulaması geçmedi:** generated built_in_addons.json içinde langpack-tr@fire-axolotl.browser vardı, fakat gerçek yeni profilde AddonManager kaydı null, availableLocales yalnızca en-US idi. Bunun nedeni çözülmeden yerleşik Türkçe çalışıyor denmez.
- Yeni üç birim gerilemesi ve native etkinleşme/marka kapısı eklendi. Bunların sonuçları CI'dan kontrol edilmelidir; eski 28 testin geçmesi bunların geçtiği anlamına gelmez.

## Lisans ve imza sınırı / Licensing and signature boundary

localization.json, Mozilla ESR 153.6.0esr Türkçe XPI'sini SHA-512 ve sürümle sabitler. Çeviriler ve özgün yazar bildirimi korunur; yalnızca eklenti kimliği, yerelleştirilmiş açıklama ve ürün markası değiştirilir. Türetilmiş yerleşik kaynak, Mozilla tarafından imzalanmış değişmemiş paket olarak sunulmaz. Eski imzalar bu değişmiş kaynağa kopyalanmaz. Özgün imzalı XPI, MPL-2.0 metni ve değişiklik makbuzu distribution/sources içinde tutulur. Harici eklenti/dil paketi imza doğrulaması kapatılmaz.

## Kesinti ve devam / Interruption and next step

Yürütme ortamı 2026-11-09 tarihinde unavailable oldu. exec-server transport disconnected ve recovery timed out hataları nedeniyle yerel günlükler tekrar okunamadı. Kaynak çalışma bu ayrı dala kurtarıldı. Sıradaki iş: native_localization.py günlüklerinden manifest/kayıt yükleme sorununu çözmek; ardından normal Ayarlar → Diller yoluyla TR/EN seçimini, marka, yeniden açılış, yüksek ölçek ve kayıtların korunmasını doğrulamak.

GitHub Actions, bu daldaki tam native testi ve ayrı commit eşleşmeli ZIP/Git bundle/makbuz üretimini çalıştırır. Otomatik backup artifact'i Drive yedeği yerine sayılmaz. Yeni dalın özel Drive aktarımı, çalışma ortamı arşivleri indiremediği için **bekliyor**; main/32ac4df ve önceki doğrulanmış Drive yedekleri korunur.

The native built-in locale activation is failing and remains a merge/release blocker. Standard signed Turkish installation works, but is not proof that this new built-in integration works. The executor is unavailable; GitHub CI and backup artifacts provide continuation evidence, with private Drive transfer still pending.
