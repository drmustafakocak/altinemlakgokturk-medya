# Cumartesi Bilgilendirme Serisi — görev talimatı (Altın Emlak Göktürk)

Bu dosya üç zamanlanmış görevin (Perşembe / Cuma / Cumartesi) ortak talimatıdır. Kullanıcı Dr. Mustafa Koçak; onunla Türkçe konuş. Kalıcı bir istek gelirse bu dosyayı güncelle.

## Amaç
Her hafta Cumartesi 10:00'da altinemlakgokturk Instagram hesabında 1 bilgilendirme paylaşımı (carousel ya da Reels). Konu, haftalık internet taramasıyla seçilen **en güncel ve en ilgi çekici** gelişmedir. Onaysız hiçbir şey yayınlanmaz.

## Akış
| Gün | Görev | Ne olur |
|---|---|---|
| Perşembe 13:17 | Konu önerisi | İnternet taraması → 3 konu önerisi → kullanıcı seçer |
| Cuma 10:23 | Taslak + onay | Seçilen konu doğrulanır, carousel/Reels + hikâye + açıklama üretilir, onaya sunulur |
| Cumartesi 09:48 | Yayın | Onaylı içerik 10:00'da yayınlanır; onay yoksa son kez sorulur |

## Sabitler
- Depo (kanonik kayıt): `drmustafakocak/altinemlakgokturk-medya`, klasör `bilgilendirme/`.
  - `_sablon/bilgi_post.py` (üretici), `_sablon/fonts`, `_sablon/logo`
  - `gecmis.json` (işlenen konular — tekrar önleme)
  - Haftalık klasör: `bilgilendirme/<CUMARTESİ YYYY-AA-GG>/` → `icerik.json`, `durum.json`, `oneriler.json`, `instagram_jpg/*.jpg`, `reels.mp4` (varsa)
