# IKEA 3D Builder (`ikea3dbuilder`)

An interactive 3D flat-pack assembly engine that pairs real IKEA assembly manuals with physically accurate, page-by-page 3D builds.

Built to replicate and expand upon [sael.net/flatpack](https://sael.net/flatpack/) with 1:1 mechanical precision, procedural geometry, dual-mode PBR and vector line-art rendering, and authentic IKEA assembly choreography.

---

## 🌟 Featured Builds (10/10 Fidelity)

| Build | Article | Steps | Key Features |
|---|---|---|---|
| **BILLY Bookcase** | `002.638.50` | 14 | Cam-lock pins (`pn`), wood dowels, shelf-peg grids, slide-in back panel, plinth kick |
| **LACK Side Table** | `304.499.08` | 3 | Double-ended screws (`115980`) with spiral threads, inverted leg drive, rug flip |
| **MARIUS Stool** | `101.356.59` | 4 | Perforated seat disc (37 concentric holes), 4 curved tubular steel legs, sleeve bolts `104875`, screws `109566`, 180° flip |
| **GLADOM Tray Table** | `504.119.90` | 4 | Continuous bent tubular scissor frame, upper support ring with welded tabs, screws `122202`, removable serving tray with rolled rim & lift-off demo |

---

## 🚀 Quick Start

The project runs completely offline with zero external dependencies (Three.js and fonts are vendored in `lib/`).

```bash
# Clone the repository
git clone https://github.com/knarayanareddy/ikea3dbuilder.git
cd ikea3dbuilder

# Start the local development server (default port 8002)
python3 tools/server.py
```

Then open your browser to:
- **BILLY**: [http://localhost:8002/viewer/?kit=billy](http://localhost:8002/viewer/?kit=billy)
- **LACK**: [http://localhost:8002/viewer/?kit=lack](http://localhost:8002/viewer/?kit=lack)
- **MARIUS**: [http://localhost:8002/viewer/?kit=marius](http://localhost:8002/viewer/?kit=marius)
- **GLADOM**: [http://localhost:8002/viewer/?kit=gladom](http://localhost:8002/viewer/?kit=gladom)

---

## 🎮 Controls & Shortcuts

| Key | Action |
|---|---|
| **`Shift + K`** | Cycle between all 4 kits (`BILLY` → `LACK` → `MARIUS` → `GLADOM`) |
| **`V`** | Toggle between **Room 3D View** (PBR) and **Manual Drawing View** (IKEA line art) |
| **`Space`** | Play / pause automatic cinematic assembly animation |
| **`[` / `]`** | Previous / next assembly step |
| **`0` – `9`** | Jump directly to step number (`0` = The Kit overview) |
| **`B`** | Toggle IKEA printed instruction booklet spread overlay |
| **`X`** | Toggle exploded view |
| **`N`** | Toggle part tags & dimensions |
| **`R`** | Reset camera orbit |

### URL Parameters & Deep-Linking
- `?kit=gladom` — load specific kit on boot (`billy`, `lack`, `marius`, `gladom`)
- `?kit=marius&step=2` — jump directly to step 2
- `#marius` / `#gladom` — hash navigation supported

---

## 📐 Mechanical & Visual Details

### 1. GLADOM Tray Table (`50411990`)
- **Continuous Bent-Tube Frame**: Procedural `CurvePath` with smooth $R = 4.0\text{ cm}$ floor bends, bottom floor glides, center interlocking notch, and welded mounting tabs.
- **Upper Retention Ring**: Torus geometry with four welded angle brackets with predrilled screw holes.
- **Pressed-Steel Serving Tray**: 11-point lathe profile featuring a recessed bottom center ($R = 19.2\text{ cm}$), conical flared transition wall ($H = 3.2\text{ cm}$), and an authentic rolled tubular bead lip.
- **Choreography**: Frame sections scissor open and lock at $90^\circ$ around center pivot; ring docks onto frame tabs; 4x pan-head screws `122202` drive with helical spin; tray lowers into ring and demonstrates lift-off serving.

### 2. MARIUS Stool (`10135659`)
- **Perforated Injection-Molded Seat**: Extruded polypropylene disc with 37 concentric ventilation holes (1 center, 6 inner, 12 middle, 18 outer) with rounded edges and 4 underside screw bosses.
- **Tubular Steel Legs**: Authentic compound curve from floor foot to center hub ($r = 3.8\text{ cm}$), flattened hub section with sleeve bolt through-holes, and horizontal mounting tabs.
- **Fasteners & Live Counters**: 4x sleeve bolts `104875` and 4x pointed screws `109566` on separate blister pack cards with live decrements.
- **Choreography**: Legs interlock at center hub; bolts slide axially; assembly mounts to seat underside; entire stool executes a smooth $180^\circ$ flip upright onto its rubber feet.

### 3. BILLY & LACK Replications
- **Zero Deviation**: 100% exact reproduction of Sael's shaders, lighting ratios, postprocessing stack, and timings.

---

## 📂 Repository Structure

```
ikea3dbuilder/
├── index.html              # Standalone 4-kit interactive 3D manual viewer
├── viewer/                 # Viewer entrypoint and reference templates
│   ├── index.html
│   └── sael_direct.html
├── manual/                 # High-resolution manual page scans
│   ├── billy/              # BILLY manual pages (p01–p16)
│   ├── lack/               # LACK manual pages (p01–p04)
│   ├── marius/             # MARIUS manual pages (p01–p04)
│   └── gladom/             # GLADOM manual pages (p08–p08)
├── lib/                    # Vendored Three.js r183, OrbitControls, and fonts
├── products/               # Datasets, builds, and metadata for 28 IKEA products
├── tools/                  # Build scripts, server, and validation suites
│   ├── build_flatpack.py   # Compiles viewer with all 4 builds
│   ├── server.py           # Local HTTP server with CORS support
│   └── test_chrome.py      # Automated headless Chrome test suite
├── screenshots/            # High-resolution renders and showcase steps
│   ├── billy/
│   ├── lack/
│   ├── marius/
│   └── gladom/
├── data/                   # Official IKEA CAD GLB models and reference PDFs
├── pipeline/               # Ingestion and hotspot extraction pipeline
└── schema/                 # JSON schemas for product build definitions
```

---

## 🛠️ Tooling & Rebuilding

To recompile the standalone viewer after modifying kit scripts or parameters:

```bash
python3 tools/build_flatpack.py
```

This updates both `index.html` and `viewer/index.html` synchronously.

---

## 📄 License & Credits

- Inspired by and replicating the design language of [sael.net/flatpack](https://sael.net/flatpack/).
- Product designs, manual illustrations, and trademarks belong to **Inter IKEA Systems B.V.**
