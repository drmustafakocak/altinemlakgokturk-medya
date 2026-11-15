#!/usr/bin/env python3
"""Altın Emlak Göktürk — "Haftanın Yorumu" post + hikaye üreticisi (sarı zemin).

Kullanım: python3 yorum_postu.py <yorum.json> <cikti_klasoru>
yorum.json: {"ad_soyad", "dil": "tr"|"en", "alinti", "tam", "aciklama_tr", ["aciklama_en"], "hafta": "YYYY-MM-DD"}
Girdi klasörü (bu dosyanın yanında): fonts/, logo/yatay-logo-koyu-zemin.png
Çıktı: <cikti>/yorum-post.png (1080x1440), yorum-story.png (1080x1920), aciklama.md
Görselde yalnızca ad ve soyadın baş harfleri yazılır (ör. "M. Ç.").
"""
import json, math, os, sys, unicodedata
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.abspath(__file__))
SARI = (243, 189, 72)
SARI_KOYU = (222, 166, 46)
SIYAH = (14, 14, 15)
KAHVE = (74, 56, 20)
BEYAZ = (255, 255, 255)
SITE = "altinemlakgokturk.com"
HT_TR = "#göktürk #kemerburgaz #eyüpsultan #müşteriyorumu #haftanınyorumu #altinemlakgokturk #altınemlak"
HT_EN = "#göktürk #kemerburgaz #istanbulrealestate #clientreview #altinemlakgokturk #altınemlak"


def F(agirlik, boyut):
    ad = {"regular": "400Regular", "medium": "500Medium", "semibold": "600SemiBold",
          "bold": "700Bold", "extrabold": "800ExtraBold"}[agirlik]
    return ImageFont.truetype(os.path.join(KOK, "fonts", f"Montserrat_{ad}.ttf"), boyut)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def bas_harfler(ad_soyad):
    """'Murat ÇİMEN' -> 'M. Ç.'  /  'R SH' -> 'R. S.'"""
    parcalar = [p for p in nfc(ad_soyad).replace("“", " ").replace("”", " ").split() if p[0].isalpha()]
    if len(parcalar) >= 2:
        parcalar = [parcalar[0], parcalar[-1]]
    return " ".join(tr_upper(p[0]) + "." for p in parcalar)


def logo(ad, yukseklik):
    im = Image.open(os.path.join(KOK, "logo", ad)).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * yukseklik / im.height), yukseklik), Image.LANCZOS)


def satirla(d, metin, font, genislik):
    satirlar, s = [], ""
    for k in metin.split():
        aday = (s + " " + k).strip()
        if d.textlength(aday, font=font) <= genislik:
            s = aday
        else:
            satirlar.append(s)
            s = k
    if s:
        satirlar.append(s)
    return satirlar


def aralikli(d, xy, metin, font, renk, aralik):
    x, y = xy
    for c in metin:
        d.text((x, y), c, font=font, fill=renk)
        x += d.textlength(c, font=font) + aralik


def yildiz(d, cx, cy, r, renk):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=renk)


def ciz(r, W, H, story=False):
    img = Image.new("RGBA", (W, H), SARI + (255,))
    d = ImageDraw.Draw(img)
    # mimari çizgiler (sağ üst) ve büyük silik tırnak
    for i in range(8):
        x0 = W - 460 + i * 66
        d.line([(x0, 0), (x0 + 460, 460)], fill=SARI_KOYU, width=3)
    M = 84
    ust = 250 if story else 96
    en = r["dil"] == "en"

    # üst etiket
    d.rectangle([M, ust + 9, M + 56, ust + 15], fill=SIYAH)
    aralikli(d, (M + 76, ust - 6), "HAFTANIN YORUMU", F("extrabold", 34 if story else 31), SIYAH, 5)
    if en:
        aralikli(d, (M + 76, ust + 44), "YABANCI MÜŞTERİLERİMİZDEN", F("bold", 23 if story else 21), KAHVE, 3)
        aralikli(d, (M + 76, ust + 76), "FROM OUR INTERNATIONAL CLIENTS", F("medium", 21 if story else 19), KAHVE, 3)

    # tırnak
    qy = ust + (190 if story else 120 if en else 70)
    d.text((M - 14, qy), "“", font=F("extrabold", 330 if story else 290), fill=SIYAH)

    # siyah alt bant
    band_h = 170 if story else 160
    band_y = H - band_h - (250 if story else 0)
    d.rectangle([0, band_y, W, band_y + band_h], fill=SIYAH)
    if story:
        d.rectangle([0, band_y + band_h, W, H], fill=SARI)
    lg = logo("yatay-logo-koyu-zemin.png", 76 if story else 72)
    img.alpha_composite(lg, (M, band_y + (band_h - lg.height) // 2))
    fs = F("semibold", 28)
    d.text((W - M - d.textlength(SITE, font=fs), band_y + (band_h - 34) // 2), SITE, font=fs, fill=BEYAZ)

    # yorum metni
    tx_top = qy + (250 if story else 215)
    tx_bot = band_y - 250
    gen = W - 2 * M
    metin = nfc(r["alinti"])
    for boy in range(74 if story else 66, 33, -2):
        f = F("semibold", boy)
        sat = satirla(d, metin, f, gen)
        lh = int(boy * 1.4)
        if len(sat) * lh <= tx_bot - tx_top:
            break
    yy = tx_top + max(0, (tx_bot - tx_top - len(sat) * lh) // 3)
    for s in sat:
        d.text((M, yy), s, font=f, fill=SIYAH)
        yy += lh

    # yıldızlar + baş harfler
    yb = yy + 44
    for i in range(5):
        yildiz(d, M + 22 + i * 52, yb + 22, 22, SIYAH)
    yb += 76
    d.text((M, yb), bas_harfler(r["ad_soyad"]), font=F("extrabold", 54 if story else 50), fill=SIYAH)
    yb += 72 if story else 66
    alt = "Google yorumu" + (" · Google review" if en else "")
    d.text((M, yb), alt, font=F("medium", 27), fill=KAHVE)
    return img.convert("RGB")


def aciklama_md(r):
    en = r["dil"] == "en"
    out = [f"# Haftanın Yorumu — {r.get('hafta', '')} — {bas_harfler(r['ad_soyad'])} (ONAY BEKLİYOR)", "",
           "Format: Post 1080 × 1440 (3:4) · Hikaye 1080 × 1920 (9:16)", "", "## Instagram açıklaması", ""]
    if en:
        out += ["🇹🇷", r["aciklama_tr"], "", "—", "", "🇬🇧", r["aciklama_en"], "", HT_EN]
    else:
        out += [r["aciklama_tr"], "", HT_TR]
    out += ["", "## Yorumun Google'daki hali (kaynak)", "", "> " + r["tam"], ""]
    return "\n".join(out)


def main():
    r = json.load(open(sys.argv[1], encoding="utf-8"))
    cikti = sys.argv[2]
    os.makedirs(cikti, exist_ok=True)
    ciz(r, 1080, 1440).save(os.path.join(cikti, "yorum-post.png"), optimize=True)
    ciz(r, 1080, 1920, story=True).save(os.path.join(cikti, "yorum-story.png"), optimize=True)
    open(os.path.join(cikti, "aciklama.md"), "w", encoding="utf-8").write(aciklama_md(r))


if __name__ == "__main__":
    main()
