#!/usr/bin/env python3
"""
Turn the 27 empty scaffolds into drafts.

Two jobs, both machine-doable, both leaving a human with a correction rather
than a blank:

  1. Hotspots - take the detected panel boxes from suggest_boxes.py and hand
     them out to steps in order, per page.
  2. Cameras  - derive a framing from geometry. Compute the bounding box of
     whatever has been built by the end of each step, aim at its centre, pull
     back far enough to see it. It will not match the drawing's viewpoint -
     that needs an eye - but it is a workable shot to adjust.

Never overwrites an authored box or camera unless --force.

    python3 autofill.py             # all products
    python3 autofill.py --id <slug>
    python3 autofill.py --gran fine
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
S = 0.04          # cm -> world units, matches the viewer


def rot_xyz(deg):
    """three.js Euler order 'XYZ' -> R = Rx @ Ry @ Rz."""
    rx, ry, rz = (math.radians(v) for v in deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def part_aabb(p):
    """Axis-aligned bounds of a part in assembled product coordinates (cm)."""
    a, b, t = (p.get("size") or [0, 0, 0])
    at = p.get("at")
    if not at:
        return None
    R = rot_xyz(p.get("rot") or [0, 0, 0])
    corners = np.array([[sx * a / 2, sy * t / 2, sz * b / 2]
                        for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    c = corners @ R.T + np.array(at)
    return c.min(axis=0), c.max(axis=0)


def cam_for(doc, upto):
    """Frame everything present at the end of step `upto`."""
    parts = doc.get("parts") or []
    placed = []
    for p in parts:
        i = next((k for k, s in enumerate(doc.get("steps") or [])
                  if p["id"] in ((s.get("placeParts") or []))), None)
        if i is not None and i <= upto:
            bb = part_aabb(p)
            if bb:
                placed.append(bb)

    d = (doc.get("product") or {}).get("dims") or {}
    if placed:
        lo = np.min([b[0] for b in placed], axis=0)
        hi = np.max([b[1] for b in placed], axis=0)
    elif d.get("w") and d.get("h") and d.get("d"):
        lo = np.array([-d["w"] / 2, 0, -d["d"] / 2])
        hi = np.array([d["w"] / 2, d["h"], d["d"] / 2])
    else:
        lo, hi = np.array([-40.0, 0, -40.0]), np.array([40.0, 100.0, 40.0])

    centre = (lo + hi) / 2
    extent = hi - lo
    radius = float(np.linalg.norm(extent)) / 2
    # a little context: see the part plus some air
    dist = max(3.0, radius * S * 3.0)
    return {
        "target": [round(float(centre[0]) * S, 3),
                   round(float(centre[1]) * S, 3),
                   round(float(centre[2]) * S, 3)],
        "yaw": -0.45,
        "pitch": 0.35,
        "dist": round(dist, 3),
    }


def process(slug: str, gran: str, force: bool) -> tuple[int, int] | None:
    pdir = os.path.join(ROOT, "products", slug)
    bj = os.path.join(pdir, "build.json")
    sj = os.path.join(pdir, "suggested_boxes.json")
    if not os.path.exists(bj):
        return None
    doc = json.load(open(bj, encoding="utf-8"))
    sugg = {}
    if os.path.exists(sj):
        sugg = json.load(open(sj, encoding="utf-8")).get("pages") or {}

    steps = doc.get("steps") or []
    cursor, nb, nc = {}, 0, 0
    for k, s in enumerate(steps):
        pg = str(s.get("page"))
        if (force or not s.get("box")) and pg in sugg:
            lst = (sugg[pg] or {}).get(gran) or []
            i = cursor.get(pg, 0)
            if i < len(lst):
                s["box"] = [float(v) for v in lst[i]["box"]]
                s["boxSource"] = "auto"
                cursor[pg] = i + 1
                nb += 1
        if force or not s.get("cam"):
            s["cam"] = cam_for(doc, k)
            s["camSource"] = "auto"
            nc += 1

    if nb or nc:
        if doc.get("status") == "scaffold":
            doc["status"] = "draft"
        with open(bj, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    return nb, nc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--gran", default="coarse", choices=["coarse", "fine"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    slugs = [a.id] if a.id else [os.path.basename(os.path.dirname(p))
                                 for p in sorted(glob.glob(os.path.join(ROOT, "products", "*", "build.json")))]
    tot_b = tot_c = 0
    for s in slugs:
        r = process(s, a.gran, a.force)
        if not r:
            continue
        nb, nc = r
        tot_b += nb
        tot_c += nc
        print(f"  {s[:44]:<44} +{nb:>3} boxes  +{nc:>3} cameras")
    print(f"\n{tot_b} hotspot boxes, {tot_c} cameras across {len(slugs)} products")
    print("note: cameras are geometry-derived framing, not viewpoint-matched to "
          "the drawings - adjust in the tool.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
