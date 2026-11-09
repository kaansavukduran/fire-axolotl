# Karakter paneli / Companion sidebar

Aion araç çubuğu paneli veya Aion Ayarları → **Yol arkadaşları → Karakter panelini aç**. Firefox'un kendi yan panelinde açılır; kurulumda kendiliğinden açılmaz. Aion, kuzu, kurt ve Baykuş Ömer hazırdır. Dinlenme, kitap okuma ve çalışma hareketleri kullanıcı tarafından seçilir. Web siteleri izlenerek otomatik hareket seçilmez.

Open **Companions → Open companion sidebar** from Aion's toolbar panel or settings. It stays closed at install. Choose Aion, the lamb, wolf or owl and an activity. Activities are selected manually, never inferred from browsing.

Hareketler bütün karakterin çizilmiş karelerinden oynatılır. Baş/gövdeyi çubuklarla birleştiren bir sistem kullanılmaz. **Hareketi durdur** klavyeyle de çalışır; işletim sisteminin azaltılmış hareket seçimi karakteri sabit tutar. Görsel seçimleri görev, kelime veya keşif puanı oluşturmaz.

Animations use illustrated whole-character frames. Pause is keyboard accessible and OS reduced motion freezes the character. Character customization awards no progress.

## Kendi karakterin / Your own character

1. **Kendi karakterini ekle → Dosya seç** ile normal PNG veya önceden dışa aktarılmış karakter JSON dosyasını seç. / Choose a regular PNG or previously exported character JSON.
2. Adını yaz. Tek resim için gelişmiş ayarlar 1 sütun, 1 satır, 1 kare olarak kalabilir. / Enter a name; still images use the default one-cell grid.
3. Kare şeridi için **Kare animasyonu ayarları** bölümünde sütun/satır sayısını, oynatılacak satırı, o satırdaki kare sayısını ve saniyedeki kare hızını gir. / For a sprite sheet, enter columns, rows, the row to play, its frame count and FPS.
4. **Karakteri kaydet ve seç** düğmesine bas. Panel yeniden açıldığında seçimin korunur. / Save and select; the selection survives reopening.

Örneğin mevcut Aion Pet görseli 8 sütun ve 11 satırdır. İlk satırdaki dinlenme için satır 1, kare sayısı 6 seçilebilir. Bir satırın kareleri başka satırdaki hareketlerle karıştırılmaz. / The existing Aion Pet uses 8 columns and 11 rows; its first idle row has 6 frames.

PNG sınırları: 6 MB, kenar başına 8192 piksel, toplam 16 milyon piksel. Kare ızgarası eşit bölünmeli; sütun/satır 1–16 ve hız 2–24 kare/saniye olmalıdır. SVG, GIF ve kendiliğinden oynayan APNG alınmaz; böylece duraklatma/azaltılmış hareket uygulanabilir. En fazla 8 özel karakter saklanır.

Imports accept regular PNG only, with bounded size/dimensions and validated grid/FPS. SVG, GIF and APNG are not accepted. Up to 8 custom characters are stored.

## Saklama ve yedek / Storage and backup

Dosyalar yalnız bu tarayıcı profilindeki IndexedDB alanında saklanır. **Karakteri dışa aktar**, PNG'yi ve kare ayarlarını tek JSON dosyasına koyar. Aynı dosya seçilerek tekrar içe aktarılır. Normal Aion ayar yedeği karakter piksellerini içermez; karakter yedeği ayrı alınır. Kaldırma işlemi seçili özel karakterle sınırlıdır; tarayıcı geçmişi, parolalar ve kelimeler değişmez.

Character files remain in this profile's IndexedDB. Export includes PNG bytes and grid settings in one JSON file that can be reimported. Normal Aion settings backups exclude character pixels, so export characters separately. Removal affects only the chosen custom character.
