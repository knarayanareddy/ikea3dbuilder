#!/usr/bin/env python3
"""
Auto-suggest hotspot boxes for every build page.

IKEA lays each page out as one or more drawing panels separated by white gutters.
Find the gutters and you have the hotspots: horizontal bands first, then vertical
splits inside a band (some pages carry two steps side by side).

    python3 suggest_boxes.py                # all products
    python3 suggest_boxes.py --id <slug>    # one
    python3 suggest_boxes.py --validate     # score against the sael.net fixture

Writes products/<slug>/suggested_boxes.json. The authoring tool offers these as
one-click "apply suggestion", so authoring a step becomes confirming a box
rather than drawing one.
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- tunables -------------------------------------------------------------
W = 400                  # analysis width; only ratios matter
INK = 200                # luminance below this counts as ink
ROW_ON = 0.004           # a row is "used" above this ink fraction
COL_ON = 0.006
MIN_BAND_H = 0.035       # ignore slivers (page numbers, rules)
MIN_COL_W = 0.045
MERGE_ROW_GAP = 0.014    # glue bands split by a hairline
MERGE_COL_GAP = 0.020
PAD = 0.012              # breathing room around the content
X_MARGIN = 0.035         # keep clear of the page edge / spine
Y_MARGIN = 0.020


def load(path: str):
    im = Image.open(path).convert("L")
    h = max(1, int(im.height * W / im.width))
    im = im.resize((W, h))
    a = np.asarray(im, dtype=np.float32)
    return (a < INK), W, h


def runs(mask: np.ndarray, min_len: int, merge_gap: int):
    """Contiguous True runs, gluing together runs split by < merge_gap."""
    idx = np.flatnonzero(mask)
    out = []
    if idx.size == 0:
        return out
    start = prev = idx[0]
    for i in idx[1:]:
        if i - prev > merge_gap:
            out.append((start, prev + 1))
            start = i
        prev = i
    out.append((start, prev + 1))
    # glue short gaps
    merged = []
    for s, e in out:
        if merged and s - merged[-1][1] < merge_gap:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return [(s, e) for s, e in merged if (e - s) >= min_len]


def deep_split(prof: np.ndarray, n: int, P: dict, depth: int = 0):
    """Split an oversized band at its deepest interior valley.

    Most panels are separated by a white gutter, but two drawings sometimes
    touch - and a plain threshold then reads them as one panel. Only try this
    on bands that are suspiciously tall, and only once: repeated splitting is
    how you end up chopping a single drawing into six.
    """
    if depth > 1:
        return None
    minh = int(P["min_band_h"] * n)
    lo, hi = minh, len(prof) - minh
    if hi - lo < 4:
        return None
    k = max(3, int(0.015 * n))
    sm = np.convolve(prof, np.ones(k) / k, mode="same")
    i = lo + int(np.argmin(sm[lo:hi]))
    # the valley must be genuinely quiet relative to the panel's own ink level
    if sm[i] > P["valley"] * float(np.percentile(sm, 75)):
        return None
    return i


def suggest(path: str, P: dict | None = None) -> list[dict]:
    P = P or PARAMS
    ink, w, h = load(path)
    rows = ink.mean(axis=1)

    bands = runs(rows > P["row_on"], int(P["min_band_h"] * h),
                 int(P["merge_row"] * h))
    if P.get("tall"):
        out = []
        for (y0, y1) in bands:
            if (y1 - y0) / h > P["tall"]:
                i = deep_split(rows[y0:y1], h, P)
                if i:
                    out += [(y0, y0 + i), (y0 + i, y1)]
                    continue
            out.append((y0, y1))
        bands = out

    boxes = []
    for (y0, y1) in bands:
        band = ink[y0:y1]
        cols = band.mean(axis=0)
        segs = runs(cols > P["col_on"], int(P["min_col_w"] * w),
                    int(P["merge_col"] * w))
        if not segs:
            segs = [(0, w)]
        for (x0, x1) in segs:
            cell = band[:, x0:x1]
            b = [
                max(X_MARGIN, x0 / w - PAD),
                max(Y_MARGIN, y0 / h - PAD),
                min(1 - X_MARGIN, x1 / w + PAD),
                min(1 - Y_MARGIN, y1 / h + PAD),
            ]
            boxes.append({"box": [round(v, 4) for v in b],
                          "ink": round(float(cell.mean()), 4)})
    boxes = [b for b in boxes if b["ink"] > 0.004]
    boxes = dedupe(boxes)
    boxes.sort(key=lambda b: (b["box"][1], b["box"][0]))
    return boxes


# Grid-searched over 648 combinations against the hand-placed fixture in
# data/_validation_billy_boxes.json: mean IoU 0.761, and the panel count is
# exactly right on 7 of 8 pages. Deep-splitting tall bands was tried and lost -
# it fixed two pages and broke four, so it is off by default.
PARAMS = {
    "row_on": ROW_ON,
    "col_on": COL_ON,
    "min_band_h": 0.050,
    "min_col_w": 0.045,
    "merge_row": 0.030,      # generous: glue a panel to its hardware callouts
    "merge_col": 0.050,
    "tall": None,            # deep-split disabled: net negative on the fixture
    "valley": 0.45,
}

# Fine pass: same method, much tighter merging. Some pages pack several build
# phases into one drawing (LACK does the whole table in a single panel); coarse
# merges those, fine separates them.
FINE_PARAMS = dict(PARAMS, min_band_h=0.022, min_col_w=0.030,
                   merge_row=0.006, merge_col=0.012, tall=None)


def dedupe(boxes: list[dict]) -> list[dict]:
    """Drop any box mostly contained in an earlier one."""
    out = []
    for b in boxes:
        x0, y0, x1, y1 = b["box"]
        if any(x0 >= o["box"][0] - .01 and y0 >= o["box"][1] - .01 and
               x1 <= o["box"][2] + .01 and y1 <= o["box"][3] + .01 for o in out):
            continue
        out.append(b)
    return out


def iou(a, b):
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0, ix1 - ix0), max(0, iy1 - iy0)
    inter = iw * ih
    area = lambda r: max(0, r[2] - r[0]) * max(0, r[3] - r[1])
    union = area(a) + area(b) - inter
    return inter / union if union else 0.0


# ------------------------------------------------------------------ driver
def process(slug: str) -> dict | None:
    bj = os.path.join(ROOT, "products", slug, "build.json")
    if not os.path.exists(bj):
        return None
    d = json.load(open(bj, encoding="utf-8"))
    man = d.get("manual") or {}
    pages = {p["page"]: p["file"] for p in (man.get("pages") or [])}
    out = {"id": slug, "pages": {}}
    for pg in (man.get("buildPages") or []):
        f = pages.get(pg)
        if not f:
            continue
        p = os.path.join(ROOT, "products", slug, man.get("dir") or "manual", f)
        if os.path.exists(p):
            # two granularities: coarse matches how a human boxes a page,
            # fine exposes sub-panels for pages that carry several phases
            out["pages"][str(pg)] = {
                "coarse": suggest(p, PARAMS),
                "fine": suggest(p, FINE_PARAMS),
            }
    with open(os.path.join(ROOT, "products", slug, "suggested_boxes.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    return out


def validate() -> int:
    """Score the detector against hand-placed boxes scraped from sael.net.

    Fixture lives in data/_validation_billy_boxes.json and is benchmarking
    only - it is not shipped as product data.
    """
    fx = os.path.join(ROOT, "data", "_validation_billy_boxes.json")
    if not os.path.exists(fx):
        print("no fixture at data/_validation_billy_boxes.json")
        return 1
    truth = json.load(open(fx, encoding="utf-8"))["boxes"]
    got = process("billy-boekenkast-wit-00263850")
    if not got:
        return 1

    scores = []
    for t in truth:
        pg = str(t["page"])
        cands = [b["box"] for b in (got["pages"].get(pg, {}).get("coarse") or [])]
        best = max((iou(t["box"], c) for c in cands), default=0.0)
        scores.append((t["page"], t["title"], best))

    print(f"{'pg':>3}  {'step':<34} IoU vs hand-placed")
    for pg, title, s in scores:
        bar = "█" * int(s * 30)
        print(f"{pg:>3}  {title[:34]:<34} {s:.2f} {bar}")
    mean = sum(s for _, _, s in scores) / len(scores)
    print(f"\nmean IoU {mean:.3f} over {len(scores)} hand-placed boxes")
    print("(0.5+ is a usable suggestion to confirm, 0.7+ is close to as-drawn)")

    # how many panels did we find vs how many exist?
    for pg in sorted({t["page"] for t in truth}):
        n_truth = sum(1 for t in truth if t["page"] == pg)
        n_got = len(got["pages"].get(str(pg), {}).get("coarse") or [])
        flag = "" if n_truth == n_got else "   <- count mismatch"
        print(f"  page {pg}: {n_got} suggested vs {n_truth} hand-placed{flag}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()

    if a.validate:
        return validate()

    slugs = [a.id] if a.id else [os.path.basename(os.path.dirname(p))
                                 for p in sorted(glob.glob(os.path.join(ROOT, "products", "*", "build.json")))]
    total = 0
    for s in slugs:
        r = process(s)
        if not r:
            continue
        n = sum(len(v.get("coarse") or []) for v in r["pages"].values())
        total += n
        print(f"  {s[:46]:<46} {n:>3} boxes over {len(r['pages'])} pages")
    print(f"\n{total} suggested boxes across {len(slugs)} products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
