#!/usr/bin/env python3
"""Altın Emlak Göktürk — Haftalık Portföy Bülteni üreticisi (v2).

Kullanım: python3 portfoy_bulten.py <cikti_klasoru>
Girdi (bu dosyanın yanında): portfoy_veri.json, foto/, danisman/, logo/, fonts/
Çıktı: <cikti>/Portföy Bülteni <tarih>/satilik|kiralik/ 01_kapak.png, 02_...png, aciklama.txt

Her seri (satılık/kiralık) = kapak + en fazla 8 portföy + beyaz son kapak (en fazla 10 görsel).
Seçim: önce hiç paylaşılmamış ilanlar (onceki_bulten.json "paylasilanlar" listesinde olmayanlar),
8'e tamamlamak için daha önce paylaşılanlardan rastgele. Sıra: önce kurallar.json oncelikli_bolgeler (Göktürk, Kemerburgaz), sonra "yeni": true, sonra portföy no büyükten küçüğe.
"""
import json, os, sys, random, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageChops

KOK = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1440                     # 3:4
SARI = (243, 189, 72)                 # #F3BD48
SIYAH = (14, 14, 15)
ANTRASIT = (24, 25, 27)
KART = (36, 37, 40)
BEYAZ = (255, 255, 255)
GRI = (170, 170, 172)
CIZGI = (62, 62, 66)
OFIS = "Altın Emlak Göktürk"
TELEFON = "0532 464 75 19"
MAIL = "gokturk@altinemlak.com.tr"
SITE = "altinemlakgokturk.com"
BAND_Y = 1296
M = 56                                 # kenar boşluğu
HASHTAG = {
    "Satılık": "#satılıkdaire #satılıkev #gayrimenkul #emlak #istanbul #altinemlakgokturk #altınemlak",
    "Kiralık": "#kiralıkdaire #kiralıkev #gayrimenkul #emlak #istanbul #altinemlakgokturk #altınemlak",
}
UNVAN = {"Mustafa Koçak": ("Dr. Mustafa Koçak", "İnşaat Yük. Mühendisi / Broker"),
         "Ahmet Koçak": ("Ahmet Koçak", "Broker")}


# ---------- yardımcılar ----------
def F(agirlik, boyut):
    ad = {"regular": "400Regular", "medium": "500Medium", "semibold": "600SemiBold",
          "bold": "700Bold", "extrabold": "800ExtraBold", "black": "900Black"}[agirlik]
    return ImageFont.truetype(os.path.join(KOK, "fonts", f"Montserrat_{ad}.ttf"), boyut)


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def para(n):
    return f"{n:,.0f}".replace(",", ".") + " ₺"


def nfc(s):
    return unicodedata.normalize("NFC", s)


def danisman_bilgi(ad):
    return UNVAN.get(ad, (ad, "Gayrimenkul Danışmanı"))


def konum(p):
    return f"{p['mahalle']}, {p['ilce']}" if p["mahalle"] != p["ilce"] else p["ilce"]


def cover_fit(im, w, h, odak_y=0.5):
    im = im.convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int((im.height - h) * odak_y)
    return im.crop((x, y, x + w, y + h))


def yuvarlak_maske(w, h, r):
    m = Image.new("L", (w * 3, h * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=r * 3, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def foto(p, w, h, r=24, sadece_ust=False):
    im = cover_fit(Image.open(os.path.join(KOK, "foto", p["foto"])), w, h)
    out = Image.new("RGBA", (w, h))
    m = yuvarlak_maske(w, h + r, r).crop((0, 0, w, h)) if sadece_ust else yuvarlak_maske(w, h, r)
    out.paste(im, (0, 0), m)
    return out


def logo_yukle(ad, yukseklik):
    im = Image.open(os.path.join(KOK, "logo", ad)).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * yukseklik / im.height), yukseklik), Image.LANCZOS)


def zemine_uyarla(logo, zemin, xy):
    """Koyu zeminde logodaki siyahlar beyaz, açık zeminde siyah olur."""
    x, y = xy
    alan = zemin.crop((x, y, x + logo.width, y + logo.height)).convert("L")
    hedef = 255 if ImageStat.Stat(alan).mean[0] < 128 else 0
    out = logo.copy()
    px = out.load()
    for j in range(out.height):
        for i in range(out.width):
            r, g, b, a = px[i, j]
            if a and max(r, g, b) < 90 and max(r, g, b) - min(r, g, b) < 30:
                px[i, j] = (hedef, hedef, hedef, a)
    return out


