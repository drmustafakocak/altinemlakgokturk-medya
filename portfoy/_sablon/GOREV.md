# Haftalık Portföy Bülteni — görev talimatı (Altın Emlak Göktürk)

> **HESAP KİLİDİ (zorunlu):** Composio'da birden fazla Instagram hesabı bağlı ve varsayılan hesap altinemlakgokturk DEĞİL. Her Instagram aracını `account: "instagram_shlu-ekron"` (alias altinemlakgokturk) ile çağır. Yayından önce aynı account ile `INSTAGRAM_GET_USER_INFO` ("me") çalıştır; username `altinemlakgokturk` ve id `28885078894525477` değilse YAYINLAMA, dur ve kullanıcıya bildir. API çağrılarında ig_user_id = `28885078894525477` (17841479910444886 eski/yanlış kimliktir, kullanma).

Bu dosya, her pazartesi çalışan iki zamanlanmış görevin ortak talimatıdır. Kullanıcı Dr. Mustafa Koçak'tır; onunla Türkçe konuş. Talimatı değiştirmek için bu dosyayı güncelle (görev metinleri kısa tutuldu).

## Amaç
altinemlakgokturk.com'daki güncel ilanlardan bülteni yeniden üret, kullanıcıya ONAYA gönder ve YALNIZCA kullanıcı o oturumda açıkça onay verdikten sonra Instagram'da paylaş. Onay gelmezse hiçbir şey yayınlama. İki carousel: SATILIK ve KİRALIK. Her carousel = kapak + en fazla 8 portföy + sarı son kapak (en fazla 10 görsel). Hikâye paylaşılmaz.

## Sabitler
- GitHub deposu (public, kanonik kayıt): `drmustafakocak/altinemlakgokturk-medya`. Şablon ve durum dosyaları: `portfoy/_sablon/` (portfoy_bulten.py, site_tara.py, bulut_uret.py, portfoy_veri.json, onceki_bulten.json, kurallar.json, fonts/, logo/, danisman/, foto/).
- Haftalık durum işareti: `portfoy/_durum/<YYYY-MM-DD>.json` → `{"mod": "bilgisayar"|"bulut", "durum": "hazirlaniyor"|"onay_bekliyor"|"yayinlandi", "saat": "..."}`.
- Bilgisayardaki klasör (yalnızca bilgisayar modunda): "/Users/mustafkocak/Documents/CLAUDE/Altın Emlak Göktürk" → device_bash'te `cd "$HOME/mnt"/*/` (ad NFD). Bülten kökü `05_PORTFOY_BULTENI/`, arşiv şablonu `05_PORTFOY_BULTENI/_sablon/`.
- Instagram: Composio, hesap alias `altinemlakgokturk`, ig_user_id `28885078894525477`.
- Ofis telefonu 0532 464 75 19, mail gokturk@altinemlak.com.tr, site altinemlakgokturk.com (script içinde sabit).

## Kalıcı kurallar
- Fiyat, m², oda, kat, konum, danışman yalnızca sitedeki ilandan; bilgi uydurma. İlan başlığı/açıklaması ile alanlar çelişirse alanı kullan ve çelişkiyi onay mesajında belirt.
- "Göktürk ve çevresi" ifadesi hiçbir yerde kullanılmaz.
- SEÇİM (script yapar): önce Instagram'da hiç paylaşılmamış ilanlar (onceki_bulten.json `paylasilanlar` dışındakiler); 8'den azsa önceden paylaşılanlardan rastgele 8'e tamamlanır; 8'i aşanlar sonraki haftalara kalır. Carousel asla ikiye bölünmez.
- SIRA: önce `yeni: true` (onceki_bulten.json `son_bulten_nolar` içinde olmayan ilan; sayfada "YENİ" etiketi), sonra portföy no büyükten küçüğe.
- kurallar.json: `haric_tutulan` bültene girmez; `danisman_duzeltme` sitedeki danışmanın yerine geçer. Kullanıcı yeni kalıcı istek verirse bu dosyayı güncelle.
- Her portföy sayfasında danışman adı + unvanı. Mustafa Koçak → "Dr. Mustafa Koçak / İnşaat Yük. Mühendisi / Broker"; Ahmet Koçak → Broker; diğerleri Gayrimenkul Danışmanı (script yapar). Danışman sitede boşsa (ör. `/tr/danisman/-NNNNN`) ve kurallar.json'da yoksa TAHMİN ETME, onay mesajında sor. `danisman/` klasöründe fotoğrafı yoksa yine sor (Ufuk Bozkurt ofis tasarımlarında kullanılmaz).
- Açıklamada ilan linki "Portföy No" satırının hemen altında (yasal zorunluluk; script yapar). Açıklama ≤ 2100 karakter (script kontrol eder).
- EİDS logosu alt bantta Göktürk logosunun hemen sağında; zemine göre siyah/beyaz (script yapar).

