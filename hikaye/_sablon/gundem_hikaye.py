#!/usr/bin/env python3
"""Altın Emlak Göktürk — Günlük gündem hikâyesi (1080x1920).

Kullanım:
  python3 gundem_hikaye.py <hikaye.json> <cikti_klasoru>

hikaye.json (tek hikâye ya da "kareler" listesiyle 1-3 karelik seri):
{
  "kareler": [
    {
      "etiket": "SEKTÖR GÜNDEMİ",            # üstte aralıklı sarı etiket
      "tarih": "16 KASIM 2026",               # sarı rozet (isteğe bağlı)
      "baslik": [                              # satır satır; renk: "sari" | "beyaz"
        {"metin": "“Yabancıdan”", "renk": "sari", "boyut": "xl"},
        {"metin": "ilanlara", "renk": "beyaz"},
        {"metin": "EİDS kontrolü", "renk": "beyaz"}
      ],
      "ozet": "Kısa açıklama (2-3 satır).",
      "maddeler": ["...", "...", "..."],      # 0-4 madde
      "slogan": "Çerçeve altındaki tek cümle.",
      "cta": "Sorularınız için: 0532 464 75 19",
      "rozet": "yol/gorsel.png",              # isteğe bağlı, sağ üst köşe (şeffaf PNG)
      "kaynak": "Kaynak: Resmî Gazete"         # isteğe bağlı, en altta küçük gri
    }
  ]
}
Metinde **kalın** desteklenir (özet ve maddelerde sarı kalın).
Çıktı: 01.png/01.jpg, 02.png/02.jpg ... Taşma olursa stderr'e "TAŞIYOR" yazar.
"""
import json, os, sys, unicodedata
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BG = (17, 17, 18)
GOLD = (243, 189, 72)
WHITE = (255, 255, 255)
SOFT = (214, 210, 202)
GREY = (150, 150, 150)
LINE = (70, 70, 70)
FX0, FY0, FX1, FY1 = 72, 292, 1008, 1578   # çerçeve
IX0, IX1 = 148, 932                          # iç metin alanı
SITE = "altinemlakgokturk.com"
TEL = "0532 464 75 19"
UYARI = []


