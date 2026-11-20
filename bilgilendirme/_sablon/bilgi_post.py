#!/usr/bin/env python3
"""Altın Emlak Göktürk — Cumartesi bilgilendirme serisi: carousel + hikâye + (isteğe bağlı) Reels.

Kullanım:
  python3 bilgi_post.py <icerik.json> <cikti_klasoru>            # carousel (1080x1440) + hikâye kapağı (1080x1920)
  python3 bilgi_post.py <icerik.json> <cikti_klasoru> --reels    # ek olarak reels.mp4 (1080x1920, sessiz)

icerik.json alanları (örnek: ../2026-11-21/icerik.json):
  etiket, seri, sayfalar[ kapak | madde | son ], aciklama, kaynaklar
  madde.grafik.tip: akis | takvim | liste | oran | buyuk | kontrol | (yok)
  Metinde **kalın** yazım desteklenir.
Çıktı: post/01.png ... (PNG), instagram_jpg/01.jpg ..., story.png, aciklama.txt, [reels.mp4]
"""
import json, os, re, subprocess, sys, unicodedata
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.abspath(__file__))
W, H, M = 1080, 1440, 84
GOLD = (243, 189, 72)
GOLD_D = (139, 98, 18)
BG = (17, 17, 18)
CREAM = (244, 240, 233)
INK = (16, 16, 17)
GREY = (150, 150, 150)
GREY_D = (105, 100, 92)
LINE_L = (222, 214, 200)
LINE_D = (58, 58, 58)
WHITE = (255, 255, 255)
SITE = "altinemlakgokturk.com"
TEL = "0532 464 75 19"
MAIL = "gokturk@altinemlak.com.tr"
FOOT_Y = 1300


