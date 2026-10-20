#!/usr/bin/env python3
"""Screenshot each product viewer and measure how much of the 3D pane is
actually occupied by bright panel pixels. Coarse 'content fraction' is
useless here: the floor and grid fill the pane whether or not anything
rendered. Luminance > 170 isolates the near-white panels."""
import sys, os
from PIL import Image
import numpy as np

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("tools/shoot.py needs playwright:  pip install playwright && playwright install chromium")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PORT = os.environ.get("PORT", "8000")

SLUGS = [
    "billy-boekenkast-wit-00263850",
    "lack-tafeltje-wit-30449908",
    "marius-kruk-zwart-10135659",
    "gladom-salontafel-met-dienblad-zwart-50411990",
    "agam-kinderstoel-zwart-70253541",
]
# 3D pane: right ~64% of width, below the header and above the playback bar
X0, X1, Y0, Y1 = 0.36, 1.00, 0.08, 0.92

def measure(path):
    im = Image.open(path).convert("L")
    a = np.asarray(im).astype(float)
    h, w = a.shape
    pane = a[int(h*Y0):int(h*Y1), int(w*X0):int(w*X1)]
    bright = pane > 170
    frac = bright.mean() * 100
    ys, xs = np.nonzero(bright)
    span = ""
    if len(ys):
        span = (f"  span x {xs.min():4d}-{xs.max():4d} /{pane.shape[1]} "
                f"y {ys.min():4d}-{ys.max():4d} /{pane.shape[0]}")
    return frac, span

def main():
    out_dir = os.path.join(ROOT, "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1600, "height": 950})
        for slug in SLUGS:
            name = slug.split("-")[0]
            out = os.path.join(out_dir, f"shot_{name}.png")
            try:
                msgs = []
                pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text}")
                      if m.type == "error" else None)
                pg.goto(f"http://127.0.0.1:{PORT}/viewer/?id={slug}",
                        wait_until="networkidle")
                pg.wait_for_timeout(3500)
                pg.screenshot(path=out)
                frac, span = measure(out)
                print(f"{name:<8} {frac:6.2f}% bright{span}")
                for m in msgs[:3]:
                    print(f"         console {m[:110]}")
            except Exception as e:
                errs.append(slug)
                print(f"{name:<8} ERROR {type(e).__name__}: {str(e)[:100]}")
        b.close()
    return 1 if errs else 0

sys.exit(main())
