#!/usr/bin/env python3
"""altinemlakgokturk.com ilanlarını tarar (Composio çalışma alanında / internete erişimi olan ortamda).

Kullanım (Python):  from site_tara import ilanlar;  veri = ilanlar()
Komut satırı:       python3 site_tara.py > ilanlar.json
Her ilan: url, no, og_title, konum, durum, tip, fiyat, oda, net, brut, kat, kullanim,
          danisman, danisman_link, foto_url, aciklama (ilk 1500 karakter)
Bilgi uydurmaz; alan sitede yoksa None döner.
"""
import html, json, re, sys
import urllib.request

SITE = "https://www.altinemlakgokturk.com"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AltinEmlakBulten/1.0", "Cache-Control": "no-cache"}


def al(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def metin(h):
    """HTML'i satır yapısını koruyarak düz metne çevirir."""
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(div|p|li|tr|h\d|span|label|td|th|section|ul|dt|dd)>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    satirlar = [re.sub(r"[ \t\xa0]+", " ", s).strip() for s in h.split("\n")]
    return "\n".join(s for s in satirlar if s)


def deger(t, etiket):
    m = re.search(re.escape(etiket) + r"\s*\n\s*([^\n]+)", t)
    return m.group(1).strip() if m else None


def ilan_linkleri():
    linkler = []
    for sayfa in range(1, 30):
        h = al(f"{SITE}/tr/ilanlar?pageSize=10&pageIndex={sayfa}")
        yeni = [l.split("?")[0] for l in re.findall(r'href="(/tr/ilan/[^"]+)"', h)]
        once = len(linkler)
        for l in yeni:
            if l not in linkler:
                linkler.append(l)
        if len(linkler) == once:
            break
    return linkler


def ilan(yol):
    h = al(SITE + yol)
    t = metin(h)
    og = re.search(r'property="og:title"\s+content="([^"]*)"', h) or re.search(r'content="([^"]*)"\s+property="og:title"', h)
    dan = re.search(r'href="(/tr/danisman/[^"]*)"[^>]*>\s*([^<]*)<', h)
    foto = re.search(r'(https://cdnc\.re-os\.com/property/[0-9a-f-]{36}\.\w+)', h)
    ac = t.split("Detaylı Açıklama", 1)[1].split("Harita Konumu", 1)[0].strip() if "Detaylı Açıklama" in t else ""
    return {
        "url": SITE + yol, "no": int(re.search(r"(\d+)$", yol).group(1)),
        "og_title": html.unescape(og.group(1)) if og else None,
        "konum": deger(t, "İl/İlçe/Mahalle"), "durum": deger(t, "Gayrimenkul Durumu:"),
        "tip": deger(t, "Portföy Tipi:"), "fiyat": deger(t, "Fiyat:"), "oda": deger(t, "Oda:"),
        "net": deger(t, "Net Alan"), "brut": deger(t, "Brüt Alan"), "kat": deger(t, "Bulunduğu Kat:"),
        "kullanim": deger(t, "Kullanım Durumu:"),
        "danisman": (dan.group(2).strip() or None) if dan else None,
        "danisman_link": dan.group(1) if dan else None,
        "foto_url": foto.group(1) if foto else None,
        "aciklama": ac[:1500],
    }


def ilanlar():
    return [ilan(l) for l in ilan_linkleri()]


def foto_indir(url, hedef, genislik=1100):
    """İlan fotoğrafını indirip ≤1100 px JPEG olarak kaydeder."""
    from io import BytesIO
    from PIL import Image
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        im = Image.open(BytesIO(r.read())).convert("RGB")
    im.thumbnail((genislik, genislik * 3))
    im.save(hedef, quality=82)


if __name__ == "__main__":
    json.dump(ilanlar(), sys.stdout, ensure_ascii=False, indent=1)
