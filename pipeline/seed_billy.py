#!/usr/bin/env python3
"""
Author BILLY (AA-1823127-9) as the reference build.

Everything here is either published by IKEA (80x28x202 cm, the hardware counts
printed in the manual) or derived from the manual's own page structure. Panel
thicknesses and shelf heights are read off the drawings, so they are close, not
measured - which is exactly what the 'notes' field on a build is for.

Convention for parts (see schema):
  size = [a, b, t]   mesh is BoxGeometry(a, t, b): 'a' along local X, 'b' along
                     local Z, t = thickness along local Y (i.e. lying flat).
  rot  = [rx, ry, rz] degrees, applied to reach the assembled orientation.
                     rot [0,0,0]   -> a horizontal board (shelf, top, bottom)
                     rot [90,0,0]  -> an upright panel facing front/back
                     rot [90,90,0] -> an upright panel turned to be a side
  at   = assembled position in cm, origin at the floor, centre of the product.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SLUG = "billy-boekenkast-wit-00263850"
T = 2.2          # panel thickness, read off the drawings
W, D, H = 80, 28, 202

PARTS = [
    # id,     label,                    size,          at,                  rot,        count
    ("SL",  "Left side",             [D, H, T],     [-(W/2 - T/2), H/2, 0], [90, 90, 0], 1),
    ("SR",  "Right side",            [D, H, T],     [  W/2 - T/2,  H/2, 0], [90, 90, 0], 1),
    ("BOT", "Bottom",                [W, D, T],     [0, T/2, 0],            [0, 0, 0],   1),
    ("MID", "Fixed middle shelf",    [W, D, T],     [0, H/2, 0],            [0, 0, 0],   1),
    ("TOP", "Top",                   [W, D, T],     [0, H - T/2, 0],        [0, 0, 0],   1),
    ("PL",  "Plinth",                [W, 9, 1.8],   [0, 4.5, D/2 - 4],      [90, 0, 0],  1),
    ("BK",  "Back, folded in three", [W - 4, H - 4, 0.3], [0, H/2, -(D/2 - 0.2)], [90, 0, 0], 1),
]
for i, y in enumerate([38, 68, 132, 162], start=1):
    PARTS.append((f"SH{i}", f"Adjustable shelf {i}", [W, D, T], [0, y, 0], [0, 0, 0], 1))

# Hardware counts as printed in AA-1823127-9. Total 82.
HARDWARE = [
    ("dowel",    "Wooden dowel",        16, "#c9a24a"),
    ("camscrew", "Cam screw",           12, "#c9cdd2"),
    ("cam",      "Cam lock",            12, "#cfc5b4"),
    ("nail",     "Nail",                18, "#9aa3ad"),
    ("pin",      "Shelf pin",           16, "#c9cdd2"),
    ("bracket",  "Wall bracket",         2, "#c9cdd2"),
    ("screw",    "Screw for bracket",    2, "#c9cdd2"),
    ("washer",   "Washer",               4, "#c9cdd2"),
]

# The manual's own page structure (printed pages 5-13 carry the build;
# 1 is the cover, 2-4 are the tip-over warning in ~25 languages, 14-16 back matter).
STEPS = [
    (5,  "What is in the box",
     "Two sides, a top, a bottom, a fixed shelf, a plinth, four shelves and a back folded in "
     "three, with 82 pieces of hardware. Lay it all out on something soft.",
     [], {}),
    (6,  "Dowels",
     "Tap a wooden dowel into each hole in the inner face of both sides. The dowels only line "
     "things up; the cam locks do the clamping.", [], {"dowel": 16}),
    (7,  "Cam screws, plinth, bottom, fixed shelf",
     "Screw a cam screw into every marked hole. Fit the plinth, the bottom and the fixed middle "
     "shelf onto the first side.", ["SL", "PL", "BOT", "MID"], {"camscrew": 12}),
    (8,  "Lock four cams, fit the top",
     "Turn each cam lock half a turn clockwise to pull the joint tight, then fit the top board.",
     ["TOP"], {"cam": 4}),
    (9,  "The second side, lock six more cams",
     "Bring the second side down onto the dowels and cam screws, then lock all six remaining cams.",
     ["SR"], {"cam": 8}),
    (10, "Turn it over, slide the back in",
     "With help, turn the case face down. Slide the folded back panel into the grooves in all "
     "four boards.", ["BK"], {}),
    (11, "Nail the back",
     "Nail the back panel along its edges. The back is what stops the case racking out of square.",
     [], {"nail": 18}),
    (12, "Stand it up, fix it to the wall",
     "Stand the bookcase up and fix the two wall brackets. Screws and plugs for the wall are not "
     "included: use ones suited to your wall.",
     [], {"bracket": 2, "screw": 2, "washer": 4}),
    (13, "Shelf pins and shelves",
     "Push four shelf pins into the holes at the height you want, per shelf, then lay each shelf "
     "on its pins.", ["SH1", "SH2", "SH3", "SH4"], {"pin": 16}),
]


def main() -> int:
    path = os.path.join(ROOT, "products", SLUG, "build.json")
    if not os.path.exists(path):
        print("no build.json - run scaffold.py first")
        return 1
    doc = json.load(open(path, encoding="utf-8"))

    doc["status"] = "draft"
    doc["product"].update({
        "name": "BILLY", "typeName": "Boekenkast", "article": "AA-1823127-9",
        "dims": {"w": W, "d": D, "h": H, "unit": "cm", "text": f"{W}x{D}x{H} cm"},
    })

    doc["parts"] = [
        {"id": i, "label": lab, "kind": "panel", "size": size,
         "at": at, "rot": rot, "count": n, "color": "#f2ede3", "keys": []}
        for (i, lab, size, at, rot, n) in PARTS
    ]
    doc["hardware"] = [
        {"id": i, "label": lab, "count": n, "color": col, "partNo": ""}
        for (i, lab, n, col) in HARDWARE
    ]

    by_page = {s["page"]: s for s in (doc.get("steps") or [])}
    doc["steps"] = []
    for pg, title, prose, parts, hw in STEPS:
        old = by_page.get(pg) or {}
        doc["steps"].append({
            "title": title, "page": pg, "box": old.get("box"),
            # preserve provenance: a box that came from autofill stays "auto".
            # Never promote machine output to "human" just because it exists.
            "boxSource": old.get("boxSource", "auto"), "kind": None,
            "duration": 5, "cam": old.get("cam"),
            "camSource": old.get("camSource", "auto"),
            "placeParts": parts, "placeHardware": hw, "prose": prose, "warn": "",
        })
    # the cover is not a build page
    doc["manual"]["buildPages"] = [s[0] for s in STEPS]

    doc["tags"] = [
        {"label": "2 sides", "at": [-(W / 2 + 16), H / 2, 0], "color": "#7fe3ff"},
        {"label": "Top, fixed shelf, bottom", "at": [0, H / 2, 46], "color": "#7fe3ff"},
        {"label": "Plinth", "at": [0, 6, 40], "color": "#7fe3ff"},
        {"label": "4 shelves", "at": [W / 2 + 18, 100, 0], "color": "#7fe3ff"},
        {"label": "Back, folded in three", "at": [0, H / 2, -46], "color": "#7fe3ff"},
        {"label": "82 pieces of hardware", "at": [0, H + 14, 0], "color": "#ffb454"},
    ]
    doc["notes"] = (
        "Parts, counts, order and hardware come from IKEA manual AA-1823127-9. "
        "Board sizes are from the published 80x28x202 cm; panel thickness (2.2 cm), shelf "
        "heights and hole positions are read off the drawings, so they are close, not measured. "
        "Camera framing and page hotspots are still to be authored in the tool."
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    total_hw = sum(h[2] for h in HARDWARE)
    print(f"seeded {SLUG}")
    print(f"  {len(doc['parts'])} parts, {len(doc['hardware'])} hardware types "
          f"({total_hw} pieces), {len(doc['steps'])} steps, pages {doc['manual']['buildPages']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
