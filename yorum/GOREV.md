# Haftanın Yorumu — görev talimatı (bulut)

Bu görev bulutta çalışır; MacBook'un açık olması GEREKMEZ. Tek kaynak bu depodur:
`drmustafakocak/altinemlakgokturk-medya/yorum/`. Kullanıcıyla (Dr. Mustafa Koçak) Türkçe konuş; onayı telefondan verir.

- Kurallar: `yorum/_kurallar.md` (baştan sona oku, hepsine uy). Geçmiş tablosu da orada.
- Şablon: `yorum/_sablon/yorum_postu.py` → `python3 yorum/_sablon/yorum_postu.py <yorum.json> <çıktı_klasörü>`
  (Pillow gerekir: `pip install pillow --break-system-packages`).
- Haftalık klasör: `yorum/<o haftanın pazartesi tarihi YYYY-AA-GG>/` → `yorum.json`, `yorum-post.png`, `yorum-story.png`, `aciklama.md`.
- yorum.json alanları: hafta, ad_soyad, dil, alinti (görsele girecek, yorumdan birebir 1-2 cümle; yalnızca bariz yazım hataları düzeltilebilir), tam (Google'daki hali), aciklama_tr, (İngilizce ise) aciklama_en. Açıklamada müşteri adı kullanılmaz; "Dr. Mustafa Koçak" her zaman böyle yazılır.

## ADIM 1 — Bu hafta zaten onaylı mı?
Bu haftanın klasörü varsa ve `_kurallar.md` geçmişinde bu hafta "Onaylandı" yazıyorsa yeni aday arama; ADIM 3'e geç.

## ADIM 2 — Aday yorum bul ve onaya sun
Google Haritalar'da "Altın Emlak Göktürk Temsilciliği" işletmesinin yorumlarını en yeniye göre sırala. Okuma yolu (sırayla dene):
1. Bulut tarayıcısı (mcp__remote-browser__*) — yorumlar herkese açıktır, oturum gerekmez.
2. Bilgisayar açıksa uygulamanın yerleşik tarayıcısı.
3. İkisi de olmazsa: kullanıcıya SendUserMessage + PushNotification ile "Bu haftanın yorumunu okuyamadım; paylaşmak istediğin yorumun metnini ve yazanın adını buraya yapıştırır mısın?" diye sor ve cevabı bekle.

Kurallara uyan, son 30 günde yazılmış, geçmişte olmayan 5 yıldızlı yorumlardan en uygununu seç. Uygun yorum yoksa bu hafta paylaşım olmayacağını bildir, geçmişe not düş, depoya yükle ve dur.

Uygun yorum varsa post + hikâye üret, iki görsele Read ile bak, depoya commit+push et. Kullanıcıya SendUserMessage ile kısa bilgi, SendUserFile ile görselleri gönder; PushNotification at; AskUserQuestion ile onay iste (Onaylıyorum / Değişiklik var / Başka yorum seç / Bu hafta paylaşma). Onay gelmeden hiçbir şey yayınlama. Onaylanmayanı geçmişe "Onaylanmadı" yaz.

## ADIM 3 — Yayın (yalnızca onaylı içerik)
Görsel URL'si: `https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/main/yorum/<tarih>/yorum-post.png`
Composio Instagram (alias "altinemlakgokturk") ile aciklama.md'deki Instagram açıklamasıyla tek görselli post yayınla: INSTAGRAM_POST_IG_USER_MEDIA → INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH. Hikâyeyi de dene; araç desteklemiyorsa yorum-story.png'yi kullanıcıya gönder, elle paylaşmasını iste.
Yayından sonra geçmişi "Paylaşıldı (tarih)" olarak güncelle, depoya push et, permalink'i kullanıcıya bildir.

## İsteğe bağlı — bilgisayar kopyası
Bilgisayar açıksa (device_list_dir "/Users/mustafkocak/Documents/CLAUDE/Altın Emlak Göktürk" çalışıyorsa) haftanın klasörünü `04_ICERIKLER/Haftalık Google Yorumları/` altına da kopyala. Kapalıysa atla; bu bir hata değildir.

Herhangi bir adım başarısız olursa yayını zorlama; durumu kullanıcıya açıkça bildir.
