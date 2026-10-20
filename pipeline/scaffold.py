#!/usr/bin/env python3
"""
Generate a starting build.json for every ingested product.

The point is to kill the blank page. Each scaffold already knows the product,
its article number, its dimensions, every manual page and which pages look like
build pages - so authoring starts at "correct these 12 pages", not "open an 88
page PDF and find out".

Usage: python3 scaffold.py [--force]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def parse_dims(text: str | None) -> dict:
    """IKEA prints Width x Depth x Height. Take what is unambiguous."""
    out = {"unit": "cm", "text": text}
    if not text:
        return out
    nums = re.findall(r"\d+(?:[.,]\d+)?", text)
    if "/" in text or len(nums) not in (2, 3):
        return out
    vals = [float(n.replace(",", ".")) for n in nums]
    if len(vals) == 3:
        out["w"], out["d"], out["h"] = vals
    elif len(vals) == 2:
        out["w"], out["d"] = vals
    return out


def main() -> int:
    force = "--force" in sys.argv
    # dims/image from the ranked product list, keyed by product url
    enrich = {}
    top = os.path.join(ROOT, "data", "top30.json")
    if os.path.exists(top):
        for r in json.load(open(top, encoding="utf-8")):
            enrich[r["url"]] = r

    made = []
    for mf in sorted(glob.glob(os.path.join(ROOT, "products", "*", "meta.json"))):
        pdir = os.path.dirname(mf)
        slug = os.path.basename(pdir)
        out = os.path.join(pdir, "build.json")
        if os.path.exists(out) and not force:
            continue
        m = json.load(open(mf, encoding="utf-8"))
        pj = os.path.join(pdir, "pages.json")
        pages = json.load(open(pj, encoding="utf-8"))["pages"] if os.path.exists(pj) else []
        build_pages = json.load(open(pj, encoding="utf-8"))["build_pages"] if os.path.exists(pj) else []

        extra = enrich.get(m.get("url"), {})
        dims = parse_dims(extra.get("dims") or m.get("dims"))

        doc = {
            "id": slug,
            "version": 1,
            "status": "scaffold",
            "units": "cm",
            "product": {
                "name": m.get("name") or extra.get("name"),
                "typeName": m.get("typeName") or extra.get("typeName"),
                "article": (m.get("article") or [None])[0],
                "dims": dims,
                "url": m.get("url"),
                "pdfUrl": m.get("pdf_url"),
                "image": extra.get("image") or m.get("image"),
                "reviews": extra.get("reviews"),
                "rating": extra.get("rating"),
                "copyrightYear": m.get("copyright_year"),
            },
            "manual": {
                "dir": "manual",
                "dpi": 150,
                "pages": [
                    {"page": p["page"], "file": p["file"], "w": p["w"], "h": p["h"],
                     "kind": p.get("kind")}
                    for p in pages
                ],
                "buildPages": build_pages,
            },
            "parts": [],
            "hardware": [],
            "steps": [
                {
                    "title": f"Page {n}",
                    "page": n,
                    "box": None,
                    "duration": 4,
                    "cam": None,
                    "prose": "",
                }
                for n in build_pages
            ],
            "tags": [],
            "notes": "",
        }
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        made.append((doc["product"]["name"], dims.get("text"), len(build_pages)))

    for n, d, k in made:
        print(f"  scaffolded {str(n)[:22]:<22} {str(d)[:18]:<18} {k:>3} build pages")
    print(f"\n{len(made)} build.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
