#!/usr/bin/env python3
"""
Classify the pages of every ingested manual: cover / warnings / illustration / backmatter.

IKEA manuals spend pages 2-5 on the tip-over warning in ~25 languages, and the
last few pages on recycling/copyright notices. Only the illustration pages carry
the build. Telling the author which pages those are (and how complex each one is)
is the difference between opening 88 PDFs and opening 12.

Heuristic, validated against BILLY (AA-1823127-9):
  illustration -> many vector paths, almost no text
  warnings     -> almost no vector paths, thousands of text chars

Writes products/<slug>/pages.json and prints a ranked workload table.
"""
from __future__ import annotations

import glob
import json
import os

VEC_MIN = 120          # vector paths: below this it is prose, not a drawing
CHARS_MAX = 600        # text chars: above this it is a warnings/language page
DENSITY_MIN = 0.02     # fraction of page area covered by drawing ink


def classify(p: dict) -> str:
    v, c = p["vectors"], p["chars"]
    if v < 30 and c < 200:
        return "backmatter"
    if c > CHARS_MAX and v < VEC_MIN:
        return "warnings"
    if v >= VEC_MIN and c <= CHARS_MAX:
        return "illustration"
    if v >= VEC_MIN and c > CHARS_MAX:
        return "mixed"
    return "cover" if p["page"] == 1 else "other"


def main() -> None:
    root = os.path.join(os.path.dirname(__file__), "..", "products")
    rows = []
    for mf in sorted(glob.glob(os.path.join(root, "*", "meta.json"))):
        m = json.load(open(mf, encoding="utf-8"))
        pages = m.get("pages", [])
        for p in pages:
            p["kind"] = classify(p)
        ill = [p for p in pages if p["kind"] == "illustration"]
        mixed = [p for p in pages if p["kind"] == "mixed"]
        build_pages = [p["page"] for p in ill + mixed]

        out = {
            "slug": m.get("slug"),
            "name": m.get("name"),
            "typeName": m.get("typeName"),
            "dims": m.get("dims"),
            "article": m.get("article"),
            "copyright_year": m.get("copyright_year"),
            "pdf_url": m.get("pdf_url"),
            "url": m.get("url"),
            "page_count": m.get("page_count"),
            "build_pages": build_pages,
            "n_build_pages": len(build_pages),
            "pages": pages,
        }
        with open(os.path.join(os.path.dirname(mf), "pages.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

        rows.append(out)

    rows.sort(key=lambda r: -r["n_build_pages"])
    print(f"{'product':<14}{'type':<26}{'dims':<17}{'pdf':>4}{'build':>7}  pages")
    tot = 0
    for r in rows:
        tot += r["n_build_pages"]
        print(f"{(r['name'] or '?')[:14]:<14}{(r['typeName'] or '')[:26]:<26}"
              f"{(r['dims'] or '?')[:17]:<17}{r['page_count']:>4}"
              f"{r['n_build_pages']:>7}  {r['build_pages'][:14]}")
    print(f"\n{len(rows)} products | {sum(r['page_count'] for r in rows)} pdf pages | "
          f"{tot} build pages -> {tot/len(rows):.1f} build pages/product")

    summary = {
        "products": len(rows),
        "pdf_pages": sum(r["page_count"] for r in rows),
        "build_pages": tot,
        "per_product": [
            {"slug": r["slug"], "name": r["name"], "typeName": r["typeName"],
             "dims": r["dims"], "article": r["article"], "url": r["url"],
             "pdf_url": r["pdf_url"], "page_count": r["page_count"],
             "build_pages": r["build_pages"], "n_build_pages": r["n_build_pages"]}
            for r in rows
        ],
    }
    sp = os.path.join(os.path.dirname(__file__), "..", "data", "catalogue.json")
    os.makedirs(os.path.dirname(os.path.abspath(sp)), exist_ok=True)
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"wrote data/catalogue.json")


if __name__ == "__main__":
    main()
