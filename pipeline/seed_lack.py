#!/usr/bin/env python3
"""
Author LACK (AA-207276-4) - the one-page proof case.

LACK is the smallest real build in the catalogue, and the manual packs the whole
thing into a single drawing. The fine pass of suggest_boxes.py separates that
drawing into four panels, which map cleanly onto four phases.

Provenance, stated plainly:
  * 55x55 cm and the 10 kg table-top limit are from IKEA's own product text.
  * Height 45 cm is the published LACK side-table height.
  * Part number 115980 / "4x" IS extractable text - but from the current US
    manual (AA-2606170-1), not this 2006 NL one. This NL page is pure vector
    art with no text at all, so 115980 is left blank here pending a look at
    the drawing. Do not assume it transfers.
  * Panel boxes come from the fine pass, and which lower panel is "legs on"
    versus "turn it over" is inferred from reading order. Confirm by eye.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SLUG = "lack-tafeltje-wit-30449908"

W = D = 55.0
H = 45.0
TOP_T = 3.5              # tabletop thickness
LEG = 5.0                # leg cross-section
LEG_H = H - TOP_T        # 41.5
INSET = 6.0              # leg centre inset from each corner

# [id, label, size[a,b,t], at, rot, count]
PARTS = [
    ("TOP", "Tabletop", [W, D, TOP_T], [0, H - TOP_T / 2, 0], [0, 0, 0], 1),
]
corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
for i, (sx, sz) in enumerate(corners, start=1):
    off = W / 2 - LEG / 2 - INSET
    PARTS.append((f"LEG{i}", f"Leg {i}", [LEG, LEG_H, LEG],
                  [sx * off, LEG_H / 2, sz * off], [90, 0, 0], 1))

# title, page, box (fine pass), prose, parts, hardware, camera
STEPS = [
    ("What is in the box", 1, [0.3355, 0.1738, 0.6645, 0.2456],
     "A tabletop, four legs and four double-ended screws. No tools: this one goes "
     "together by hand. Lay the top face down on something soft.",
     [], {},
     {"target": [0, 0.35, 0], "yaw": -0.50, "pitch": 0.55, "dist": 4.2}),

    ("Screw into the top", 1, [0.3330, 0.2429, 0.6670, 0.4987],
     "Screw a double-ended screw into each corner hole in the underside of the top, "
     "by hand, until it is halfway in.",
     ["TOP"], {"screw": 4},
     {"target": [0, 0.30, 0], "yaw": -0.40, "pitch": 0.70, "dist": 3.0}),

    ("Twist the legs on", 1, [0.3005, 0.4942, 0.5045, 0.6226],
     "Twist a leg onto each screw, clockwise, until it sits tight against the top.",
     [f"LEG{i}" for i in range(1, 5)], {},
     {"target": [0, 0.60, 0], "yaw": -0.45, "pitch": 0.35, "dist": 3.2}),

    ("Turn it over", 1, [0.5555, 0.4942, 0.7445, 0.6226],
     "Turn the table the right way up. Done: 55x55x45 cm. It is a delicate table - "
     "no sitting, and 10 kg on the top at most.",
     [], {},
     {"target": [0, 0.90, 0], "yaw": -0.50, "pitch": 0.18, "dist": 3.8}),
]


def main() -> int:
    path = os.path.join(ROOT, "products", SLUG, "build.json")
    if not os.path.exists(path):
        print("no build.json - run scaffold.py first")
        return 1
    doc = json.load(open(path, encoding="utf-8"))

    doc["status"] = "draft"
    doc["product"].update({
        "name": "LACK", "typeName": "Tafeltje", "article": "AA-207276-4",
        "dims": {"w": W, "d": D, "h": H, "unit": "cm", "text": f"{W:g}x{D:g}x{H:g} cm"},
    })

    doc["parts"] = [
        {"id": i, "label": lab, "kind": "panel", "size": size, "at": at,
         "rot": rot, "count": n, "color": "#f2ede3", "keys": []}
        for (i, lab, size, at, rot, n) in PARTS
    ]
    doc["hardware"] = [
        {"id": "screw", "label": "Double-ended screw", "count": 4,
         "color": "#c9cdd2", "partNo": ""}
    ]
    doc["steps"] = [
        {"title": t, "page": pg, "box": box, "boxSource": "human", "kind": None, "duration": 4,
         "cam": cam, "camSource": "human",
            "placeParts": parts, "placeHardware": hw,
         "prose": prose, "warn": ""}
        for (t, pg, box, prose, parts, hw, cam) in STEPS
    ]
    doc["manual"]["buildPages"] = [1]

    doc["tags"] = [
        {"label": "Tabletop", "at": [0, H + 6, 0], "color": "#7fe3ff"},
        {"label": "4 legs", "at": [W / 2 + 14, LEG_H / 2, 0], "color": "#7fe3ff"},
        {"label": "4 double-ended screws", "at": [-(W / 2 + 14), 4, 0],
         "color": "#ffb454"},
    ]
    doc["notes"] = (
        "55x55 cm and the 10 kg limit are IKEA's own product text; 45 cm is the "
        "published LACK side-table height. Part number 115980 is NOT set here: it "
        "is extractable from the current US manual (AA-2606170-1) but this 2006 NL "
        "page is pure vector art with no text, so it needs confirming against the "
        "drawing. Hotspot boxes are the fine pass of suggest_boxes.py; the mapping "
        "of the two lower panels to 'legs on' and 'turn it over' is inferred from "
        "reading order and wants a human eye. The face-down/turn-over choreography "
        "needs parented keyframes, which the schema supports but the viewer does "
        "not yet play."
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"seeded {SLUG}")
    print(f"  {len(doc['parts'])} parts, 4 screws, {len(doc['steps'])} steps "
          f"on 1 page, {sum(1 for s in doc['steps'] if s['box'])} hotspots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