def F(w, s):
    ad = {"r": "400Regular", "m": "500Medium", "sb": "600SemiBold", "b": "700Bold",
          "xb": "800ExtraBold", "bl": "900Black"}[w]
    return ImageFont.truetype(os.path.join(KOK, "fonts", f"Montserrat_{ad}.ttf"), s)


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def logo(h):
    im = Image.open(os.path.join(KOK, "logo", "yatay-logo-koyu-zemin.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def spaced(d, x, y, text, font, fill, sp):
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + sp
    return x


def spaced_len(d, text, font, sp):
    return sum(d.textlength(c, font=font) + sp for c in text) - sp


def tokens(text):
    out, bold = [], False
    for i, part in enumerate(nfc(text).split("**")):
        bold = i % 2 == 1
        for w in part.split(" "):
            if w:
                out.append((w, bold))
    return out


def wrap_rich(d, text, fr, fb, maxw):
    lines, cur, curw = [], [], 0
    sp = d.textlength(" ", font=fr)
    for w, b in tokens(text):
        ww = d.textlength(w, font=fb if b else fr)
        if cur and curw + sp + ww > maxw:
            lines.append(cur); cur, curw = [], 0
        curw += (sp if cur else 0) + ww
        cur.append((w, b))
    if cur:
        lines.append(cur)
    return lines


def draw_rich(d, x, y, text, fr, fb, fill, fill_b, maxw, lh):
    sp = d.textlength(" ", font=fr)
    lines = wrap_rich(d, text, fr, fb, maxw)
    for ln in lines:
        xx = x
        for w, b in ln:
            f = fb if b else fr
            d.text((xx, y), w, font=f, fill=fill_b if b else fill)
            xx += d.textlength(w, font=f) + sp
        y += lh
    return y


def fit(d, text, weight, size, maxw, minsize=40):
    while size > minsize and d.textlength(text, font=F(weight, size)) > maxw:
        size -= 2
    if d.textlength(text, font=F(weight, size)) > maxw:
        UYARI.append(f"TAŞIYOR başlık: {text}")
    return F(weight, size)


def tablo(d, t, y):
    """t = {"basliklar": [...], "satirlar": [[...], ...], "vurgu_sutun": 1, "not": "..."}"""
    cols = [IX1 - IX0 - 3 * 156] + [156] * 3
    xs = [IX0]
    for c in cols:
        xs.append(xs[-1] + c)
    hh, rh = 62, 72
    d.rectangle([IX0, y, IX1, y + hh], fill=GOLD)
    fh = F("xb", 25)
    for j, b in enumerate(t["basliklar"]):
        b = nfc(b)
        tx = xs[j] + 20 if j == 0 else xs[j] + (cols[j] - d.textlength(b, font=fh)) / 2
        d.text((tx, y + 17), b, font=fh, fill=BG)
    y += hh
    fl, fv = F("sb", 26), F("xb", 34)
    vs = t.get("vurgu_sutun", 1)
    for i, row in enumerate(t["satirlar"]):
        if i % 2 == 0:
            d.rectangle([IX0, y, IX1, y + rh], fill=(28, 28, 29))
        for j, c in enumerate(row):
            c = nfc(c)
            if j == 0:
                d.text((xs[0] + 20, y + 22), c, font=fl, fill=WHITE)
            else:
                d.text((xs[j] + (cols[j] - d.textlength(c, font=fv)) / 2, y + 16), c, font=fv,
                       fill=GOLD if j == vs else WHITE)
        y += rh
    d.line([(IX0, y), (IX1, y)], fill=GOLD, width=3)
    y += 26
    if t.get("not"):
        y = draw_rich(d, IX0, y, t["not"], F("r", 27), F("sb", 27), SOFT, GOLD, IX1 - IX0, 38)
    return y + 30


def kare(k):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # üst etiket
    spaced(d, 78, 202, nfc(k.get("etiket", "SEKTÖR GÜNDEMİ")).upper(), F("xb", 30), GOLD, 11)

    # çerçeve + köşe tarama
    for i in range(-6, 14):
        x0 = 700 + i * 30
        d.line([(x0, FY0 + 8), (x0 + 300, FY0 + 308)], fill=(30, 30, 31), width=2)
    d.rectangle([FX0, FY0, FX1, FY1], outline=GOLD, width=6)
    # taramayı çerçeve dışında temizle
    d.rectangle([FX1 + 3, FY0, W, FY0 + 330], fill=BG)

    if k.get("rozet") and os.path.exists(k["rozet"]):
        r = Image.open(k["rozet"]).convert("RGBA")
        r = r.crop(r.getbbox())
        s = 180 / max(r.size)
        r = r.resize((round(r.width * s), round(r.height * s)), Image.LANCZOS)
        img.paste(r, (858 - r.width // 2, 445 - r.height // 2), r)

    # içerik bloğunu dikeyde hesapla: önce yükseklikleri ölç
    fr, fb = F("r", 31), F("sb", 31)
    fi = F("sb", 29)
    bas = k.get("baslik", [])
    bas_h = []
    for s in bas:
        size = {"xl": 104, "l": 84}.get(s.get("boyut"), 74)
        f = fit(d, nfc(s["metin"]), "bl" if s.get("renk") == "sari" else "xb", size, IX1 - IX0)
        bas_h.append((f, round(f.size * 1.08)))
    ozet_l = wrap_rich(d, k.get("ozet", ""), fr, fb, IX1 - IX0) if k.get("ozet") else []
    md = [wrap_rich(d, m, fi, fi, IX1 - IX0 - 80) for m in k.get("maddeler", [])]
    rozet_y = 560 if (k.get("rozet") or k.get("tarih")) else 430
    y = rozet_y
    if k.get("tarih"):
        ft = F("xb", 32)
        tw = spaced_len(d, nfc(k["tarih"]).upper(), ft, 5)
        d.rectangle([IX0, y, IX0 + tw + 40, y + 52], fill=GOLD)
        spaced(d, IX0 + 20, y + 8, nfc(k["tarih"]).upper(), ft, BG, 5)
        y += 52 + 50
    for s, (f, lh) in zip(bas, bas_h):
        d.text((IX0, y), nfc(s["metin"]), font=f, fill=GOLD if s.get("renk") == "sari" else WHITE)
        y += lh
    y += 22
    d.rectangle([IX0, y, IX0 + 110, y + 8], fill=GOLD)
    y += 46
    if ozet_l:
        y = draw_rich(d, IX0, y, k["ozet"], fr, fb, SOFT, GOLD, IX1 - IX0, 44) + 22
    if k.get("tablo"):
        y = tablo(d, k["tablo"], y)
    for i, lines in enumerate(md, 1):
        cy = y + (len(lines) * 37) // 2 - 2
        d.ellipse([IX0, cy - 28, IX0 + 56, cy + 28], fill=GOLD)
        n = str(i)
        fn = F("xb", 30)
        d.text((IX0 + 28 - d.textlength(n, font=fn) / 2, cy - 19), n, font=fn, fill=BG)
        yy = y
        for ln in lines:
            d.text((IX0 + 80, yy), " ".join(w for w, _ in ln), font=fi, fill=WHITE)
            yy += 37
        y = max(yy, cy + 28) + 30
    if y - 30 > 1450:
        UYARI.append(f"TAŞIYOR içerik: y={y} (sınır 1462) — metni kısalt")

    # alt bant
    d.line([(IX0, 1470), (IX1, 1470)], fill=LINE, width=2)
    d.rectangle([IX0, 1466, IX0 + 105, 1472], fill=GOLD)
    lg = logo(56)
    img.paste(lg, (IX0, 1497), lg)
    fs = F("m", 27)
    d.text((IX1 - d.textlength(SITE, font=fs), 1522), SITE, font=fs, fill=GREY)

    # çerçeve altı
    if k.get("slogan"):
        f = fit(d, nfc(k["slogan"]), "sb", 35, 960, 26)
        t = nfc(k["slogan"])
        d.text(((W - d.textlength(t, font=f)) / 2, 1645), t, font=f, fill=WHITE)
    cta = nfc(k.get("cta", f"Sorularınız için: {TEL}"))
    f = F("m", 31)
    d.text(((W - d.textlength(cta, font=f)) / 2, 1712), cta, font=f, fill=GOLD)
    if k.get("kaynak"):
        f = F("r", 21)
        t = nfc(k["kaynak"])
        d.text(((W - d.textlength(t, font=f)) / 2, 1800), t, font=f, fill=GREY)
    return img


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    data = json.load(open(src, encoding="utf-8"))
    kareler = data.get("kareler") or [data]
    for i, k in enumerate(kareler, 1):
        im = kare(k)
        im.save(f"{out}/{i:02d}.png", optimize=True)
        im.save(f"{out}/{i:02d}.jpg", quality=92)
        print(f"{out}/{i:02d}.jpg")
    for u in UYARI:
        print(u, file=sys.stderr)


if __name__ == "__main__":
    main()
