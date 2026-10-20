#!/usr/bin/env python3
"""
IKEA flat-pack manual ingest pipeline.

For each product:
  name -> search API -> canonical product URL + article id
       -> product page HTML -> assembly_instructions PDF url + JSON-LD (dims, 3D GLB)
       -> download PDF
       -> rasterise every page to WebP (default 150 DPI, A4 = 1241x1754)

Writes:
  products/<slug>/meta.json
  products/<slug>/manual/pNN.webp

Usage:
  python3 ikea.py billy                    # single product, search by name
  python3 ikea.py --url <product-page-url>  # skip search
  python3 ikea.py --file list.txt           # one name or url per line
  python3 ikea.py --file list.txt --dpi 200 --glb

Polite by default: 1.5s between network requests, retries with backoff.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.parse

import requests
import pymupdf
from PIL import Image

MARKET = os.environ.get("IKEA_MARKET", "nl/nl")
LANG = os.environ.get("IKEA_LANG", "nl-NL,nl;q=0.9")
BASE = "https://www.ikea.com"
SEARCH_API = f"https://sik.search.blue.cdtapps.com/{MARKET}/search-result-page"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": UA,
    "Accept-Language": LANG,
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
})

DELAY = 1.5
_last = [0.0]


def polite_get(url: str, tries: int = 3, **kw):
    """GET with a floor on request rate and simple exponential backoff."""
    wait = DELAY
    last_exc = None
    for attempt in range(tries):
        gap = DELAY - (time.monotonic() - _last[0])
        if gap > 0:
            time.sleep(gap)
        try:
            r = SESSION.get(url, timeout=60, **kw)
            _last[0] = time.monotonic()
            if r.status_code == 200:
                return r
            last_exc = RuntimeError(f"HTTP {r.status_code}")
        except Exception as e:  # noqa: BLE001
            _last[0] = time.monotonic()
            last_exc = e
        time.sleep(wait)
        wait *= 2
    raise last_exc


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------- resolve

def search(name: str, size: int = 8) -> list[dict]:
    """Resolve a product name to candidate products via IKEA's search API."""
    url = f"{SEARCH_API}?types=PRODUCT&q={urllib.parse.quote(name)}&size={size}"
    r = polite_get(url, headers={"Accept": "application/json"})
    body = r.json().get("searchResultPage", {})
    items = body.get("products", {}).get("main", {}).get("items", [])
    out = []
    for it in items:
        p = it.get("product") or {}
        if not p.get("pipUrl"):
            continue
        out.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "typeName": p.get("typeName"),
            "url": p.get("pipUrl"),
            "dims": p.get("itemMeasureReferenceText"),
            "filterClass": p.get("filterClass"),
            "badge": (p.get("badge") or {}).get("type"),
            "category": "/".join(
                c.get("name", "") for c in (p.get("categoryPath") or [])
            ),
            "image": p.get("mainImageUrl"),
            "rating": p.get("ratingValue"),
            "reviews": p.get("ratingCount"),
            "price": (p.get("salesPrice") or {}).get("numeral"),
        })
    return out


def pick_best(cands: list[dict], want: str) -> dict | None:
    """Prefer an exact name match, else the most-reviewed real product."""
    if not cands:
        return None
    key = want.lower().split()[0]
    exact = [c for c in cands if (c["name"] or "").lower() == key]
    if exact:
        return max(exact, key=lambda c: (c["reviews"] or 0))
    named = [c for c in cands if (c["name"] or "").lower().startswith(key)]
    if named:
        return max(named, key=lambda c: (c["reviews"] or 0))
    return max(cands, key=lambda c: (c["reviews"] or 0))


# ---------------------------------------------------------------- parse

def extract_assembly_pdf(html: str) -> str | None:
    """The canonical assembly instructions PDF linked from the product page."""
    pat = rf"https://www\.ikea\.com/{re.escape(MARKET)}/assembly_instructions/[^\"'\\ ]+?\.pdf"
    hits = re.findall(pat, html)
    if hits:
        # de-dup, prefer lowest -N suffix (the primary/100 variant)
        uniq = sorted(set(hits), key=lambda u: (len(u), u))
        return uniq[0]
    return None


def extract_ld(html: str) -> dict:
    """Pull Product + 3DModel JSON-LD blocks."""
    out = {"product": None, "models": []}
    for m in re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    ):
        try:
            d = json.loads(m.group(1))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        t = d.get("@type")
        if t == "Product" and out["product"] is None:
            out["product"] = d
        elif t == "3DModel":
            out["models"] = [
                e.get("contentUrl") for e in d.get("encoding", [])
                if (e.get("encodingFormat") or "").startswith("model/gltf-binary")
            ]
    return out


