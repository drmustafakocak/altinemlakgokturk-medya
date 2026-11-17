# Günlük Gündem Hikâyesi — görev talimatı (Altın Emlak Göktürk)

> **HESAP KİLİDİ (zorunlu):** Composio'da birden fazla Instagram hesabı bağlı ve varsayılan hesap altinemlakgokturk DEĞİL. Her Instagram aracını `account: "instagram_shlu-ekron"` (alias altinemlakgokturk) ile çağır. Yayından önce aynı account ile `INSTAGRAM_GET_USER_INFO` ("me") çalıştır; username `altinemlakgokturk` ve id `28885078894525477` değilse YAYINLAMA, dur ve kullanıcıya bildir. ig_user_id = `28885078894525477` (17841479910444886 eski/yanlış kimliktir).

Kullanıcı Dr. Mustafa Koçak; onunla Türkçe konuş, onayları telefondan verir. **Bu projede her şey Türkçe:** mesajlar, bildirimler, soru seçenekleri ve oturum sonu özetleri dahil hiçbir çıktı İngilizce yazılmaz. Kalıcı bir istek gelirse bu dosyayı güncelle ve push et.

## Amaç
Her gün 12:00 civarı internet + sosyal medya taranır, emlak/gayrimenkul gündeminden **3 konu** önerilir. Kullanıcı bir veya birden fazla konu seçer. Seçilen her konu için Instagram hikâyesi (1080x1920) hazırlanır, onaya sunulur, **yalnızca açık onayla** altinemlakgokturk hesabında hikâye olarak paylaşılır.

## Sabitler
- Depo: `drmustafakocak/altinemlakgokturk-medya`, klasör `hikaye/`.
  - `_sablon/gundem_hikaye.py` (üretici; JSON alanları dosyanın başında), `_sablon/fonts`, `_sablon/logo`
  - `gecmis.json` — önerilen ve paylaşılan konular: `[{tarih, konu, kategori, durum: "onerildi"|"secildi"|"paylasildi"|"atlandi", kaynaklar, permalink}]`
  - Günlük klasör: `hikaye/<YYYY-AA-GG>-<kisa-konu-slug>/` → `hikaye.json`, `01.jpg`, `01.png` …, `kaynaklar.txt`
- Bilgisayar klasörü (erişilebilirse): `/Users/mustafkocak/Documents/CLAUDE/Altın Emlak Göktürk/04_ICERIKLER/Gündem Hikâyeleri/<YYYY-AA-GG> - <kısa konu>/`. Erişilemezse atla; depo yeterli.
- Ofis tel 0532 464 75 19, site altinemlakgokturk.com (şablonda sabit). Dr. Mustafa Koçak'ın şahsi numarası kullanılmaz.
- Başlangıç: `add_repo("drmustafakocak","altinemlakgokturk-medya", access "push")`, `git clone --depth 1 https://github.com/drmustafakocak/altinemlakgokturk-medya /home/claude/medya` (uzun zaman aşımı). Commit: user.name drmustafakocak; oturumun git ek satırlarını ekle; `git -c push.negotiate=true push`.

