#!/usr/bin/env python3
"""
Rebuild data/catalogue.json from the build.json files - the source of truth
once anything has been authored. Also prints the authoring queue, cheapest first.

    python3 catalogue.py
"""
from __future__ import annotations

import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main() -> None:
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "products", "*", "build.json"))):
        d = json.load(open(f, encoding="utf-8"))
        p = d.get("product") or {}
        man = d.get("manual") or {}
        steps = d.get("steps") or []
        rows.append({
            "id": d.get("id"),
            "name": p.get("name"),
            "typeName": p.get("typeName"),
            "dims": (p.get("dims") or {}).get("text"),
            "article": p.get("article"),
            "url": p.get("url"),
            "pdfUrl": p.get("pdfUrl"),
            "status": d.get("status"),
            "page_count": len(man.get("pages") or []),
            "build_pages": man.get("buildPages") or [],
            "n_build_pages": len(man.get("buildPages") or []),
            "steps": len(steps),
            "steps_complete": sum(1 for s in steps
                              if s.get("box") and s.get("cam")
                              and s.get("boxSource") != "auto"
                              and s.get("camSource") != "auto"),
            "parts": len(d.get("parts") or []),
            "hardware": sum(h.get("count") or 0 for h in (d.get("hardware") or [])),
        })

    rows.sort(key=lambda r: r["n_build_pages"])
    out = {
        "market": "nl/nl",
        "products": len(rows),
        "pdf_pages": sum(r["page_count"] for r in rows),
        "build_pages": sum(r["n_build_pages"] for r in rows),
        "steps": sum(r["steps"] for r in rows),
        "steps_complete": sum(r["steps_complete"] for r in rows),
        "per_product": rows,
    }
    with open(os.path.join(ROOT, "data", "catalogue.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(f"{out['products']} products | {out['pdf_pages']} pdf pages | "
          f"{out['build_pages']} build pages | {out['steps']} steps "
          f"({out['steps_complete']} fully authored)")
    print()
    print("authoring queue, cheapest first:")
    print(f"  {'#':>3}  {'product':<34}{'type':<26}{'dims':<18}{'pages':>6}{'steps':>7}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>3}  {(r['name'] or '?')[:34]:<34}{(r['typeName'] or '')[:26]:<26}"
              f"{(r['dims'] or '—')[:18]:<18}{r['n_build_pages']:>6}{r['steps']:>7}")


if __name__ == "__main__":
    main()