def summarise_product(ld: dict) -> dict:
    p = ld.get("product") or {}
    dims = {}
    for k, src in (("width", "width"), ("height", "height"), ("depth", "depth")):
        v = p.get(src)
        if isinstance(v, str):
            dims[k] = v
        elif isinstance(v, dict):
            dims[k] = v.get("value")
    return {
        "name": p.get("name"),
        "color": p.get("color"),
        "category": p.get("category"),
        "description": (p.get("description") or "")[:400],
        "dimensions": dims,
        "rating": (p.get("aggregateRating") or {}).get("ratingValue"),
        "reviews": (p.get("aggregateRating") or {}).get("reviewCount"),
    }


# ---------------------------------------------------------------- rasterise

def rasterise(pdf_bytes: bytes, outdir: str, dpi: int = 150, quality: int = 88) -> dict:
    """Render every PDF page to WebP. Returns page list + detected metadata."""
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text_all = []
    pages = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        fn = f"p{i:02d}.webp"
        path = os.path.join(outdir, fn)
        img.save(path, "WEBP", quality=quality, method=5)
        txt = page.get_text()
        text_all.append(txt)
        pages.append({
            "page": i,
            "file": fn,
            "w": pix.width,
            "h": pix.height,
            "chars": len(txt.strip()),
            "vectors": len(page.get_drawings()),
        })
    meta = doc.metadata or {}
    blob = "\n".join(text_all)
    art = re.findall(r"AA-\d+-\d+", blob)
    year = re.findall(r"©\s*Inter IKEA Systems B\.V\.\s*(\d{4})", blob)
    doc.close()
    return {
        "page_count": len(pages),
        "pages": pages,
        "article": sorted(set(art)),
        "copyright_year": year[0] if year else None,
        "pdf_title": meta.get("title"),
        "pdf_created": (meta.get("creationDate") or "").replace("D:", "")[:8],
    }


# ---------------------------------------------------------------- driver

def process(query: str, root: str, dpi: int, want_glb: bool) -> dict:
    query = query.strip()
    if not query or query.startswith("#"):
        return {"query": query, "status": "skipped"}

    rec: dict = {"query": query}

    if query.startswith("http"):
        url = query
        rec["resolved_by"] = "url"
    else:
        cands = search(query)
        best = pick_best(cands, query)
        if not best:
            rec["status"] = "error"
            rec["error"] = "no search results"
            return rec
        url = best["url"]
        rec.update({k: best[k] for k in (
            "id", "name", "typeName", "dims", "filterClass", "badge",
            "category", "image", "rating", "reviews", "price",
        )})
        rec["resolved_by"] = "search"
        rec["candidates"] = len(cands)
    rec["url"] = url

    html = polite_get(url).text
    pdf_url = extract_assembly_pdf(html)
    if not pdf_url:
        rec["status"] = "error"
        rec["error"] = "no assembly PDF on product page"
        return rec
    rec["pdf_url"] = pdf_url

    ld = extract_ld(html)
    rec.update(summarise_product(ld))
    rec["glb"] = (ld["models"][0] if ld["models"] else None)

    slug = slugify(re.search(r"/p/([^/?#]+)", url).group(1))
    pdir = os.path.join(root, slug)
    mdir = os.path.join(pdir, "manual")
    os.makedirs(pdir, exist_ok=True)

    pdf = polite_get(pdf_url).content
    if not pdf.startswith(b"%PDF"):
        rec["status"] = "error"
        rec["error"] = "download was not a PDF (blocked?)"
        return rec
    rec["pdf_bytes"] = len(pdf)

    rec.update(rasterise(pdf, mdir, dpi=dpi))
    rec["slug"] = slug

    if want_glb and rec.get("glb"):
        try:
            g = polite_get(rec["glb"]).content
            if g[:4] == b"glTF":
                with open(os.path.join(pdir, "model.glb"), "wb") as f:
                    f.write(g)
                rec["glb_bytes"] = len(g)
        except Exception as e:  # noqa: BLE001
            rec["glb_error"] = str(e)

    with open(os.path.join(pdir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)

    rec["status"] = "ok"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "products"))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--glb", action="store_true", help="also download the official IKEA GLB")
    ap.add_argument("--out", default=None, help="write a combined catalogue json here")
    a = ap.parse_args()

    queries = list(a.names)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            queries += [ln.strip() for ln in f if ln.strip()]
    if not queries:
        ap.error("give names or --file")

    root = os.path.abspath(a.root)
    os.makedirs(root, exist_ok=True)

    results = []
    for q in queries:
        try:
            r = process(q, root, a.dpi, a.glb)
        except Exception as e:  # noqa: BLE001
            r = {"query": q, "status": "error", "error": repr(e)}
        results.append(r)
        if r["status"] == "ok":
            print(f"  ok   {r['query']:<28} {r.get('name',''):<12} "
                  f"{r.get('typeName','')[:26]:<26} {r['page_count']:>2}p  "
                  f"art={','.join(r.get('article') or []) or '-'}")
        else:
            print(f"  FAIL {r['query']:<28} {r.get('error')}")

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nwrote {a.out}")

    ok = [r for r in results if r["status"] == "ok"]
    print(f"\n{len(ok)}/{len(results)} ok")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