def hap(d, xy, metin, font, zemin, yazi, pad=(20, 11), sag=False, cerceve=None):
    x, y = xy
    b = d.textbbox((0, 0), metin, font=font)
    w, h = b[2] - b[0] + 2 * pad[0], b[3] - b[1] + 2 * pad[1]
    if sag:
        x -= w
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=zemin, outline=cerceve, width=2 if cerceve else 0)
    d.text((x + pad[0] - b[0], y + pad[1] - b[1]), metin, font=font, fill=yazi)
    return w, h


def sar(d, metin, font, genislik, max_satir=2):
    kel, satirlar, cur = metin.split(), [], ""
    for k in kel:
        t = (cur + " " + k).strip()
        if d.textlength(t, font=font) <= genislik:
            cur = t
        else:
            satirlar.append(cur)
            cur = k
    satirlar.append(cur)
    if len(satirlar) > max_satir:
        satirlar = satirlar[:max_satir]
        while d.textlength(satirlar[-1] + "…", font=font) > genislik:
            satirlar[-1] = satirlar[-1].rsplit(" ", 1)[0]
        satirlar[-1] += "…"
    return satirlar


def pin(d, x, y, r, renk, ic=ANTRASIT):
    """Konum iğnesi; (x, y) iğnenin ucu."""
    d.ellipse((x - r, y - 2.6 * r, x + r, y - 0.6 * r), fill=renk)
    d.polygon([(x - r * 0.86, y - 1.2 * r), (x + r * 0.86, y - 1.2 * r), (x, y)], fill=renk)
    d.ellipse((x - r * 0.4, y - 2.0 * r, x + r * 0.4, y - 1.2 * r), fill=ic)