## 1) Tarama ve 3 konu önerisi
1. WebSearch ile en az 8–10 arama (bugünün tarihi/ayı ile): konut satış/kira piyasası, tapu-TKGM duyuruları, Resmî Gazete gayrimenkul düzenlemeleri, kira artış oranı/TÜFE, konut kredisi faizleri, emlak vergisi/harç, EİDS ve ilan kuralları, deprem/kentsel dönüşüm, İstanbul–Eyüpsultan–Göktürk–Kemerburgaz ulaşım/proje haberleri. Sosyal medya gündemi için de ara (ör. "emlak gündem bugün", X/Instagram/LinkedIn'de konuşulan emlak konuları; haber sitelerinin "en çok okunan" emlak haberleri). WebFetch ile ana kaynakları oku.
2. Öncelik: son 24–72 saatin gelişmeleri; ofisin hedef kitlesini (alıcı, satıcı, kiracı, mal sahibi, yatırımcı, Göktürk–Kemerburgaz) doğrudan ilgilendirenler. `gecmis.json`'da son 14 günde önerilmiş/paylaşılmış konuyu, yeni bir gelişme yoksa tekrar önerme.
3. Kaçın: siyasi/tartışmalı, kişi veya kurumları hedef alan, asayiş haberleri; Göktürk'teki imar/proje uyuşmazlıklarında taraf tutmak; doğrulanamayan söylentiler.
4. Her konu için: kısa başlık, 1 cümle "neden bugün", kategori, 2 kaynak linki (biri mümkünse resmî kaynak). `gecmis.json`'a `onerildi` olarak ekle, push.
5. SendUserMessage ile 3 konuyu numaralı ve kısa göster. Sonra AskUserQuestion (multiSelect: true): "Bugün hangi konularda hikâye hazırlayayım? Birden fazla seçebilirsin." seçenekler = 3 konu + "Bugün paylaşma". PushNotification: "Bugünün emlak gündemi: 3 hikâye konusu seçiminizi bekliyor".
6. Yanıt gelmezse hiçbir şey hazırlama/yayınlama ve bitir. "Bugün paylaşma" → ilgili kayıtlar `atlandi`, push, bitir.

## 2) Hikâye hazırlama (seçilen her konu için)
1. Konuyu derinlemesine doğrula: rakam, tarih, oran ve kural en az iki kaynakla (Resmî Gazete, mevzuat.gov.tr, TÜİK, GİB, TKGM, TCMB, Ticaret/Çevre Bakanlığı, İBB/Eyüpsultan Belediyesi öncelikli; haber siteleri destekleyici). Doğrulanamayan bilgi hikâyeye girmez. Uydurma rakam, yorum, örnek yok.
2. `hikaye.json` yaz: genelde 1 kare; konu gerektiriyorsa en fazla 3 kare. Etiket örnekleri: "SEKTÖR GÜNDEMİ", "SEKTÖR DUYURUSU", "PİYASA NOTU", "GÖKTÜRK GÜNDEMİ", "KİRACI–MAL SAHİBİ". Başlık 2–4 kısa satır (ilki sarı, xl). Özet 2–3 satır, 0–3 madde, tek cümlelik slogan. Hukuki/vergi/finans konularında `kaynak` alanına "Kaynak: … · Bilgilendirme amaçlıdır." yaz. Dil: profesyonel, anlaşılır, samimi; klişe yok ("kaçırılmayacak fırsat", "hayallerinizdeki ev", "hemen arayın").
3. `python3 hikaye/_sablon/gundem_hikaye.py <klasör>/hikaye.json <klasör>` — stderr'de "TAŞIYOR" varsa metni kısalt ve yeniden üret. Read ile her kareyi kontrol et (taşma, Türkçe karakter, yazım, rakam doğruluğu).
4. Commit + push. Bilgisayar klasörüne erişilebiliyorsa PNG'leri ve kaynaklar.txt'yi oraya da yaz (önce /mnt/user-data/outputs/ altına kopyala, sonra device_commit_files).
5. Onaya sun: SendUserFile ile tüm kareler, SendUserMessage ile kaynak linkleri ve varsa belirsizlikler. AskUserQuestion: "Bu hikâyeyi şimdi paylaşayım mı?" → Paylaş / Değişiklik var / Paylaşma. Birden fazla konu seçildiyse hepsini aynı anda sun ve konu başına onay al. PushNotification: "Gündem hikâyesi onayınızı bekliyor".
6. Değişiklik → uygula, 3'ten tekrar. Paylaşma → `atlandi`, push.

## 3) Paylaşım (yalnızca açık onayla)
1. Hesap kilidini doğrula (yukarıda). Görsel adresi commit hash'li raw GitHub: `https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/<HASH>/hikaye/<klasör>/01.jpg` — curl ile 200 doğrula.
2. Her kare için sırayla: `INSTAGRAM_POST_IG_USER_MEDIA` {ig_user_id, image_url, media_type "STORIES"} → `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` (creation_id). Kareler sırayla paylaşılır.
3. `gecmis.json` → `paylasildi` (+ varsa permalink), push. SendUserMessage + PushNotification ile "Hikâye paylaşıldı" bildir.
4. Hata: bir kez yeniden dene; olmazsa yayını zorlamadan hatayı açıkla ve JPG'leri kullanıcıya gönder (telefondan elle paylaşabilsin).

## Değişmez kurallar
- Kullanıcı bu oturumda açıkça onay vermeden Instagram'da hiçbir şey paylaşma.
- Bilgi, rakam, tarih, kaynak veya yorum uydurma.
- Yalnızca bu depoya, altinemlakgokturk Instagram hesabına ve (açıksa) kullanıcının "Altın Emlak Göktürk" klasörüne yaz.
