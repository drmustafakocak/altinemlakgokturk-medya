#!/usr/bin/env python3
"""Bülteni Composio çalışma alanında (bulut) üretir ve görselleri Instagram için yükler.

Çalışma alanında:
    import urllib.request; exec(urllib.request.urlopen(
        "https://raw.githubusercontent.com/drmustafakocak/altinemlakgokturk-medya/<HASH>/portfoy/_sablon/bulut_uret.py").read())
    sonuc = bulut_uret("<HASH>")      # upload_local_file çalışma alanında hazır gelir
Dönen sözlük: {"satilik": [{"dosya","s3key","s3_url"}...], "kiralik": [...], "aciklama": {...}, "secim": {...}}
Not: <HASH>, portfoy_veri.json'un güncel hâlinin push edildiği commit olmalı.
"""
import io, json, os, shutil, subprocess, sys, tarfile, urllib.request

DEPO = "drmustafakocak/altinemlakgokturk-medya"


def bulut_uret(hash_, kok="/home/user/bulten"):
    shutil.rmtree(kok, ignore_errors=True)
    os.makedirs(kok)
    veri = urllib.request.urlopen(f"https://codeload.github.com/{DEPO}/tar.gz/{hash_}", timeout=120).read()
    with tarfile.open(fileobj=io.BytesIO(veri)) as tf:
        uyeler = [m for m in tf.getmembers() if "/portfoy/_sablon/" in m.name]
        for m in uyeler:
            m.name = m.name.split("/portfoy/_sablon/", 1)[1]
        tf.extractall(kok, members=[m for m in uyeler if m.name])
    sys.path.insert(0, kok)
    from site_tara import foto_indir
    pv = json.load(open(os.path.join(kok, "portfoy_veri.json"), encoding="utf-8"))
    os.makedirs(os.path.join(kok, "foto"), exist_ok=True)
    for p in pv["portfoyler"]:
        yol = os.path.join(kok, "foto", p["foto"])
        if not os.path.exists(yol):
            if not p.get("foto_url"):
                raise SystemExit(f"{p['no']}: foto yok ve foto_url boş")
            foto_indir(p["foto_url"], yol)
    out = os.path.join(kok, "out")
    r = subprocess.run([sys.executable, os.path.join(kok, "portfoy_bulten.py"), out], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)
    print(r.stdout)
    b = os.path.join(out, f"Portföy Bülteni {pv['bulten_tarihi']}")
    sonuc = {"secim": json.load(open(os.path.join(b, "secim.json"))), "aciklama": {}}
    for seri in ("satilik", "kiralik"):
        k = os.path.join(b, seri)
        if not os.path.isdir(k):
            continue
        sonuc["aciklama"][seri] = open(os.path.join(k, "aciklama.txt"), encoding="utf-8").read()
        liste = []
        for f in sorted(os.listdir(os.path.join(k, "instagram_jpg"))):
            res, err = upload_local_file(os.path.join(k, "instagram_jpg", f))  # noqa: F821 (çalışma alanı yardımcısı)
            if err:
                raise SystemExit(f"yükleme hatası {f}: {err}")
            d = res.get("data", res) if isinstance(res, dict) else res
            liste.append({"dosya": f, "s3key": d["s3key"], "s3_url": d["s3_url"]})
        sonuc[seri] = liste
    return sonuc
