#!/usr/bin/env python3
"""
Build a *real* "top selling flat-pack IKEA products" list.

ikea.com's own "best sellers" page is dominated by accessories (hooks, pans,
hangers, mugs) that have no assembly manual at all. The search API, however,
tags products with an explicit badge: {"type": "TOP_SELLER"}.

So: sweep furniture category queries, keep TOP_SELLER items whose filterClass
is an assemblable furniture class, de-duplicate by product family (BILLY comes
in 12 colours), and rank by review count.

Usage:
  python3 discover.py --out ../data/discovered.json
"""
from __future__ import annotations

import argparse
import json
import os
import time

from ikea import search, MARKET

# Category sweeps (Dutch). Broad enough to surface the whole furniture range.
QUERIES = [
    "boekenkast", "kast", "schappenwand", "ladekast", "dressoir", "vitrinekast",
    "tv-meubel", "opbergcombinatie", "wandplank", "nachtkastje", "commode",
    "bureau", "computerbureau", "bureaustoel", "eettafel", "salontafel",
    "bijzettafel", "klaptafel", "stoel", "fauteuil", "bank", "tweezitsbank",
    "hoekbank", "slaapbank", "bed", "bedframe", "ledikant", "hoogslaper",
    "kinderbed", "kinderstoel", "kindertafel", "kledingkast", "garderobekast",
    "schoenenkast", "spiegelkast", "badkamermeubel", "keukenkastje", "kar",
    "krukje", "bankje", "buitenstoel", "tuintafel", "ligstoel", "plantenrek",
]

# filterClass values that mean "this ships flat and needs assembling".
ASSEMBLY_CLASSES = {
    "bookcases and display cabinets", "shelving units", "cabinets",
    "chest of drawers", "chests of drawers", "drawer units", "wardrobes",
    "open wardrobes", "sideboards", "tv units", "tv benches",
    "storage combinations", "modular storage", "wall shelves",
    "desks", "computer desks", "desk chairs", "office chairs",
    "dining tables", "coffee tables", "side tables", "tables",
    "gateleg tables", "bar tables", "chairs", "armchairs", "easy chairs",
    "sofas", "two-seat sofas", "corner sofas", "sofa beds", "benches",
    "beds", "bed frames", "day beds", "cots", "children's beds",
    "highchairs", "children's chairs", "children's tables", "children's storage",
    "stools", "shoe cabinets", "mirror cabinets", "bathroom furniture",
    "kitchen cabinets", "trolleys", "room dividers", "nursery furniture",
    "chests", "dressing tables", "bookcases", "display cabinets",
}

# Classes that are accessories / soft goods / not flat-pack.
EXCLUDE_CLASSES = {
    "mugs", "glasses", "plates", "bowls", "cutlery", "pots and pans",
    "kitchen utensils", "textiles", "cushions", "rugs", "lighting",
    "lamps", "candles", "vases", "plants", "storage boxes", "bags",
    "hooks", "hangers", "towels", "bedding", "duvet covers", "mattresses",
    "mirrors", "wall art", "frames", "batteries", "food",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(__file__), "..", "data", "discovered.json"))
    ap.add_argument("--raw", default=None, help="dump every product seen")
    ap.add_argument("--size", type=int, default=24)
    a = ap.parse_args()

    seen: dict[str, dict] = {}
    classes: dict[str, int] = {}
    badge_counts: dict[str, int] = {}

    for q in QUERIES:
        try:
            cands = search(q, size=a.size)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {q}: {e}")
            continue
        n_new = 0
        for c in cands:
            fc = (c["filterClass"] or "").strip().lower()
            if fc:
                classes[fc] = classes.get(fc, 0) + 1
            b = c["badge"] or "none"
            badge_counts[b] = badge_counts.get(b, 0) + 1
            key = c["id"]
            if key not in seen:
                c["queries"] = [q]
                seen[key] = c
                n_new += 1
            elif q not in seen[key]["queries"]:
                seen[key]["queries"].append(q)
        print(f"  {q:<20} {len(cands):>3} hits, {n_new} new")

    products = list(seen.values())

    def assemblable(p: dict) -> bool:
        fc = (p["filterClass"] or "").strip().lower()
        if fc in EXCLUDE_CLASSES:
            return False
        return fc in ASSEMBLY_CLASSES

    flagged = [p for p in products if assemblable(p)]
    top = [p for p in flagged if p["badge"] == "TOP_SELLER"]

    # De-duplicate by product family name, keeping the most-reviewed variant.
    def dedupe(items: list[dict]) -> list[dict]:
        best: dict[str, dict] = {}
        for p in items:
            fam = (p["name"] or "?").upper()
            cur = best.get(fam)
            if cur is None or (p["reviews"] or 0) > (cur["reviews"] or 0):
                best[fam] = p
        return sorted(best.values(), key=lambda p: (p["reviews"] or 0), reverse=True)

    ranked = dedupe(top)
    ranked_all = dedupe(flagged)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({
            "market": MARKET,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "queries": QUERIES,
            "stats": {
                "products_seen": len(products),
                "assemblable": len(flagged),
                "top_seller_flagged": len(top),
                "after_dedupe": len(ranked),
            },
            "badge_counts": badge_counts,
            "top_sellers": ranked,
            "assemblable_all": ranked_all,
        }, f, ensure_ascii=False, indent=2)

    if a.raw:
        with open(a.raw, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"\nseen={len(products)} assemblable={len(flagged)} "
          f"top_seller={len(top)} after_dedupe={len(ranked)}")
    print(f"\n{'#':>3} {'name':<14} {'type':<28} {'class':<28} {'rev':>6}  dims")
    for i, p in enumerate(ranked[:40], 1):
        print(f"{i:>3} {(p['name'] or '')[:14]:<14} "
              f"{(p['typeName'] or '')[:28]:<28} "
              f"{(p['filterClass'] or '')[:28]:<28} "
              f"{p['reviews'] or 0:>6}  {p['dims'] or ''}")
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