## Akış

### 0) Başlangıç (her iki mod)
1. `add_repo("drmustafakocak","altinemlakgokturk-medya", access "push")`; `git clone --depth 1 https://github.com/drmustafakocak/altinemlakgokturk-medya /home/claude/medya` (uzun zaman aşımı).
2. Bugün T (pazartesi, Europe/Istanbul). bulten_tarihi "<gün> <Ay> <Yıl>" (ör. "23 Kasım 2026"); hafta "<T>–<T+6>" (ay değişirse "30 Kasım – 6 Aralık 2026").
3. `portfoy/_durum/<T>.json` varsa: BULUT görevi sessizce biter (bu hafta başka görev üstlendi). BİLGİSAYAR görevi de sessizce biter.
4. Yoksa hemen `{"mod": ..., "durum": "hazirlaniyor"}` yazıp commit + `git -c push.negotiate=true push` (commit mesajının sonuna oturumun git ek satırlarını ekle; user.name drmustafakocak).
5. MOD seçimi: BİLGİSAYAR görevi önce `device_list_dir` ile klasöre erişmeyi dener; erişemezse bulut moduna geçer (işarette mod'u "bulut" yap). BULUT görevi her zaman bulut modunda çalışır.

### 1) Site verisi
- Composio çalışma alanında (COMPOSIO_REMOTE_WORKBENCH) her iki modda da aynı yol: arşivi `https://codeload.github.com/drmustafakocak/altinemlakgokturk-medya/tar.gz/<HEAD-hash>` ile ya da `bulut_uret.py` içindeki yöntemle indir, `site_tara.ilanlar()` çalıştır, sonucu yazdır (fotoğraflar hariç, yalnızca metin alanları).
- (Bilgisayar modunda çalışma alanı kullanılamazsa yedek: Claude dahili tarayıcısı `mcp__remote-devices__Claude_Browser__*` ile aynı alanları topla.)

### 2) portfoy_veri.json'u yeniden yaz (container'daki klonda, `portfoy/_sablon/`)
- Sitedeki tüm uygun ilanlar (haric_tutulan hariç). Alanlar: no (int), durum, tur (Portföy Tipi'nden: Daire, Villa, Dükkan, Ofis, Arsa…), baslik (≤ 30 karakter, ilandan türetilmiş, "fırsat" klişesi yok), mahalle, ilce (İstanbul dışıysa "İlçe / İl"), fiyat (int), oda (yoksa null), net (int; "150 m 2" → 150), brut (null|int), kat ("1", "Zemin"…; yoksa null), ozellik (açıklamadan TEK ayırt edici özellik, ≤ 40 karakter, fotoğrafla çelişmesin), kiracili (satılıkta "Kiracı Var" ise true), kira_ay null, kira_tahmini false, foto ("<uuid>.jpg", foto_url'deki uuid), foto_url, danisman (kurallar.json düzeltmesi öncelikli), url (tam ilan adresi), yeni (bool).
- Önceki portfoy_veri.json'da aynı no varsa baslik ve ozellik'i KORU; diğer alanları siteden güncelle. Sitede olmayanlar düşer.
- Commit + push. Yeni hash'i not et.

### 3a) Üretim — BİLGİSAYAR modu
- `portfoy/_sablon/foto/` içinde olmayan kapak fotoğraflarını dahili tarayıcıyla al (çalışma alanından container'a dosya aktarılamaz): sekmeyi `https://cdnc.re-os.com/property/<id>.jpg?width=200` adresine götür; javascript_tool ile `fetch('/property/<id.ext>')` → createImageBitmap → genişlik ≤1100 → OffscreenCanvas JPEG 0.72 → base64; her çağrıda TEK fotoğraf: `'IMG|<uuid>|'+b64+'|'+'#'.repeat(max(0,80000-b64.length))`; `/tmp/claude-tool-results/**` dosyalarını `r'IMG\|([0-9a-f-]{36})\|([A-Za-z0-9+/=]+)'` ile çözüp `portfoy/_sablon/foto/<uuid>.jpg` yaz ve depoya ekle.
- `cd /home/claude/medya/portfoy/_sablon && python3 portfoy_bulten.py /home/claude/out` → `Portföy Bülteni <tarih>/satilik|kiralik/` (PNG + instagram_jpg/*.jpg + aciklama.txt) ve `secim.json`.
- Read ile kontrol et (kapaklar, son kapaklar, yeni ve fiyatı değişen sayfalar); sorun varsa düzelt, yeniden üret.
- Kaydet: PNG'leri ve aciklama.txt'yi /mnt/user-data/outputs/ altına kopyala; device_commit_files (force true) ile `05_PORTFOY_BULTENI/Portföy Bülteni <tarih>/Satılık|Kiralık/` içine yaz (instagram_jpg hariç; eski adla kalan sayfaları `_to_delete/`'e taşı). `_sablon/` içindeki json'ları da bilgisayara kopyala.
- Görselleri depoya ekle: `portfoy/bulten-<YYYY-MM-DD>/<seri>/*.jpg`; commit + push; adresler `https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/<hash>/portfoy/bulten-<tarih>/<seri>/<dosya>.jpg` (curl ile 200 doğrula).

### 3b) Üretim — BULUT modu
- Çalışma alanında: `exec(urllib.request.urlopen("https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/<HASH>/portfoy/_sablon/bulut_uret.py").read()); sonuc = bulut_uret("<HASH>")` (eksik fotoğrafları foto_url'den kendisi indirir, görselleri üretir ve yükler). Dönen `s3key`/`s3_url` listesini ve `secim`, `aciklama` alanlarını al; `/home/user/sonuc.json`'a kaydet.
- Görsel kontrol: çalışma alanında görsel sayısını ve boyutlarını (1080×1440) doğrula. Görselleri kendin göremezsin; onay mesajında bunu belirtmene gerek yok, bağlantıları ver.

### 4) Onaya gönder ve DUR
- İşareti `"durum": "onay_bekliyor"` yap, push.
- BİLGİSAYAR modu: SendUserFile (status proactive) ile her serinin kapağı + yeni ilan sayfaları + fiyatı değişen sayfalar. BULUT modu: SendUserMessage içinde her görselin `s3_url` bağlantısı (sıra numarasıyla; telefondan açılır).
- SendUserMessage: seride seçilenler (ilk kez / tekrar), dışarıda kalanlar, yeni eklenenler, siteden düşenler, fiyatı değişenler (önceki portfoy_veri.json ile), çelişkiler ve sorular, iki açıklama metninin tamamı. Sonunda: "Bu haliyle Instagram'da paylaşayım mı? (Onay / değişiklik isteği)".
- PushNotification: "Portföy bülteni onayınızı bekliyor: X satılık, Y kiralık (Z yeni)".
- Turu bitir, yanıt bekle. Değişiklik istenirse uygula, yeniden üret, tekrar onaya sun; kalıcı istekse kurallar.json'a yaz.

### 5) Açık onaydan sonra yayınla
- Composio (COMPOSIO_SEARCH_TOOLS ile instagram araçları; alias altinemlakgokturk). Her seri için sırayla (kapak, portföyler, son kapak) her görsele `INSTAGRAM_POST_IG_USER_MEDIA` {ig_user_id, is_carousel_item: true, ve BİLGİSAYAR modunda `image_url` (raw GitHub, commit hash'li) / BULUT modunda `image_file` {name, mimetype "image/jpeg", s3key}} → hepsi `INSTAGRAM_GET_POST_STATUS` ile FINISHED → `INSTAGRAM_CREATE_CAROUSEL_CONTAINER` {ig_user_id, children: [sıralı id'ler], caption: aciklama} → `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` {ig_user_id, creation_id: parent}. Önce SATILIK, ~5 dk sonra KİRALIK. Hatalı görseli yeniden oluştur; düzelmezse dur ve bildir.
- `INSTAGRAM_GET_IG_MEDIA` ile permalink'leri al.
- onceki_bulten.json: `yayin_tarihi` = T; `son_bulten_nolar` = bu haftaki portfoy_veri.json'daki tüm no'lar; `paylasilanlar` = önceki ∪ yayınlanan serilerin secim no'ları. İşaret `"durum": "yayinlandi"`. Commit + push (bilgisayar modunda `_sablon/` kopyasını da güncelle).
- SendUserMessage: post linkleri. PushNotification: "Portföy bülteni yayında: X satılık, Y kiralık".

## Hata durumları
- Composio Instagram bağlantısı yoksa/süresi dolduysa: bülteni hazırla, onay mesajında bağlantının yenilenmesi gerektiğini söyle; yayın yapma.
- Bulut modunda üretilen bültenin bilgisayardaki klasöre kopyası yoktur; kullanıcı isterse sonraki bilgisayar oturumunda depodaki `portfoy/_sablon` ve görsellerden eşitlenir.