- `durum.json`: `{"asama": "konu_onerildi" | "konu_secildi" | "taslak_onay_bekliyor" | "onaylandi" | "yayinlandi" | "atlandi", "konu": "...", "format": "carousel"|"reels", "not": "...", "permalink": "..."}`
- Bilgisayardaki klasör (erişilebilirse): `/Users/mustafkocak/Documents/CLAUDE/Altın Emlak Göktürk/04_ICERIKLER/Cumartesi Bilgilendirme/<YYYY-AA-GG> - <kısa konu>/` (PNG'ler, story.png, aciklama.txt, reels.mp4). Bilgisayar kapalıysa atla; depo yeterli.
- Instagram: Composio, alias `altinemlakgokturk`. ig_user_id'yi her seferinde `INSTAGRAM_GET_USER_INFO` ("me") ile al.
- Ofis tel 0532 464 75 19, mail gokturk@altinemlak.com.tr, site altinemlakgokturk.com (şablonda sabit).
- Başlangıç: `add_repo("drmustafakocak","altinemlakgokturk-medya", access "push")`, `git clone --depth 1 https://github.com/drmustafakocak/altinemlakgokturk-medya /home/claude/medya` (uzun zaman aşımı). Commit: user.name drmustafakocak; oturumun git ek satırlarını ekle; `git -c push.negotiate=true push`.

## Konu kuralları
- Kategoriler (dönüşümlü olsun, aynı kategori art arda 3 haftayı geçmesin): **Hukuki** (kira, tapu, miras, tahliye, sözleşme), **Vergi/Finans** (emlak vergisi, tapu harcı, kira geliri beyanı, konut kredisi), **Teknik** (deprem, iskân, aidat, yapı denetimi, enerji kimlik), **Mal sahibi–kiracı**, **Göktürk–Kemerburgaz ve çevresi** (ulaşım, imar, projeler, sosyal yaşam), **Genel** (herkesi ilgilendiren pratik bilgiler).
- Öncelik: son 7–10 günün gelişmesi + önümüzdeki 1–3 haftada son tarihi/yürürlüğü olan konular (ör. ay başı kira artış oranı, vergi taksitleri, yürürlüğe giren düzenleme). Haber yoksa kalıcı değeri yüksek bir "nasıl yapılır" konusu.
- `gecmis.json`'daki konuları son 8 haftada tekrar etme (yeni gelişme varsa güncelleme olarak işlenebilir).
- Siyasi, tartışmalı, kişileri/kurumları hedef alan konulardan; asayiş haberlerinden ve Göktürk'teki imar/proje uyuşmazlıklarında taraf tutmaktan kaçın.
- Kaynak: Resmî Gazete, mevzuat.gov.tr, TÜİK, GİB, TKGM, Ticaret/Çevre Bakanlığı, İBB/Eyüpsultan Belediyesi öncelikli; haber siteleri yalnızca destekleyici. Rakam, tarih, oran ve kuralı en az iki kaynakla doğrula. Doğrulanamayan bilgi içeriğe girmez. Uydurma istatistik/örnek yok; temsilî grafik kullanılırsa "temsilîdir" yazılır.
- Hukuki/vergi/finans içeriklerinde son sayfada ve açıklamada "Bilgilendirme amaçlıdır; hukuki/mali danışmanlık yerine geçmez." uyarısı ve kaynak satırı.
- Dil: profesyonel, anlaşılır, samimi; klişe yok ("kaçırılmayacak fırsat", "hayallerinizdeki ev", "hemen arayın" kullanma). İlk cümle konuya özel bir kanca.

## FORMAT seçimi
- Varsayılan **carousel** (kapak + 4–7 madde + son sayfa; en fazla 10). Adım adım/çok maddeli, rakam ve tarih içeren konular.
- **Reels**: tek ve çarpıcı mesaj, hesaplama örneği, "biliyor muydunuz" türü konular. Reels de aynı icerik.json'dan `--reels` ile üretilir (sayfalar sahne olur, ~30–40 sn, sessiz; kullanıcı isterse uygulamada müzik ekleyebilir). Reels haftalarında madde sayısını 4–5'te tut.

## 1) PERŞEMBE — konu önerisi
1. Cumartesi tarihi S = bu haftanın cumartesisi. `bilgilendirme/S/durum.json` varsa ve aşaması `konu_secildi` veya ötesindeyse: sessizce bitir.
2. WebSearch ile tarama (en az 8–10 arama, kategorilere yayılmış; tarih ifadesi olarak bu ay/yıl). WebFetch ile ana kaynakları oku.
3. En iyi 3 konuyu seç; her biri için: başlık, kategori, neden şimdi (tarih/son tarih), önerilen format, 2 doğrulayıcı kaynak. `bilgilendirme/S/oneriler.json` ve `durum.json` (`konu_onerildi`) yaz, push.
4. SendUserMessage ile 3 öneriyi kısaca göster; AskUserQuestion: "Bu Cumartesi hangi konu?" seçenekler = 3 konu (ilki önerilen) + "Bu hafta paylaşma". Format değişikliği yanıttan anlaşılırsa uygula. PushNotification: "Cumartesi bilgilendirme konusu seçiminizi bekliyor".
5. Yanıt gelirse `durum.json` → `konu_secildi` (ya da `atlandi`), push. Yanıt gelmezse bir şey yapma (Cuma görevi 1. öneriyle devam eder).

## 2) CUMA — taslak ve onay
1. `durum.json` `atlandi` ise sessizce bitir. `taslak_onay_bekliyor` ise (taslak önceden hazırlanmış): içerikteki tarih/kural hâlâ geçerli mi kısaca doğrula, değiştiyse düzelt; sonra 5. adımdan devam et. `onaylandi` ise: içerikteki kritik tarih/oran/kural hâlâ geçerli mi hızlıca doğrula; geçerliyse sessizce bitir. Değiştiyse içeriği düzelt, `durum.json`'u `taslak_onay_bekliyor` yap ve 5. adımdan devam ederek yeniden onay iste.
2. Konu: `konu_secildi` ise seçilen; değilse oneriler.json'daki 1.; o da yoksa Perşembe 2–3. adımlarını kendin yap.
3. Konuyu derinlemesine araştır ve doğrula (yukarıdaki kaynak kuralları). `bilgilendirme/S/icerik.json` yaz (örnek: `2026-11-21/icerik.json`; alanlar `_sablon/bilgi_post.py` başında). Grafik tipleri: akis, takvim (+cizgi), liste, oran, buyuk, kontrol. Açıklama ≤ 2200 karakter: kanca, kısa özet, maddeler, CTA (telefon + site), kaynak + uyarı, 6–10 hashtag (#göktürk #kemerburgaz #eyüpsultan #altinemlakgokturk #altınemlak + konuya özel).
4. `cd /home/claude/medya/bilgilendirme && python3 _sablon/bilgi_post.py S/icerik.json /home/claude/out [--reels]`. stderr'deki "taşıyor" uyarısı varsa metni kısalt, yeniden üret. Read ile TÜM sayfaları ve story.png'yi kontrol et (taşma, yazım, Türkçe karakter, rakam doğruluğu). Reels ise birkaç kare çıkarıp bak.
5. `out/instagram_jpg/*` ve varsa `reels.mp4`'ü `bilgilendirme/S/` altına kopyala, commit + push; `durum.json` → `taslak_onay_bekliyor`. Bilgisayar klasörüne erişilebiliyorsa PNG'ler, story.png, aciklama.txt, reels.mp4'ü device_commit_files ile yaz (önce /mnt/user-data/outputs/ altına kopyala).
6. Onaya sun: SendUserFile (kapak, tüm sayfalar ya da reels.mp4 + story.png), SendUserMessage ile açıklama metninin tamamı + kaynak linkleri + belirsizlikler. AskUserQuestion: "Cumartesi 10:00'da bu haliyle yayınlayayım mı?" → Onaylıyorum / Değişiklik var / Bu hafta paylaşma. PushNotification: "Cumartesi bilgilendirme taslağı onayınızı bekliyor".
7. Onay → `durum.json` `onaylandi`, push; "Cumartesi 10:00'da yayınlanacak" de. Değişiklik → uygula, 4'ten tekrar. Paylaşma → `atlandi`. Kalıcı istek → bu dosyaya yaz.

## 3) CUMARTESİ — yayın
1. `durum.json` `yayinlandi`/`atlandi` ise sessizce bitir. Klasör yoksa: "Bu hafta hazır bilgilendirme içeriği yok" diye bildir ve bitir.
2. `taslak_onay_bekliyor` ise: görselleri/açıklamayı tekrar gönder, açık onay iste (AskUserQuestion), PushNotification. Onay gelmezse YAYINLAMA.
3. Onaylı içerikte saat 10:00'ı bekle (önceyse), sonra Composio ile yayınla (görsel adresleri commit hash'li raw GitHub: `https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/<HASH>/bilgilendirme/S/instagram_jpg/<dosya>`; curl ile 200 doğrula):
   - Carousel: her sayfa için `INSTAGRAM_POST_IG_USER_MEDIA` {ig_user_id, image_url, is_carousel_item: true} → `INSTAGRAM_POST_IG_USER_MEDIA` {media_type "CAROUSEL", children: sıralı id'ler, caption} (ya da `INSTAGRAM_CREATE_CAROUSEL_CONTAINER`) → `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH`.
   - Reels: `INSTAGRAM_POST_IG_USER_MEDIA` {video_url (raw mp4), media_type "REELS", caption, share_to_feed: true, cover_url: instagram_jpg/01.jpg} → `..._PUBLISH` (max_wait_seconds 240).
   - Hikâye: `INSTAGRAM_POST_IG_USER_MEDIA` {image_url: story.jpg, media_type "STORIES"} → publish. Hikâye başarısız olursa post'u etkilemez; story.png'yi kullanıcıya gönder.
4. `INSTAGRAM_GET_IG_MEDIA` ile permalink al. `durum.json` → `yayinlandi` + permalink; `gecmis.json`'a {tarih, konu, kategori, format, permalink} ekle; push. SendUserMessage + PushNotification ile linki bildir.
5. Hata: bir kez yeniden dene; olmazsa yayını zorlamadan hatayı açıkla.