def F(w, s):
    ad = {"r": "400Regular", "m": "500Medium", "sb": "600SemiBold", "b": "700Bold", "xb": "800ExtraBold", "bl": "900Black"}[w]
    return ImageFont.truetype(os.path.join(KOK, "fonts", f"Montserrat_{ad}.ttf"), s)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def logo(ad, h):
    im = Image.open(os.path.join(KOK, "logo", f"yatay-logo-{ad}-zemin.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def spaced(d, xy, text, font, fill, sp):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + sp
    return x


def spaced_len(d, text, font, sp):
    return sum(d.textlength(c, font=font) + sp for c in text) - sp


# ---------- zengin metin (**kalın**) ----------
def tokens(text):
    out = []
    for i, part in enumerate(re.split(r"\*\*", nfc(text))):
        for w in part.split():
            out.append((w, i % 2 == 1))
    return out


def wrap_rich(d, text, fr, fb, maxw):
    lines, cur, curw = [], [], 0
    sp = d.textlength(" ", font=fr)
    for w, b in tokens(text):
        ww = d.textlength(w, font=fb if b else fr)
        add = ww + (sp if cur else 0)
        if cur and curw + add > maxw:
            lines.append(cur); cur, curw = [], 0; add = ww
        cur.append((w, b)); curw += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich(d, xy, text, fr, fb, fill, fill_b, maxw, lh):
    x0, y = xy
    sp = d.textlength(" ", font=fr)
    for ln in wrap_rich(d, text, fr, fb, maxw):
        x = x0
        for w, b in ln:
            f = fb if b else fr
            d.text((x, y), w, font=f, fill=fill_b if b else fill)
            x += d.textlength(w, font=f) + sp
        y += lh
    return y


def wrap(d, text, font, maxw):
    return [" ".join(w for w, _ in ln) for ln in wrap_rich(d, text.replace("**", ""), font, font, maxw)]


# ---------- ikonlar ----------
def check(d, x, y, r=14, w=3, col=GOLD):
    d.ellipse((x, y, x + 2 * r, y + 2 * r), outline=col, width=w)
    d.line((x + r * .5, y + r * 1.0, x + r * .88, y + r * 1.4, x + r * 1.52, y + r * .62), fill=col, width=w)


def lock(d, cx, cy, s, col):
    d.rounded_rectangle((cx - s, cy - s * .2, cx + s, cy + s * 1.15), radius=s * .22, fill=col)
    d.arc((cx - s * .62, cy - s * 1.15, cx + s * .62, cy + s * .2), 180, 360, fill=col, width=max(3, int(s * .24)))
    d.line((cx - s * .62, cy - s * .48, cx - s * .62, cy - s * .15), fill=col, width=max(3, int(s * .24)))
    d.line((cx + s * .62, cy - s * .48, cx + s * .62, cy - s * .15), fill=col, width=max(3, int(s * .24)))


# ---------- ortak çerçeve ----------
def frame(sayfa, idx, n, ic):
    koyu = sayfa["tip"] == "kapak"
    sari = sayfa["tip"] == "son"
    bg = BG if koyu else GOLD if sari else CREAM
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    kol = GOLD if koyu else INK if sari else GOLD_D
    d.rectangle((M, 101, M + 44, 106), fill=kol)
    spaced(d, (M + 62, 88), f"{ic['seri']} · {ic['etiket']}" if not koyu else ic["seri"], F("b", 22), kol, 4)
    d.text((W - M, 104), f"{idx:02d} / {n:02d}", font=F("sb", 22), fill=GREY if koyu else GREY_D if not sari else INK, anchor="rm")
    # alt bant
    if sari:
        d.rectangle((0, FOOT_Y - 40, W, H), fill=INK)
        lg = logo("koyu", 64)
        img.paste(lg, (M, FOOT_Y + 30 - 6), lg)
        d.text((W - M, FOOT_Y + 62), SITE, font=F("sb", 26), fill=WHITE, anchor="rm")
    else:
        d.line((M, FOOT_Y, W - M, FOOT_Y), fill=LINE_D if koyu else LINE_L, width=2)
        d.rectangle((M, FOOT_Y - 1, M + 120, FOOT_Y + 2), fill=GOLD)
        lg = logo("koyu" if koyu else "acik", 62)
        img.paste(lg, (M, FOOT_Y + 38), lg)
        d.text((W - M, FOOT_Y + 70), SITE, font=F("sb", 24), fill=GREY if koyu else GREY_D, anchor="rm")
    return img, d


def kapak(img, d, s, ic):
    for i in range(7):
        x0 = W - 420 + i * 64
        d.line([(x0, 0), (x0 + 420, 420)], fill=(40, 36, 26), width=3)
    tag = ic["etiket"]
    f = F("xb", 26)
    tw = spaced_len(d, tag, f, 4)
    d.rectangle((M, 330, M + tw + 52, 386), fill=GOLD)
    spaced(d, (M + 26, 342), tag, f, INK, 4)
    y = 432
    for t in (s["ust"], s.get("ust2")):
        if t:
            d.text((M, y), t, font=F("xb", 66), fill=WHITE); y += 78
    y += 18
    big = s["buyuk"]
    for i, t in enumerate(big):
        fs = 240
        while fs > 90 and d.textlength(t, font=F("bl", fs)) > W - 2 * M:
            fs -= 6
        f = F("bl", fs)
        bb = d.textbbox((0, 0), t, font=f)
        d.text((M - bb[0] + 4, y - bb[1]), t, font=f, fill=GOLD)
        y += (bb[3] - bb[1]) + 30
    y += 14
    for ln in wrap(d, s["alt"], F("b", 40), W - 2 * M):
        d.text((M, y), ln, font=F("b", 40), fill=WHITE); y += 52
    y += 26
    d.rectangle((M, y, M + 128, y + 7), fill=GOLD); y += 40
    for ln in wrap(d, s["aciklama"], F("r", 30), W - 2 * M - 60):
        d.text((M, y), ln, font=F("r", 30), fill=(190, 190, 190)); y += 44
    d.text((W - M, FOOT_Y - 52), "KAYDIRIN  →", font=F("b", 24), fill=GOLD, anchor="rm")
    return y


def grafik(img, d, g, y, ymax):
    t = g.get("tip")
    gw = W - 2 * M
    if t == "akis":
        n = len(g["adimlar"]); gap = 56
        bw = (gw - gap * (n - 1)) / n; bh = 210
        for i, a in enumerate(g["adimlar"]):
            x = M + i * (bw + gap)
            mid = i == n // 2
            d.rounded_rectangle((x, y, x + bw, y + bh), radius=18, fill=INK if mid else WHITE, outline=None if mid else LINE_L, width=2)
            if mid:
                lock(d, x + bw / 2, y + 62, 22, GOLD)
            else:
                d.ellipse((x + bw / 2 - 26, y + 34, x + bw / 2 + 26, y + 86), fill=GOLD)
                d.text((x + bw / 2, y + 60), str(i + 1), font=F("xb", 28), fill=INK, anchor="mm")
            yy = y + 112
            for ln in wrap(d, a, F("b", 25), bw - 30):
                d.text((x + bw / 2, yy), ln, font=F("b", 25), fill=WHITE if mid else INK, anchor="ma"); yy += 33
            if i < n - 1:
                ax = x + bw + 10; ay = y + bh / 2
                d.line((ax, ay, ax + gap - 26, ay), fill=GOLD_D, width=5)
                d.polygon([(ax + gap - 28, ay - 11), (ax + gap - 12, ay), (ax + gap - 28, ay + 11)], fill=GOLD_D)
        return y + bh
    if t == "takvim":
        cw, ch = 300, 300
        d.rounded_rectangle((M, y, M + cw, y + ch), radius=22, fill=WHITE, outline=LINE_L, width=2)
        d.rounded_rectangle((M, y, M + cw, y + 84), radius=22, fill=INK)
        d.rectangle((M, y + 60, M + cw, y + 84), fill=INK)
        for k in (0.3, 0.7):
            d.rounded_rectangle((M + cw * k - 7, y - 16, M + cw * k + 7, y + 22), radius=6, fill=GOLD)
        spaced(d, (M + cw / 2 - spaced_len(d, g["ay"], F("xb", 30), 5) / 2, y + 24), g["ay"], F("xb", 30), GOLD, 5)
        d.text((M + cw / 2, y + 84 + (ch - 84) / 2 - 8), g["gun"], font=F("bl", 150), fill=INK, anchor="mm")
        d.text((M + cw / 2, y + ch - 30), g.get("yil", ""), font=F("b", 24), fill=GREY_D, anchor="mm")
        # yanında zaman çizgisi
        tx = M + cw + 70
        pts = g.get("cizgi") or []  # [[tarih, etiket, vurgulu_mu], ...]
        if pts:
            ly0, ly1 = y + 30, y + ch - 30
            d.line((tx, ly0, tx, ly1), fill=LINE_L, width=4)
            for i, (a, b, on) in enumerate(pts):
                yy = ly0 + (ly1 - ly0) * i / max(1, len(pts) - 1)
                d.ellipse((tx - 14, yy - 14, tx + 14, yy + 14), fill=GOLD if on else CREAM, outline=GOLD if on else GREY_D, width=4)
                d.text((tx + 34, yy - 16), a, font=F("xb" if on else "b", 28), fill=INK if on else GREY_D, anchor="ls")
                d.text((tx + 34, yy + 22), b, font=F("m", 22), fill=GOLD_D if on else GREY_D, anchor="ls")
        return y + ch
    if t == "liste":
        x = M
        for it in g["maddeler"]:
            f = F("b", 30)
            w = d.textlength(it, font=f) + 104
            d.rounded_rectangle((x, y, x + w, y + 76), radius=38, fill=WHITE, outline=GOLD, width=3)
            check(d, x + 24, y + 22, r=16, w=4, col=GOLD_D)
            d.text((x + 72, y + 38), it, font=f, fill=INK, anchor="lm")
            x += w + 18
        return y + 76
    if t == "oran":
        parts = g["parcalar"]; bh = 92; x = M
        for i, (a, b, p) in enumerate(parts):
            w = gw * p
            on = i == len(parts) - 1
            d.rectangle((x, y, x + w - (6 if i < len(parts) - 1 else 0), y + bh), fill=GOLD if on else INK)
            d.text((x + 26, y + bh / 2), b.upper(), font=F("xb", 24), fill=INK if on else GOLD, anchor="lm")
            d.text((x, y + bh + 22), a, font=F("b", 27), fill=INK)
            x += w
        d.text((M, y + bh + 70), "Oranlar temsilîdir.", font=F("m", 20), fill=GREY_D)
        return y + bh + 96
    if t == "buyuk":
        r = 92
        d.ellipse((M, y, M + 2 * r, y + 2 * r), fill=INK)
        d.text((M + r, y + r), g["metin"], font=F("bl", 110), fill=GOLD, anchor="mm")
        d.text((M + 2 * r + 36, y + r), g["etiket"], font=F("b", 30), fill=INK, anchor="lm")
        return y + 2 * r
    if t == "tablo":  # {"basliklar": [...4], "satirlar": [[...4]], "vurgu_sutun": 1}
        cols = [gw - 3 * 170] + [170] * 3
        xs = [M]
        for c in cols:
            xs.append(xs[-1] + c)
        hh, rh = 66, 76
        d.rectangle((M, y, W - M, y + hh), fill=INK)
        for j, b in enumerate(g["basliklar"]):
            f = F("xb", 25)
            if j == 0:
                d.text((xs[0] + 22, y + hh / 2), b, font=f, fill=GOLD, anchor="lm")
            else:
                d.text((xs[j] + cols[j] / 2, y + hh / 2), b, font=f, fill=GOLD, anchor="mm")
        y += hh
        vs = g.get("vurgu_sutun", 1)
        for i, row in enumerate(g["satirlar"]):
            d.rectangle((M, y, W - M, y + rh), fill=WHITE if i % 2 == 0 else CREAM)
            for j, c in enumerate(row):
                if j == 0:
                    d.text((xs[0] + 22, y + rh / 2), c, font=F("sb", 27), fill=INK, anchor="lm")
                else:
                    d.text((xs[j] + cols[j] / 2, y + rh / 2), c, font=F("xb", 36), fill=GOLD_D if j == vs else INK, anchor="mm")
            y += rh
        d.line((M, y, W - M, y), fill=GOLD, width=4)
        return y
    if t == "kiyas":  # {"tavan": 5, "birim": "milyon TL", "satirlar": [[etiket, deger, vurgulu_mu], ...]}
        bh, gap = 84, 54
        for a, v, on in g["satirlar"]:
            d.text((M, y), a, font=F("b", 27), fill=GOLD_D if on else GREY_D)
            y += 42
            lbl = f"{v:g} {g['birim']}"
            w = max(d.textlength(lbl, font=F("xb", 34)) + 56, gw * v / g["tavan"])
            d.rectangle((M, y, M + gw, y + bh), fill=WHITE, outline=LINE_L, width=2)
            d.rectangle((M, y, M + w, y + bh), fill=GOLD if on else INK)
            d.text((M + 28, y + bh / 2), lbl, font=F("xb", 34), fill=INK if on else GOLD, anchor="lm")
            y += bh + gap
        return y - gap
    if t == "kontrol":
        items = g["maddeler"]
        step = min(190, (ymax - y) / len(items))
        for a, b in items:
            d.line((M, y, W - M, y), fill=LINE_L, width=2)
            check(d, M, y + 40, r=17, w=4, col=GOLD_D)
            d.text((M + 60, y + 34), a, font=F("b", 36), fill=INK)
            yy = y + 88
            for ln in wrap(d, b, F("r", 28), gw - 60):
                d.text((M + 60, yy), ln, font=F("r", 28), fill=GREY_D); yy += 38
            y += step
        d.line((M, y, W - M, y), fill=LINE_L, width=2)
        return y
    return y


def madde(img, d, s, ic, y0=None):
    if y0 is None:  # önce ölç, sonra içeriği dikeyde ortala
        tmp = Image.new("RGB", (W, H), CREAM)
        end = madde(tmp, ImageDraw.Draw(tmp), s, ic, 0)
        top, bot = 175, FOOT_Y - 70
        y0 = top + max(0, (bot - top - end) * 0.42)
    nf = F("bl", 150)
    bb = d.textbbox((0, 0), s["no"], font=nf)
    d.text((M - bb[0], y0 - bb[1]), s["no"], font=nf, fill=GOLD_D)
    y = y0 + (bb[3] - bb[1]) + 34
    d.rectangle((M, y, M + 128, y + 7), fill=GOLD); y += 36
    if s.get("vurgu"):
        d.text((M, y), s["vurgu"], font=F("b", 30), fill=GOLD_D); y += 50
    for ln in wrap(d, s["baslik"], F("xb", 56), W - 2 * M):
        d.text((M, y), ln, font=F("xb", 56), fill=INK); y += 66
    y += 22
    if s.get("metin"):
        y = draw_rich(d, (M, y), s["metin"], F("r", 31), F("b", 31), INK, INK, W - 2 * M, 45) + 14
    g = s.get("grafik")
    not_h = 0
    if s.get("not"):
        not_lines = wrap(d, s["not"], F("m", 25), W - 2 * M - 30)
        not_h = len(not_lines) * 36 + 30
    if g:
        gy = y + 34
        y = grafik(img, d, g, gy, gy + 600 if g.get("tip") == "kontrol" else FOOT_Y)
    if s.get("not"):
        ny = y + 46
        d.rectangle((M, ny, M + 5, ny + len(not_lines) * 36 - 6), fill=GOLD)
        for i, ln in enumerate(not_lines):
            d.text((M + 28, ny + i * 36), ln, font=F("m", 25), fill=GREY_D)
        y = ny + len(not_lines) * 36
    return y


def son(img, d, s, ic):
    y = 230
    for t in s["baslik"]:
        d.text((M, y), t, font=F("xb", 70), fill=INK); y += 84
    y += 30
    for ln in wrap(d, s["metin"], F("m", 32), W - 2 * M):
        d.text((M, y), ln, font=F("m", 32), fill=INK); y += 46
    y += 56
    d.rectangle((M, y, W - M, y + 250), fill=INK)
    spaced(d, (M + 44, y + 40), "BİZE ULAŞIN", F("xb", 22), GOLD, 4)
    d.text((M + 44, y + 80), TEL, font=F("xb", 62), fill=WHITE)
    d.text((M + 44, y + 170), MAIL, font=F("m", 28), fill=(200, 200, 200))
    y += 300
    if s.get("kaynak"):
        for ln in wrap(d, s["kaynak"], F("m", 22), W - 2 * M):
            d.text((M, y), ln, font=F("m", 22), fill=(92, 66, 12)); y += 32
    return y


def sayfa_ciz(s, idx, n, ic):
    img, d = frame(s, idx, n, ic)
    y = {"kapak": kapak, "madde": madde, "son": son}[s["tip"]](img, d, s, ic)
    if y > FOOT_Y - 20:
        print(f"UYARI: sayfa {idx} taşıyor (y={int(y)})", file=sys.stderr)
    return img


def story(cover):
    st = Image.new("RGB", (1080, 1920), BG)
    sc = cover.resize((int(W * 0.86), int(H * 0.86)), Image.LANCZOS)
    x = (1080 - sc.width) // 2
    y = 300
    d = ImageDraw.Draw(st)
    spaced(d, (x, 200), "YENİ GÖNDERİ", F("xb", 30), GOLD, 6)
    d.rectangle((x - 6, y - 6, x + sc.width + 6, y + sc.height + 6), fill=GOLD)
    st.paste(sc, (x, y))
    d.text((540, y + sc.height + 90), "Tamamını okumak için gönderiye dokunun", font=F("sb", 30), fill=WHITE, anchor="mm")
    return st


def reels(pages, out, ic):
    """Sayfaları 9:16 sahnelere çevirir: üst/alt boşluk zeminle uzatılır, sahne geçişi + hafif yakınlaşma."""
    FPS = 30
    dur = {"kapak": 3.5, "madde": 5.0, "son": 4.0}
    frames = []
    for s, im in pages:
        bgc = im.getpixel((5, 5))
        c = Image.new("RGB", (1080, 1920), bgc)
        c.paste(im, (0, 210))
        if s["tip"] == "son":
            ImageDraw.Draw(c).rectangle((0, 210 + FOOT_Y - 40, 1080, 1920), fill=INK)
            c.paste(im.crop((0, FOOT_Y - 40, W, H)), (0, 210 + FOOT_Y - 40))
        frames.append((dur[s["tip"]], c))
    XF = 0.45
    total = sum(t for t, _ in frames) - XF * (len(frames) - 1)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                           "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264",
                           "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    starts, t0 = [], 0.0
    for t, _ in frames:
        starts.append(t0); t0 += t - XF

    def at(i, tt):
        t, c = frames[i]
        z = 1.0 + 0.035 * max(0, min(1, tt / t))
        if z > 1.0:
            cw, ch = 1080 / z, 1920 / z
            c = c.resize((1080, 1920), Image.BICUBIC, box=((1080 - cw) / 2, (1920 - ch) / 2, (1080 + cw) / 2, (1920 + ch) / 2))
        return c

    for k in range(int(total * FPS)):
        t = k / FPS
        act = [i for i, s0 in enumerate(starts) if s0 <= t < s0 + frames[i][0]]
        fr = at(act[0], t - starts[act[0]])
        if len(act) > 1:
            j = act[1]
            fr = Image.blend(fr, at(j, t - starts[j]), max(0, min(1, (t - starts[j]) / XF)))
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    return total


def main():
    ic = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(f"{out}/post", exist_ok=True); os.makedirs(f"{out}/instagram_jpg", exist_ok=True)
    sp = ic["sayfalar"]; n = len(sp)
    if n > 10:
        sys.exit("Carousel en fazla 10 sayfa olabilir")
    pages = []
    for i, s in enumerate(sp, 1):
        im = sayfa_ciz(s, i, n, ic)
        im.save(f"{out}/post/{i:02d}.png", optimize=True)
        im.save(f"{out}/instagram_jpg/{i:02d}.jpg", quality=92)
        pages.append((s, im))
    st = story(pages[0][1])
    st.save(f"{out}/story.png", optimize=True)
    st.save(f"{out}/instagram_jpg/story.jpg", quality=92)
    acik = ic["aciklama"]
    if len(acik) > 2200:
        print(f"UYARI: açıklama {len(acik)} karakter (sınır 2200)", file=sys.stderr)
    open(f"{out}/aciklama.txt", "w", encoding="utf-8").write(acik)
    if "--reels" in sys.argv or ic.get("format") == "reels":
        sure = reels(pages, f"{out}/reels.mp4", ic)
        print(f"reels: {sure:.1f} sn")
    print("ok", n, "sayfa")


if __name__ == "__main__":
    main()
