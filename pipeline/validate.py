#!/usr/bin/env python3
"""
Validate every products/*/build.json against schema/build.schema.json,
plus the cross-references the schema cannot express on its own.

JSON Schema can say "this field is a string". It cannot say "this part id
actually exists", or "the screws handed out over the steps add up to the
screws in the box". Those are the mistakes that survive a schema check and
then surface as a blank 3D view or a hardware counter that goes negative,
so they are checked here.

    python3 pipeline/validate.py            # all products
    python3 pipeline/validate.py lack       # match on slug substring

Exit code is 0 when everything passes, 1 otherwise.
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

try:
    import jsonschema
except ImportError:
    sys.exit("pipeline/validate.py needs jsonschema:  pip install jsonschema")


def cross_reference(doc):
    """Structural checks beyond what the schema can express."""
    problems = []
    name = doc.get("product", {}).get("name", "?")

    part_ids = {p["id"] for p in doc.get("parts", [])}
    hw_ids = {h["id"] for h in doc.get("hardware", [])}
    pages = {p["page"] for p in doc.get("manual", {}).get("pages", [])}

    for i, st in enumerate(doc.get("steps", []), 1):
        where = f"step {i} ({st.get('title', '?')[:28]})"

        for pid in st.get("placeParts", []):
            if pid not in part_ids:
                problems.append(f"{where}: placeParts references unknown part '{pid}'")

        for hid, n in (st.get("placeHardware") or {}).items():
            if hid not in hw_ids:
                problems.append(f"{where}: placeHardware references unknown hardware '{hid}'")

        box = st.get("box")
        if box:
            if len(box) != 4:
                problems.append(f"{where}: box must have 4 components, has {len(box)}")
            else:
                x0, y0, x1, y1 = box
                if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
                    problems.append(f"{where}: box {box} is not a sane normalised rect")

        pg = st.get("page")
        if pg is not None and pages and pg not in pages:
            problems.append(f"{where}: page {pg} is not in the manual")

        if st.get("page") is not None and st.get("page") not in doc.get("manual", {}).get("buildPages", [pg]):
            problems.append(f"{where}: page {pg} is not listed in manual.buildPages")

    # Do the fasteners handed out equal the fasteners in the box?
    for h in doc.get("hardware", []):
        placed = sum((s.get("placeHardware") or {}).get(h["id"], 0) for s in doc.get("steps", []))
        if placed > h["count"]:
            problems.append(
                f"hardware '{h['id']}': steps hand out {placed}, box only has {h['count']}")

    return problems


def main() -> int:
    schema = json.load(open(os.path.join(ROOT, "schema", "build.schema.json"), encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)

    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    files = sorted(glob.glob(os.path.join(ROOT, "products", "*", "build.json")))
    if pattern:
        files = [f for f in files if pattern in f]

    ok = bad = 0
    for path in files:
        slug = os.path.basename(os.path.dirname(path))
        doc = json.load(open(path, encoding="utf-8"))
        name = doc.get("product", {}).get("name", "?")[:22]

        errs = [f"{'/'.join(str(x) for x in e.absolute_path) or '(root)'}: {e.message}"
                for e in validator.iter_errors(doc)]
        errs += cross_reference(doc)

        if errs:
            bad += 1
            print(f"FAIL  {name:<22} {slug}")
            for e in errs[:6]:
                print(f"        {e[:100]}")
            if len(errs) > 6:
                print(f"        ... and {len(errs) - 6} more")
        else:
            ok += 1

    print(f"\n{ok} valid, {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