def avatar(ad, boyut, halka=SARI):
    """Danışman fotoğrafı: baş, dairenin üst çizgisine yakın (üstte fazla boşluk yok)."""
    yol = None
    for f in os.listdir(os.path.join(KOK, "danisman")):
        if nfc(os.path.splitext(f)[0]) == nfc(ad):
            yol = os.path.join(KOK, "danisman", f)
    if not yol:
        raise SystemExit(f"Danışman fotoğrafı yok: {ad} — danisman/ klasörüne ekleyin")
    im = Image.open(yol)
    if im.mode == "RGBA" and im.getextrema()[3][0] < 255:
        maske = im.getchannel("A").point(lambda a: 255 if a > 40 else 0)
        rgb = Image.new("RGB", im.size, (235, 235, 236))
        rgb.paste(im.convert("RGB"), (0, 0), im.getchannel("A"))
    else:
        rgb = im.convert("RGB")
        kose = Image.new("RGB", rgb.size, rgb.getpixel((4, 4)))
        maske = ImageChops.difference(rgb, kose).convert("L").point(lambda v: 255 if v > 28 else 0)
    w, h = rgb.size
    # başın üstü: kişiye ait piksellerin genişliğin %3'ünü geçtiği ilk satır
    bas = 0
    for y in range(h):
        if ImageStat.Stat(maske.crop((0, y, w, y + 1))).mean[0] / 255 > 0.03:
            bas = y
            break
    # baş genişliği: başın üstünden biraz aşağıdaki satırlarda kişinin en geniş yeri
    def genislik(y):
        bb = maske.crop((0, y, w, y + 1)).getbbox()
        return (bb[0], bb[2]) if bb else (w // 2, w // 2)
    ornek = [genislik(min(h - 1, bas + int(h * t))) for t in (0.04, 0.06, 0.08)]
    sol, sag = min(o[0] for o in ornek), max(o[1] for o in ornek)
    bas_w = max(sag - sol, w * 0.08)
    cx = (sol + sag) // 2
    k = int(min(w, h, bas_w * 2.5))
    y0 = max(0, bas - int(k * 0.05))
    x0 = max(0, min(w - k, cx - k // 2))
    kare = rgb.crop((x0, y0, x0 + k, y0 + k)).resize((boyut, boyut), Image.LANCZOS)
    out = Image.new("RGBA", (boyut + 8, boyut + 8), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, boyut + 7, boyut + 7), fill=halka)
    m = Image.new("L", (boyut * 3, boyut * 3), 0)
    ImageDraw.Draw(m).ellipse((0, 0, boyut * 3, boyut * 3), fill=255)
    out.paste(kare, (4, 4), m.resize((boyut, boyut), Image.LANCZOS))
    return out


def alt_bant(img, acik=False):
    """Alt bant. acik=True: beyaz zeminli son kapak için açık zemin logosu."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, BAND_Y, W, H), fill=BEYAZ if acik else SIYAH)
    d.rectangle((0, BAND_Y, W, BAND_Y + 4), fill=SARI)
    logo = logo_yukle("yatay-logo-acik-zemin.png" if acik else "yatay-logo-koyu-zemin.png", 78)
    img.alpha_composite(logo, (M, BAND_Y + (H - BAND_Y - logo.height) // 2 + 2))
    eids = logo_yukle("eidslogo.png", 92)
    exy = (M + logo.width + 26, BAND_Y + (H - BAND_Y - eids.height) // 2 + 2)
    img.alpha_composite(zemine_uyarla(eids, img, exy), exy)
    d.text((W - M, BAND_Y + 52), TELEFON, font=F("bold", 32), fill=SIYAH if acik else BEYAZ, anchor="rm")
    d.text((W - M, BAND_Y + 94), SITE, font=F("semibold" if acik else "medium", 23),
           fill=(150, 108, 20) if acik else SARI, anchor="rm")


def zemin():
    """Koyu zemin + ince mimari çizgi dokusu (sarı imza aksanıyla)."""
    img = Image.new("RGBA", (W, H), ANTRASIT + (255,))
    d = ImageDraw.Draw(img)
    for x in range(M, W, 96):
        d.line((x, 0, x, BAND_Y), fill=(30, 31, 33), width=1)
    return img


# ---------- kapak ----------
def kapak(durum, liste, hafta):
    img = zemin()
    d = ImageDraw.Draw(img)
    hap(d, (M, 64), "HAFTALIK PORTFÖY BÜLTENİ", F("bold", 24), SARI, SIYAH)
    d.text((W - M, 86), hafta, font=F("semibold", 26), fill=BEYAZ, anchor="rm")

    fb = F("black", 150)
    d.text((M - 6, 170), tr_upper(durum), font=fb, fill=BEYAZ)
    bb = d.textbbox((M - 6, 170), tr_upper(durum), font=fb)
    d.text((M, bb[3] + 22), "PORTFÖYLER", font=F("bold", 52), fill=SARI)
    yeni = sum(1 for p in liste if p.get("yeni"))
    alt = f"Bu hafta {len(liste)} {durum.lower()} portföy" + (f"  ·  {yeni} yeni" if yeni else "")
    d.text((M, bb[3] + 100), alt, font=F("medium", 32), fill=GRI)

    # 3 küçük portföy kartı (hiçbiri ana fotoğraf değil)
    secim = liste[:3]
    n = len(secim)
    gap = 24
    kw = (W - 2 * M - gap * 2) // 3
    toplam_w = n * kw + (n - 1) * gap
    x0 = (W - toplam_w) // 2
    ky, fh = 500, 400
    for i, p in enumerate(secim):
        x = x0 + i * (kw + gap)
        d.rounded_rectangle((x, ky, x + kw, ky + fh + 210), radius=24, fill=KART)
        img.alpha_composite(foto(p, kw, fh, 24, sadece_ust=True), (x, ky))
        if p.get("yeni"):
            hap(d, (x + 14, ky + 14), "YENİ", F("bold", 18), SARI, SIYAH, pad=(14, 8))
        tx = x + 20
        d.text((tx, ky + fh + 22), para(p["fiyat"]) + (" /ay" if durum == "Kiralık" else ""),
               font=F("extrabold", 30), fill=SARI)
        bilgi = " · ".join(x for x in [p.get("oda") or p["tur"], f"{p['net']} m²" if p.get("net") else None] if x)
        d.text((tx, ky + fh + 72), bilgi, font=F("semibold", 24), fill=BEYAZ)
        pin(d, tx + 9, ky + fh + 146, 8, SARI, KART)
        sat = sar(d, konum(p), F("medium", 20), kw - 60, 2)
        for j, s in enumerate(sat):
            d.text((tx + 28, ky + fh + 116 + j * 26), s, font=F("medium", 20), fill=GRI)

    kalan = len(liste) - n
    yy = ky + fh + 210 + 52
    d.text((M, yy), f"+{kalan} portföy daha" if kalan > 0 else "Detaylar sonraki sayfalarda",
           font=F("semibold", 28), fill=BEYAZ)
    d.text((W - M - 46, yy), "Kaydırın", font=F("bold", 28), fill=SARI, anchor="ra")
    ax, ay = W - M - 34, yy + 17
    d.line((ax, ay, ax + 28, ay), fill=SARI, width=4)
    d.polygon([(ax + 32, ay), (ax + 18, ay - 10), (ax + 18, ay + 10)], fill=SARI)
    alt_bant(img)
    return img.convert("RGB")


# ---------- portföy sayfası ----------
def portfoy_sayfasi(p, sira, toplam):
    img = zemin()
    d = ImageDraw.Draw(img)

    hap(d, (M, 52), f"{tr_upper(p['durum'])}  ·  {tr_upper(p['tur'])}", F("bold", 22), SARI, SIYAH)
    if p.get("yeni"):
        hap(d, (M + d.textlength(f"{tr_upper(p['durum'])}  ·  {tr_upper(p['tur'])}", font=F("bold", 22)) + 56, 52),
            "YENİ", F("bold", 22), ANTRASIT, SARI, cerceve=SARI)
    hap(d, (W - M, 52), f"{sira:02d} / {toplam:02d}", F("semibold", 22), KART, BEYAZ, sag=True)

    # çerçeveli fotoğraf kartı: yüksekliği metin bloğuna göre ayarlanır
    sy = 1086
    fb = F("bold", 54)
    satirlar = sar(d, p["baslik"], fb, W - 2 * M)
    blok = 50 + len(satirlar) * 64 + 10 + 44 + (46 if p.get("ozellik") else 0) + 44
    fy, fw = 122, W - 2 * M
    fh = sy - 22 - blok - fy
    img.alpha_composite(foto(p, fw, fh, 28), (M, fy))
    d.rectangle((M, fy + fh + 18, M + 120, fy + fh + 24), fill=SARI)

    y = fy + fh + 50
    for s in satirlar:
        d.text((M, y), s, font=fb, fill=BEYAZ)
        y += 64
    y += 10
    pin(d, M + 12, y + 32, 10, SARI)
    d.text((M + 36, y), konum(p), font=F("medium", 28), fill=GRI)
    if p.get("ozellik"):
        d.text((M, y + 46), p["ozellik"], font=F("semibold", 26), fill=SARI)

    # bilgi satırı
    d.line((M, sy - 22, W - M, sy - 22), fill=CIZGI, width=2)
    kalemler = []
    if p.get("oda"):
        kalemler.append((p["oda"], "ODA"))
    if p.get("net"):
        kalemler.append((f"{p['net']} m²", "NET ALAN"))
    elif p.get("brut"):
        kalemler.append((f"{p['brut']} m²", "BRÜT ALAN"))
    if p.get("kat"):
        kalemler.append((f"{p['kat']}." if str(p["kat"]).isdigit() else str(p["kat"]), "KAT"))
    x = M
    for deger, etiket in kalemler:
        d.text((x, sy), deger, font=F("bold", 36), fill=BEYAZ)
        d.text((x, sy + 48), etiket, font=F("semibold", 17), fill=GRI)
        x += max(d.textlength(deger, font=F("bold", 36)), d.textlength(etiket, font=F("semibold", 17))) + 40
    d.text((W - M, sy - 4), para(p["fiyat"]), font=F("extrabold", 50), fill=SARI, anchor="ra")
    d.text((W - M, sy + 52), "AYLIK KİRA" if p["durum"] == "Kiralık" else "SATIŞ FİYATI",
           font=F("semibold", 17), fill=GRI, anchor="ra")
    if p["durum"] == "Satılık" and p.get("kiracili"):
        hap(d, (M + 20, fy + 20), "KİRACILI", F("bold", 20), BEYAZ, SIYAH, pad=(16, 9))

    # danışman (her sayfada ad + unvan zorunlu)
    if not p.get("danisman"):
        raise SystemExit(f"Portföy {p['no']} için danışman yok")
    cy = 1176
    av = avatar(p["danisman"], 84)
    img.alpha_composite(av, (M, cy))
    ad, unvan = danisman_bilgi(p["danisman"])
    d.text((M + 112, cy + 14), ad, font=F("bold", 28), fill=BEYAZ)
    d.text((M + 112, cy + 52), unvan, font=F("medium", 21), fill=GRI)
    d.text((W - M, cy + 18), "PORTFÖY NO", font=F("semibold", 17), fill=GRI, anchor="ra")
    d.text((W - M, cy + 44), str(p["no"]), font=F("bold", 28), fill=BEYAZ, anchor="ra")

    alt_bant(img)
    return img.convert("RGB")


# ---------- son kapak (beyaz zemin, siteye yönlendirme) ----------
def son_kapak(durum):
    """Son kapak: kurumsal sarı zemin; siteye yönlendirme. Alt bant beyaz (logo sarı zeminde kaybolmasın)."""
    img = Image.new("RGBA", (W, H), SARI + (255,))
    d = ImageDraw.Draw(img)
    IKINCIL = (70, 52, 12)
    for x in range(M, W, 96):
        d.line((x, 0, x, BAND_Y), fill=(233, 179, 62), width=1)
    hap(d, (M, 64), "TÜM PORTFÖYLERİMİZ", F("bold", 24), SIYAH, SARI)

    y = 190
    for s_ in ["Diğer", "portföylerimiz", "web sitemizde"]:
        d.text((M - 4, y), s_, font=F("black", 92), fill=SIYAH)
        y += 104
    d.rectangle((M, y + 18, M + 140, y + 26), fill=SIYAH)
    y += 64
    alt = {"Satılık": "Satılık ve kiralık tüm ilanlarımızı güncel fiyat,",
           "Kiralık": "Kiralık ve satılık tüm ilanlarımızı güncel fiyat,"}[durum]
    d.text((M, y), alt, font=F("medium", 32), fill=IKINCIL)
    d.text((M, y + 46), "fotoğraf ve detaylarıyla inceleyebilirsiniz.", font=F("medium", 32), fill=IKINCIL)

    by = y + 140
    d.rounded_rectangle((M, by, W - M, by + 132), radius=66, fill=SIYAH)
    d.text((M + 56, by + 66), SITE, font=F("extrabold", 46), fill=BEYAZ, anchor="lm")
    cx, cy = W - M - 66, by + 66
    d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=SARI)
    d.line((cx - 18, cy, cx + 16, cy), fill=SIYAH, width=7)
    d.polygon([(cx + 22, cy), (cx + 4, cy - 16), (cx + 4, cy + 16)], fill=SIYAH)

    qy = by + 186
    qr = Image.open(os.path.join(KOK, "logo", "qr_ilanlar.png")).convert("RGB").resize((200, 200), Image.NEAREST)
    d.rounded_rectangle((M - 14, qy - 14, M + 214, qy + 214), radius=18, fill=BEYAZ)
    img.paste(qr, (M, qy))
    tx = M + 256
    d.text((tx, qy + 18), "Kodu okutun,", font=F("bold", 30), fill=SIYAH)
    d.text((tx, qy + 56), "ilanlarımıza gidin", font=F("bold", 30), fill=SIYAH)
    d.text((tx, qy + 118), TELEFON, font=F("semibold", 26), fill=IKINCIL)
    d.text((tx, qy + 156), MAIL, font=F("semibold", 26), fill=IKINCIL)
    alt_bant(img, acik=True)
    ImageDraw.Draw(img).rectangle((0, BAND_Y, W, BAND_Y + 4), fill=SIYAH)
    return img.convert("RGB")


# ---------- açıklama ----------
def aciklama(durum, liste, hafta):
    giris = {"Satılık": "Bu haftanın satılık portföyleri bir arada. 🏡",
             "Kiralık": "Bu haftanın kiralık portföyleri bir arada. 🔑"}[durum]
    ust = [giris, f"📅 {hafta}", "Kaydırarak her portföyü inceleyebilirsiniz.", ""]
    alt = ["Detaylı bilgi ve yer görme randevusu için bize mesaj atabilir ya da arayabilirsiniz.",
           f"📞 {TELEFON}", f"✉️ {MAIL}", f"🌐 {SITE}", "",
           "Diğer tüm portföylerimiz için: www.altinemlakgokturk.com", "", OFIS, "", HASHTAG[durum]]

    def blok(kisa):
        s = []
        for i, p in enumerate(liste, 1):
            ad, _ = danisman_bilgi(p["danisman"])
            bas = f"{i}) {'🆕 ' if p.get('yeni') else ''}{p['baslik']} — {konum(p)}"
            ozet = " | ".join(x for x in [p.get("oda") or p["tur"], f"{p['net']} m²" if p.get("net") else None,
                                          para(p["fiyat"]) + (" / ay" if durum == "Kiralık" else "")] if x)
            s += [bas] + {0: [ozet, f"Danışman: {ad}"], 1: [ozet], 2: []}[kisa] + [f"Portföy No: {p['no']}", p["url"], ""]
        return s

    say = lambda t: len(t.encode("utf-16-le")) // 2
    for seviye in (0, 1, 2):                    # ilan linki yasal zorunluluk: kısaltılan özet, link değil
        metin = "\n".join(ust + blok(seviye) + alt)
        if say(metin) <= 2100:
            break
    if say(metin) > 2100:
        raise SystemExit(f"{durum} açıklaması 2100 karakteri aşıyor ({say(metin)}) — seriyi ikiye bölün")
    return metin


ADET = 8                                       # carousel: kapak + en fazla 8 portföy + son kapak = 10 görsel


def sec(tum, paylasilanlar, tohum):
    """Önce hiç paylaşılmamış ilanlar (yeniler başta); 8'e tamamlamak için daha önce paylaşılanlardan rastgele."""
    sira = lambda p: (not p.get("yeni"), -int(p["no"]))
    hic = sorted([p for p in tum if int(p["no"]) not in paylasilanlar], key=sira)
    eski = [p for p in tum if int(p["no"]) in paylasilanlar]
    secilen = hic[:ADET]
    if len(secilen) < ADET and eski:
        rnd = random.Random(tohum)
        secilen += rnd.sample(eski, min(len(eski), ADET - len(secilen)))
    return sorted(secilen, key=lambda p: (not oncelikli(p),) + sira(p))


def oncelikli(p):
    """kurallar.json oncelikli_bolgeler (ör. Göktürk, Kemerburgaz) mahalle/ilçede geçiyorsa carousel'de öne alınır."""
    yol = os.path.join(KOK, "kurallar.json")
    bolgeler = json.load(open(yol, encoding="utf-8")).get("oncelikli_bolgeler", []) if os.path.exists(yol) else []
    yer = f"{p.get('mahalle') or ''} {p.get('ilce') or ''}".casefold()
    return any(b.casefold() in yer for b in bolgeler)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(KOK, "out")
    veri = json.load(open(os.path.join(KOK, "portfoy_veri.json"), encoding="utf-8"))
    yol = os.path.join(KOK, "onceki_bulten.json")
    paylasilanlar = set(json.load(open(yol, encoding="utf-8")).get("paylasilanlar", [])) if os.path.exists(yol) else set()
    kok = os.path.join(out, f"Portföy Bülteni {veri['bulten_tarihi']}")
    secim = {}
    for durum, klasor in (("Satılık", "satilik"), ("Kiralık", "kiralik")):
        tum = [p for p in veri["portfoyler"] if p["durum"] == durum]
        if not tum:
            continue
        liste = sec(tum, paylasilanlar, veri["bulten_tarihi"] + durum)
        k = os.path.join(kok, klasor)
        os.makedirs(k, exist_ok=True)
        sayfalar = [("01_kapak", kapak(durum, liste, veri["hafta"]))]
        for i, p in enumerate(liste, 2):
            sayfalar.append((f"{i:02d}_portfoy_{p['no']}", portfoy_sayfasi(p, i - 1, len(liste))))
        sayfalar.append((f"{len(liste) + 2:02d}_son_kapak", son_kapak(durum)))
        ig = os.path.join(k, "instagram_jpg")
        os.makedirs(ig, exist_ok=True)
        for ad, im in sayfalar:
            im.save(os.path.join(k, ad + ".png"), optimize=True)
            im.save(os.path.join(ig, ad + ".jpg"), quality=92)      # Instagram API yalnızca JPEG kabul eder
        open(os.path.join(k, "aciklama.txt"), "w", encoding="utf-8").write(aciklama(durum, liste, veri["hafta"]))
        secim[durum] = [int(p["no"]) for p in liste]
        disarida = [int(p["no"]) for p in tum if p not in liste]
        print(durum, len(liste), "portföy seçildi →", k, "| bu hafta dışarıda kalan:", disarida)
    json.dump(secim, open(os.path.join(kok, "secim.json"), "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
