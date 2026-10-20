#!/usr/bin/env python3
"""
Author MARIUS, GLADOM and AGAM - the next three cheapest products (17 build
pages between them) to prove the workflow repeats outside BILLY and LACK.

What is evidence and what is inference, per product:

  HARDWARE  read straight out of the PDFs' text layer. These three, unlike
            BILLY, DO have extractable text. AGAM is self-checking: the
            per-page quantities (4+2+2+2+1+1+4) sum to exactly the 16x stated
            on its parts page.
  HOTSPOTS  the coarse pass of suggest_boxes.py, merged where one drawing was
            split into a row of callouts.
  PARTS     geometry is PROVISIONAL. Board sizes and leg sections are not
            published for these, so they are estimated from the product
            dimensions and marked as such in each build's notes.
  PROSE     written to match the hardware action on each page, not invented
            detail. All three are left at status "review": the words need
            someone who can see the drawings.

    python3 seed_batch.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def corner_parts(prefix, w, d, leg, leg_h, inset, count=4, y=None):
    """count legs standing at the corners of a w x d footprint."""
    off_w = w / 2 - leg / 2 - inset
    off_d = d / 2 - leg / 2 - inset
    corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)][:count]
    return [
        (f"{prefix}{i}", f"Leg {i}", [leg, leg_h, leg],
         [sx * off_w, y if y is not None else leg_h / 2, sz * off_d], [90, 0, 0], 1)
        for i, (sx, sz) in enumerate(corners, start=1)
    ]


SPECS = {}

# ---------------------------------------------------------------- MARIUS
# AA-302068-12, stool, 45 cm. Text layer gives 4x, 4x, 1x, 1x, 1x and a load
# rating of 110 kg. Part numbers present: 109566, 104875, 10004961, 108184,
# 10123077/78/96/75, 10128375/77.
SPECS["marius-kruk-zwart-10135659"] = {
    "product": {"name": "MARIUS", "typeName": "Kruk", "article": "AA-302068-12",
                "dims": {"w": 34, "d": 34, "h": 45, "unit": "cm", "text": "34x34x45 cm"}},
    "parts": [("SEAT", "Seat", [34, 34, 2.5], [0, 45 - 1.25, 0], [0, 0, 0], 1)]
              + corner_parts("LEG", 34, 34, 3.5, 42.5, 3.0),
    "hardware": [
        {"id": "screw", "label": "Screw", "partNo": "109566", "count": 4, "color": "#c9cdd2"},
        {"id": "bolt", "label": "Bolt", "partNo": "104875", "count": 4, "color": "#9aa3ad"},
    ],
    "steps": [
        (1, [0.0880, 0.0674, 0.6495, 0.1672], "What is in the box",
         "A seat, four legs, four screws (109566) and four bolts (104875). Max load 110 kg.",
         [], {}),
        (1, [0.1755, 0.2261, 0.9245, 0.9644], "Turn the seat over",
         "Lay the seat face down on something soft so you can reach the leg holes.", [], {}),
        (2, [0.0730, 0.0480, 0.9245, 0.4653], "Fit the legs",
         "Seat each leg in its corner socket, hand-tight.", ["LEG1", "LEG2", "LEG3", "LEG4"], {}),
        (2, [0.0730, 0.4730, 0.9245, 0.6804], "Screw and bolt each leg",
         "A screw and a bolt per leg. Do not fully tighten yet.", [],
         {"screw": 4, "bolt": 4}),
        (2, [0.0755, 0.6882, 0.9245, 0.8903], "Tighten and stand it up",
         "Go round all four legs and tighten, then turn the stool the right way up.", ["SEAT"], {}),
        (3, [0.0955, 0.0356, 0.9095, 0.9644], "Check it is level",
         "Set it on a flat floor and check all four legs touch.", [], {}),
        (4, [0.0730, 0.0480, 0.9245, 0.8903], "Done",
         "34x34x45 cm. Rated to 110 kg.", [], {}),
    ],
    "notes": ("Hardware counts and part numbers read from the PDF text layer (4x 109566, "
              "4x 104875, load 110 kg); further part numbers 10004961 / 108184 / 1012307x / "
              "1012837x are on the page but their roles are unconfirmed. Board sizes and leg "
              "sections are PROVISIONAL and estimated from the 45 cm height - measure a real "
              "stool before trusting the 3D. Hotspots are the coarse pass; the row of four "
              "callouts on page 2 was merged into one box. Prose needs a reader who can see "
              "the drawings."),
}

# ---------------------------------------------------------------- GLADOM
# AA-2544925-1, tray table, 45x53 cm. Page 4 text: 1x, 1x, 1x, 3x with
# 100006, 123451, 122202. Page 5: 1x. Page 6: 2x.
SPECS["gladom-salontafel-met-dienblad-zwart-50411990"] = {
    "product": {"name": "GLADOM", "typeName": "Salontafel met dienblad",
                "article": "AA-2544925-1",
                "dims": {"w": 45, "d": 45, "h": 53, "unit": "cm", "text": "45x45x53 cm"}},
    "parts": [("TRAY", "Tray top", [45, 45, 4], [0, 53 - 2, 0], [0, 0, 0], 1)]
              + corner_parts("LEG", 45, 45, 2.5, 49, 3.5, count=4, y=24.5),
    "hardware": [
        {"id": "screw", "label": "Screw", "partNo": "122202", "count": 4, "color": "#c9cdd2"},
    ],
    "steps": [
        (1, [0.0580, 0.0535, 0.6895, 0.1536], "What is in the box",
         "A tray top, a frame and four screws (122202).", [], {}),
        (1, [0.1480, 0.2376, 0.9495, 0.9800], "Lay out the frame",
         "Lay the frame down so you can reach the fixing points.", [], {}),
        (4, [0.2680, 0.0464, 0.5595, 0.2138], "Screws for the tray",
         "One screw per corner of the tray.", [], {"screw": 1}),
        (4, [0.5880, 0.0464, 0.6645, 0.2138], "The remaining screws",
         "Three more, kept hand-tight until the tray sits right.", [], {"screw": 3}),
        (4, [0.0755, 0.2570, 0.9120, 0.9147], "Fit the tray to the frame",
         "Lower the tray onto the frame and start all four screws.", ["TRAY"], {}),
        (5, [0.0830, 0.1084, 0.9295, 0.6385], "Tighten",
         "Tighten all four, working across the tray rather than round it.",
         ["LEG1", "LEG2", "LEG3", "LEG4"], {}),
        (6, [0.0730, 0.0411, 0.8970, 0.8085], "Stand it up",
         "Turn the table the right way up and check it sits flat.", [], {}),
        (7, [0.2305, 0.0411, 0.7670, 0.7624], "Lift the tray off",
         "The tray lifts clear of the frame - that is the point of it. 45x45x53 cm.", [], {}),
    ],
    "notes": ("Part numbers 122202 / 100006 / 123451 and the 1x-1x-1x-3x, 1x and 2x counts come "
              "from the PDF text layer; only the four 122202 screws are modelled here because "
              "the roles of 100006 and 123451 are unconfirmed. Geometry is PROVISIONAL - GLADOM "
              "has a bent-tube frame, modelled here as four straight legs, so the 3D is "
              "representative rather than accurate. Prose needs a reader who can see the drawings."),
}

# ---------------------------------------------------------------- AGAM
# AA-183046-9, child's chair. Text: 16x 106553 on the parts page, plus 1x
# 100092 and 1x 121030. Per-page quantities: p4 4x, p5 2x+2x, p6 2x+1x,
# p7 1x+4x  ->  4+2+2+2+1+1+4 = 16. Matches exactly.
SPECS["agam-kinderstoel-zwart-70253541"] = {
    "product": {"name": "AGAM", "typeName": "Kinderstoel", "article": "AA-183046-9",
                "dims": {"w": 32, "d": 30, "h": 55, "unit": "cm", "text": "32x30x55 cm"}},
    "parts": [("SEAT", "Seat", [32, 30, 2], [0, 32, 0], [0, 0, 0], 1),
              ("BACK", "Back", [32, 24, 2], [0, 46, -13], [90, 0, 0], 1)]
              + corner_parts("LEG", 32, 30, 3, 30, 2.5, y=15),
    "hardware": [
        {"id": "screw", "label": "Screw", "partNo": "106553", "count": 16, "color": "#c9cdd2"},
    ],
    "steps": [
        (2, [0.0755, 0.0674, 0.7245, 0.2025], "What is in the box",
         "Seat, back, four legs and sixteen screws (106553).", [], {}),
        (2, [0.1830, 0.2296, 0.9245, 0.9644], "Lay the parts out",
         "Everything on a soft surface, screws to hand.", [], {}),
        (3, [0.0755, 0.0480, 0.9270, 0.4670], "Fit the back to the seat",
         "Offer the back up to the seat and line the holes up.", ["BACK"], {}),
        (4, [0.0980, 0.0480, 0.9270, 0.4370], "First four screws",
         "Four screws to hold the back on. Hand-tight only.", [], {"screw": 4}),
        (4, [0.0730, 0.4589, 0.9270, 0.9644], "Check the angle",
         "Make sure the back is square before anything is tightened.", [], {}),
        (5, [0.0730, 0.0497, 0.9295, 0.4670], "Two screws, front",
         "Two screws into the front rail.", [], {"screw": 2}),
        (5, [0.0730, 0.4748, 0.9270, 0.8938], "Two screws, back",
         "Two more at the back.", [], {"screw": 2}),
        (6, [0.0755, 0.0497, 0.9270, 0.9115], "Legs on",
         "Three screws to fix the legs.", ["LEG1", "LEG2", "LEG3", "LEG4"],
         {"screw": 3}),
        (7, [0.0680, 0.0480, 0.9270, 0.9626], "Five screws, tighten up",
         "Five screws, then go round and tighten everything.", ["SEAT"], {"screw": 5}),
        (8, [0.0980, 0.0656, 0.7845, 0.8938], "Done",
         "32x30x55 cm. Check it does not rock.", [], {}),
    ],
    "notes": ("Hardware is the strongest part of this build: 16x 106553 is stated on the parts "
              "page, and the per-page quantities (4+2+2+2+1+1+4) sum to exactly 16, so the "
              "screw counts per step are cross-checked rather than guessed. 1x 100092 and 1x "
              "121030 are also listed and unmodelled. Geometry is PROVISIONAL - no published "
              "dimensions, so 32x30x55 cm and all sections are estimates. Hotspots are the "
              "coarse pass. Prose needs a reader who can see the drawings."),
}


def main() -> int:
    for slug, sp in SPECS.items():
        path = os.path.join(ROOT, "products", slug, "build.json")
        if not os.path.exists(path):
            print(f"  skip {slug}: no build.json, run scaffold.py first")
            continue
        doc = json.load(open(path, encoding="utf-8"))
        doc["status"] = "review"
        doc["product"].update(sp["product"])

        doc["parts"] = [
            {"id": i, "label": lab, "kind": "panel", "size": [float(v) for v in size],
             "at": [float(v) for v in at], "rot": rot, "count": n,
             "color": "#f2ede3", "keys": []}
            for (i, lab, size, at, rot, n) in sp["parts"]
        ]
        doc["hardware"] = sp["hardware"]
        doc["steps"] = [
            {"title": t, "page": pg, "box": box, "boxSource": "auto",
             "kind": None, "duration": 4, "cam": None, "camSource": "auto",
             "placeParts": parts, "placeHardware": hw, "prose": prose, "warn": ""}
            for (pg, box, t, prose, parts, hw) in sp["steps"]
        ]
        pages = sorted({s["page"] for s in doc["steps"]})
        doc["manual"]["buildPages"] = pages
        doc["notes"] = sp["notes"]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        hw_total = sum(h["count"] for h in doc["hardware"])
        placed = sum(sum(s["placeHardware"].values()) for s in doc["steps"])
        ok = "OK" if placed == hw_total else f"MISMATCH ({placed} placed vs {hw_total} listed)"
        print(f"  {doc['product']['name']:<8} {len(doc['parts']):>2} parts, "
              f"{hw_total:>2} fasteners, {len(doc['steps']):>2} steps on pages {pages}  "
              f"hardware {ok}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
