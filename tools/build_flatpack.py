#!/usr/bin/env python3
"""
Assemble the 4-kit Flat Pack engine:
1. 100% exact copy of BILLY and LACK from sael_direct.html without deviating 1%.
2. Add MARIUS stool (10135659) and GLADOM tray table (50411990) to the exact same visual,
   material, and mechanical standards.
3. Support switching via UI buttons, Shift+K keyboard shortcut, hash (#lack, #marius, #gladom) and URL parameter (?kit=marius).
"""

import sys, os, re

BASE_PATH = "/Users/brightech/Downloads/ikea/flatpack/viewer/sael_direct.html"
OUT_PATH = "/Users/brightech/Downloads/ikea/flatpack/viewer/index.html"
ROOT_PATH = "/Users/brightech/Downloads/ikea/flatpack/index.html"

with open(BASE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Update UI buttons in #seg-kit
src = src.replace(
    '<div class="seg kit" id="seg-kit" role="group" aria-label="Piece"><button data-k="billy" class="on">BILLY bookcase</button><button data-k="lack">LACK table</button></div>',
    '<div class="seg kit" id="seg-kit" role="group" aria-label="Piece"><button data-k="billy" class="on">BILLY bookcase</button><button data-k="lack">LACK table</button><button data-k="marius">MARIUS stool</button><button data-k="gladom">GLADOM table</button></div>'
)

# 2. Adjust CSS for .seg.kit so 4 buttons fit cleanly in a 2x2 grid
src = src.replace(
    '.seg.kit button{flex:1}',
    '.seg.kit{display:grid;grid-template-columns:1fr 1fr;gap:3px}.seg.kit button{padding:0 6px;height:26px;font-size:11.5px}'
)

# 3. Guard Fs(e) against any mesh without position attribute
src = src.replace(
    'if(!s.isMesh||s.isInstancedMesh||s===y.BK.line||s===y.SR.mark||s===y.SL.mark)return;',
    'if(!s.isMesh||s.isInstancedMesh||!s.geometry||!s.geometry.attributes||!s.geometry.attributes.position||s===y.BK.line||s===y.SR.mark||s===y.SL.mark)return;'
)

# 4. Remove tracking script at line 35
src = re.sub(
    r'<script>\(function\(d\)\{if\(/(\^|\\.)sael\\\.net\$\.test\(location\.hostname\)\)\{.*?\}\)\("G-Q355EKBXDT"\);</script>',
    '<script>window.saelConsent=function(){};</script>',
    src,
    flags=re.DOTALL
)

# 5. Code for MARIUS and GLADOM
ADDITIONAL_KITS_CODE = r"""
// ==========================================
// BUILD 3: MARIUS STOOL (10135659)
// ==========================================
const mariusGroup = new l.Group;
mariusGroup.scale.setScalar(Ke);
jo.add(mariusGroup);
mariusGroup.visible = false;

const mariusRoot = { name: "stool", keys: [] };
const mariusPanels = [], mariusItems = [];
const mariusSeatMat = ye(new l.MeshStandardMaterial({ color: "#22252a", roughness: 0.44, envMapIntensity: 0.52 }));
const mariusLegMat = ye(new l.MeshStandardMaterial({ color: "#1e2126", roughness: 0.34, metalness: 0.28, envMapIntensity: 0.7 }));
const mariusFootMat = g("#141517", { roughness: 0.94 });

function addMariusPanel(name, pos, geom, mat) {
  const g = new l.Group;
  g.matrixAutoUpdate = false;
  mariusGroup.add(g);
  const m = new l.Mesh(geom, mat);
  m.castShadow = m.receiveShadow = true;
  g.add(m);
  const p = { name, num: "", g, c: w(...pos), keys: [], kind: "panel" };
  mariusPanels.push(p);
  return p;
}

// Seat: Perforated injection-molded plastic disc (dia 32cm, thick 2.2cm) with concentric holes and 4 underside screw bosses
const mariusSeatShape = new l.Shape();
mariusSeatShape.absarc(0, 0, 16.0, 0, Math.PI * 2, false);
function addSeatHole(x, y, r) {
  const hp = new l.Path();
  hp.absarc(x, y, r, 0, Math.PI * 2, true);
  mariusSeatShape.holes.push(hp);
}
addSeatHole(0, 0, 0.7);
for (let i = 0; i < 6; i++) {
  const a = i * Math.PI / 3;
  addSeatHole(Math.cos(a) * 4.8, Math.sin(a) * 4.8, 0.52);
}
for (let i = 0; i < 12; i++) {
  const a = i * Math.PI / 6;
  addSeatHole(Math.cos(a) * 8.8, Math.sin(a) * 8.8, 0.52);
}
for (let i = 0; i < 18; i++) {
  const a = i * Math.PI / 9;
  addSeatHole(Math.cos(a) * 12.8, Math.sin(a) * 12.8, 0.52);
}
const mariusSeatTopGeom = new l.ExtrudeGeometry(mariusSeatShape, {
  depth: 1.8,
  bevelEnabled: true,
  bevelThickness: 0.25,
  bevelSize: 0.25,
  curveSegments: 24
});
mariusSeatTopGeom.rotateX(-Math.PI / 2);
mariusSeatTopGeom.translate(0, 0.9, 0);

const mariusBossGeoms = [0, 1, 2, 3].map(i => {
  const a = i * Math.PI / 2 + Math.PI / 4;
  return new l.CylinderGeometry(1.2, 1.2, 1.2, 16).translate(Math.cos(a) * 10.5, -0.6, Math.sin(a) * 10.5);
});
const mariusSeatGeom = Ko([mariusSeatTopGeom.toNonIndexed(), ...mariusBossGeoms.map(bg => bg.toNonIndexed())]);
const mariusSeat = addMariusPanel("Seat", [0, 42.9, 0], mariusSeatGeom, mariusSeatMat);

pn(mariusSeat.g, [0, 1, 2, 3].map(i => {
  const a = i * Math.PI / 2 + Math.PI / 4;
  return [Math.cos(a) * 10.5, -1.2, Math.sin(a) * 10.5, 0, -1, 0, 0.4];
}));
mariusSeat.baseT = 0.001;
mariusSeat.exo = w(0, 18, 0);

// 4 Curved Tubular Legs with compound curve, center hub bracket, and top mounting tab
const mariusLegs = [];
for (let i = 0; i < 4; i++) {
  const ang = i * Math.PI / 2 + Math.PI / 4;
  const ca = Math.cos(ang), sa = Math.sin(ang);
  const pts = [
    new l.Vector3(ca * 18.5, 0.6, sa * 18.5),
    new l.Vector3(ca * 16.2, 8.0, sa * 16.2),
    new l.Vector3(ca * 10.0, 15.0, sa * 10.0),
    new l.Vector3(ca * 3.8,  20.0, sa * 3.8),
    new l.Vector3(ca * 5.8,  27.0, sa * 5.8),
    new l.Vector3(ca * 8.6,  36.0, sa * 8.6),
    new l.Vector3(ca * 10.5, 42.8, sa * 10.5)
  ];
  const curve = new l.CatmullRomCurve3(pts);
  const tube = new l.TubeGeometry(curve, 32, 0.92, 16, false);
  const foot = new l.CylinderGeometry(1.05, 1.05, 1.2, 16).translate(ca * 18.5, 0.6, sa * 18.5);
  const hubBracket = new l.BoxGeometry(2.2, 1.4, 2.2).translate(ca * 3.8, 20.0, sa * 3.8);
  const topTab = new l.BoxGeometry(2.6, 0.35, 3.2).translate(ca * 10.5, 42.8, sa * 10.5);

  const legMerged = Ko([tube.toNonIndexed(), foot.toNonIndexed(), hubBracket.toNonIndexed(), topTab.toNonIndexed()]);
  const leg = addMariusPanel("Leg " + (i + 1), [0, 0, 0], legMerged, mariusLegMat);

  pn(leg.g, [
    [ca * 3.8, 20.0, sa * 3.8, ca, 0, sa, 0.35],
    [ca * 10.5, 42.8, sa * 10.5, 0, 1, 0, 0.35]
  ]);
  leg.ca = ca; leg.sa = sa; leg.ang = ang;
  mariusLegs.push(leg);
}

// Hardware: 4x Bolt 104875 and 4x Screw 109566
const mariusHw = {
  bolt: { num: "104875", n: 4, name: "Bolt", items: [] },
  screw: { num: "109566", n: 4, name: "Screw", items: [] }
};

const mariusBoltGeom = He([
  [Sl([[0,0], [0.62,0], [0.62,0.18], [0.38,0.18], [0.38,1.6], [0,1.6]], 16), "#b0b4ba"],
  [new l.CylinderGeometry(0.2, 0.2, 0.1, 6).translate(0, 0.05, 0), "#303236"]
]);
mariusHw.bolt.mesh = new l.InstancedMesh(mariusBoltGeom, ws, 4);
mariusHw.bolt.mesh.castShadow = mariusHw.bolt.mesh.receiveShadow = true;
mariusHw.bolt.mesh.frustumCulled = false;
mariusGroup.add(mariusHw.bolt.mesh);

const mariusScrewGeom = He([
  [Sl([[0,0], [0.55,0], [0.55,0.2], [0.26,0.2], [0.26,2.2], [0,2.2]], 16), "#b8bcc2"]
]);
mariusHw.screw.mesh = new l.InstancedMesh(mariusScrewGeom, ws, 4);
mariusHw.screw.mesh.castShadow = mariusHw.screw.mesh.receiveShadow = true;
mariusHw.screw.mesh.frustumCulled = false;
mariusGroup.add(mariusHw.screw.mesh);

// Keyframes: Upside-down assembly on rug, then 180 flip upright
const mariusUpsideDown = ne([1,0,0],[0,-1,0],[0,0,-1]);
k(mariusRoot, 0, null, w(0, T + 44, -30), mariusUpsideDown);
k(mariusRoot, 2.04, null, w(0, T + 44, -30), mariusUpsideDown);
k(mariusRoot, 2.5, null, w(0, T + 41, -30), ne([1,0,0],[0,0,-1],[0,1,0]), { arc: 16 });
k(mariusRoot, 2.94, null, w(0, T, -30), B, { arc: 4 });

k(mariusSeat, 0, mariusRoot, mariusSeat.c, B);

// Legs initial placement on rug in the kit stage:
mariusLegs.forEach((leg, i) => {
  k(leg, 0, null, w(72 + (i % 2) * 22, T + 1.2, -68 + Math.floor(i / 2) * 36), ne([0,1,0],[1,0,0],[0,0,-1]));
  leg.exo = w(leg.ca * 14, -8, leg.sa * 14);
});

// Center sleeve bolts into 4-leg hub:
mariusLegs.forEach((leg, i) => {
  const bolt = { kind: "bolt", name: "Bolt", num: "104875", keys: [], i, hw: mariusHw.bolt };
  mariusHw.bolt.items.push(bolt);
  mariusItems.push(bolt);
  k(bolt, 0, null, w(-68 + (i % 2) * 8.5, T + 0.45, 12 + Math.floor(i / 2) * 8), oa);
  const tStart = 0.06 + i * 0.22;
  ke(bolt, tStart, tStart + 0.2, mariusRoot, w(leg.ca * 3.8, 20.0, leg.sa * 3.8), B, w(leg.ca * 4.0, 0, leg.sa * 4.0), { arc: 12, split: 0.45, spin1: 5 * Math.PI, lin: true });
  Z(bolt, 1, tStart, tStart + 0.08, tStart + 0.2);
  bolt.exo = w(0, -4, 0);
});

// Legs move to center cross assembly:
mariusLegs.forEach((leg, i) => {
  const tStart = 0.04 + i * 0.22;
  ke(leg, tStart, tStart + 0.21, mariusRoot, leg.c, B, w(leg.ca * 10, -6, leg.sa * 10), { arc: 22, split: 0.48, spin1: 2 * Math.PI, lin: true });
  Z(leg, 1, tStart, tStart + 0.1, tStart + 0.21);
});

// Screws initial placement & animation into underside seat bosses:
mariusLegs.forEach((leg, i) => {
  const screw = { kind: "screw", name: "Screw", num: "109566", keys: [], i, hw: mariusHw.screw };
  mariusHw.screw.items.push(screw);
  mariusItems.push(screw);
  k(screw, 0, null, w(-68 + (i % 2) * 8.5, T + 0.45, -18 + Math.floor(i / 2) * 8), oa);
  const tStart = 1.05 + i * 0.22;
  ke(screw, tStart, tStart + 0.2, mariusRoot, w(leg.ca * 10.5, 42.8, leg.sa * 10.5), B, w(0, -4.5, 0), { arc: 14, split: 0.42, spin1: 6 * Math.PI, lin: true });
  Z(screw, 2, tStart, tStart + 0.08, tStart + 0.2);
  screw.exo = w(0, -4, 0);
});

// Hardware cards on rug
const mariusCards = {
  screw: ia(27, 22, (e, t, o, n=4) => {
    e.fillStyle="#f6f3ec"; e.fillRect(0,0,t,o); e.fillStyle="#16171a"; e.font="500 64px Outfit, sans-serif";
    e.fillText(n+"x", 22, o-26); e.save(); e.translate(t-26, o-24); e.rotate(-Math.PI/2);
    e.font="500 30px Outfit, sans-serif"; e.fillText("109566", 0, 0); e.restore();
  }),
  bolt: ia(27, 22, (e, t, o, n=4) => {
    e.fillStyle="#f6f3ec"; e.fillRect(0,0,t,o); e.fillStyle="#16171a"; e.font="500 64px Outfit, sans-serif";
    e.fillText(n+"x", 22, o-26); e.save(); e.translate(t-26, o-24); e.rotate(-Math.PI/2);
    e.font="500 30px Outfit, sans-serif"; e.fillText("104875", 0, 0); e.restore();
  })
};
mariusCards.screw.position.set(-68, T + 0.03, -15);
mariusCards.bolt.position.set(-68, T + 0.03, 15);

// Steps for MARIUS
const mariusSteps = [
  { t: "What is in the box", pg: 1, box: [0.088, 0.067, 0.65, 0.167], d: 0, cam: { t: [0, 26, -30], yaw: -0.42, pitch: 0.46, dist: 12.5 } },
  { t: "Cross the four legs", pg: 2, box: [0.073, 0.048, 0.925, 0.465], kind: "bolt", d: 8, cam: { t: [0, 36, -30], yaw: -0.45, pitch: 0.52, dist: 9.0 } },
  { t: "Fasten legs to seat", pg: 2, box: [0.073, 0.473, 0.925, 0.680], kind: "screw", d: 8, cam: { t: [0, 42, -30], yaw: -0.45, pitch: 0.58, dist: 8.5 } },
  { t: "Turn upright on rug", pg: 3, box: [0.075, 0.060, 0.925, 0.890], d: 5, cam: { t: [0, 24, -30], yaw: -0.45, pitch: 0.35, dist: 10.5 } },
  { t: "Done (110 kg)", pg: 4, box: [0.095, 0.035, 0.910, 0.964], d: 4, cam: { t: [0, 22, -30], yaw: -0.48, pitch: 0.28, dist: 10.5 } }
];


// ==========================================
// BUILD 4: GLADOM TRAY TABLE (50411990)
// ==========================================
const gladomGroup = new l.Group;
gladomGroup.scale.setScalar(Ke);
jo.add(gladomGroup);
gladomGroup.visible = false;

const gladomRoot = { name: "table", keys: [] };
const gladomPanels = [], gladomItems = [];
const gladomMat = ye(new l.MeshStandardMaterial({ color: "#1c1e23", roughness: 0.36, metalness: 0.25, envMapIntensity: 0.72 }));

function addGladomPanel(name, pos, geom, mat=gladomMat) {
  const g = new l.Group;
  g.matrixAutoUpdate = false;
  gladomGroup.add(g);
  const m = new l.Mesh(geom, mat);
  m.castShadow = m.receiveShadow = true;
  g.add(m);
  const p = { name, num: "", g, c: w(...pos), keys: [], kind: "panel" };
  gladomPanels.push(p);
  return p;
}

// Removable Pressed-Steel Serving Tray: dia 44.8cm, recessed base, conical wall, rolled bead rim
const gladomTrayProfile = [
  [0, 0], [19.2, 0], [19.8, 0.1], [21.8, 3.0], [22.3, 3.4], [22.5, 3.3],
  [22.4, 2.9], [22.1, 2.7], [19.8, 0.35], [19.2, 0.25], [0, 0.25]
];
const gladomTrayGeom = Sl(gladomTrayProfile, 64);
const gladomTray = addGladomPanel("Tray top", [0, 51.5, 0], gladomTrayGeom);
gladomTray.baseT = 0.001;
gladomTray.exo = w(0, 18, 0);

// Upper Support Ring: radius 21.8cm, tube radius 0.62cm with 4 welded screw brackets
const ringTorus = new l.TorusGeometry(21.8, 0.62, 16, 64).rotateX(Math.PI / 2);
const ringTabs = [0, 1, 2, 3].map(i => {
  const a = i * Math.PI / 2;
  return new l.BoxGeometry(2.4, 0.3, 2.6).translate(Math.cos(a) * 21.8, -0.35, Math.sin(a) * 21.8);
});
const gladomRingGeom = Ko([ringTorus.toNonIndexed(), ...ringTabs.map(g => g.toNonIndexed())]);
const gladomRing = addGladomPanel("Upper ring", [0, 50.8, 0], gladomRingGeom);
pn(gladomRing.g, [0, 1, 2, 3].map(i => {
  const a = i * Math.PI / 2;
  return [Math.cos(a) * 21.8, -0.35, Math.sin(a) * 21.8, 0, -1, 0, 0.36];
}));
gladomRing.exo = w(0, 10, 0);

// Base Continuous Bent Tubular Scissor Frames A & B
function makeGladomUFrame(isFrameB) {
  const curve = new l.CurvePath();
  const r = 21.8, h = 50.8, cr = 4.0, yFloor = 0.65;
  curve.add(new l.LineCurve3(new l.Vector3(-r, h, 0), new l.Vector3(-r, yFloor + cr, 0)));
  curve.add(new l.QuadraticBezierCurve3(
    new l.Vector3(-r, yFloor + cr, 0),
    new l.Vector3(-r, yFloor, 0),
    new l.Vector3(-r + cr, yFloor, 0)
  ));
  curve.add(new l.LineCurve3(new l.Vector3(-r + cr, yFloor, 0), new l.Vector3(r - cr, yFloor, 0)));
  curve.add(new l.QuadraticBezierCurve3(
    new l.Vector3(r - cr, yFloor, 0),
    new l.Vector3(r, yFloor, 0),
    new l.Vector3(r, yFloor + cr, 0)
  ));
  curve.add(new l.LineCurve3(new l.Vector3(r, yFloor + cr, 0), new l.Vector3(r, h, 0)));

  const tubeGeom = new l.TubeGeometry(curve, 64, 0.62, 16, false);
  const tab1 = new l.BoxGeometry(2.4, 0.3, 2.6).translate(-r, h, 0);
  const tab2 = new l.BoxGeometry(2.4, 0.3, 2.6).translate(r, h, 0);
  const foot1 = new l.CylinderGeometry(0.85, 0.85, 0.5, 16).translate(-r, yFloor - 0.25, 0);
  const foot2 = new l.CylinderGeometry(0.85, 0.85, 0.5, 16).translate(r, yFloor - 0.25, 0);
  const centerNotch = new l.BoxGeometry(1.8, 0.4, 1.8).translate(0, yFloor + (isFrameB ? 0.3 : -0.1), 0);

  return Ko([
    tubeGeom.toNonIndexed(),
    tab1.toNonIndexed(),
    tab2.toNonIndexed(),
    foot1.toNonIndexed(),
    foot2.toNonIndexed(),
    centerNotch.toNonIndexed()
  ]);
}

const gladomFrameA = addGladomPanel("Frame A", [0, 0, 0], makeGladomUFrame(false));
pn(gladomFrameA.g, [[-21.8, 50.8, 0, 0, 1, 0, 0.35], [21.8, 50.8, 0, 0, 1, 0, 0.35]]);

const gladomFrameB = addGladomPanel("Frame B", [0, 0, 0], makeGladomUFrame(true));
pn(gladomFrameB.g, [[-21.8, 50.8, 0, 0, 1, 0, 0.35], [21.8, 50.8, 0, 0, 1, 0, 0.35]]);

// Hardware: 4x Screw 122202 with hex socket drive
const gladomHw = {
  screw: { num: "122202", n: 4, name: "Screw", items: [] }
};
const gladomScrewGeom = He([
  [Sl([[0,0], [0.52,0], [0.52,0.22], [0.26,0.22], [0.26,2.0], [0,2.0]], 16), "#b0b4ba"],
  [new l.CylinderGeometry(0.18, 0.18, 0.1, 6).translate(0, 0.05, 0), "#303236"]
]);
gladomHw.screw.mesh = new l.InstancedMesh(gladomScrewGeom, ws, 4);
gladomHw.screw.mesh.castShadow = gladomHw.screw.mesh.receiveShadow = true;
gladomHw.screw.mesh.frustumCulled = false;
gladomGroup.add(gladomHw.screw.mesh);

// Keyframes: Root stands on rug
k(gladomRoot, 0, null, w(0, T, -30), B);

// Frame A initial position & upright placement:
k(gladomFrameA, 0, null, w(54, T + 0.65, -58), ne([0,0,1],[1,0,0],[0,1,0]));
ke(gladomFrameA, 0.05, 0.42, gladomRoot, w(0, 0, 0), B, w(18, 12, -8), { arc: 20, split: 0.5 });
Z(gladomFrameA, 1, 0.05, 0.22, 0.42);

// Frame B initial position & crossing over Frame A at 90 deg:
k(gladomFrameB, 0, null, w(54, T + 0.65, 0), ne([0,0,1],[1,0,0],[0,1,0]));
ke(gladomFrameB, 0.45, 0.92, gladomRoot, w(0, 0, 0), ne([0,0,1],[0,1,0],[-1,0,0]), w(18, 14, 8), { arc: 24, split: 0.5 });
Z(gladomFrameB, 1, 0.45, 0.68, 0.92);

// Upper Ring lifts and seats onto top frame tabs:
k(gladomRing, 0, null, w(0, T + 0.65, -76), B);
ke(gladomRing, 1.05, 1.45, gladomRoot, gladomRing.c, B, w(0, 16, 0), { arc: 22, split: 0.45 });
Z(gladomRing, 2, 1.05, 1.25, 1.45);

// Screws 122202 into 4 top brackets:
const gladomScrewPos = [[-21.8, 50.8, 0], [21.8, 50.8, 0], [0, 50.8, -21.8], [0, 50.8, 21.8]];
gladomScrewPos.forEach((pos, i) => {
  const screw = { kind: "screw", name: "Screw", num: "122202", keys: [], i, hw: gladomHw.screw };
  gladomHw.screw.items.push(screw);
  gladomItems.push(screw);
  k(screw, 0, null, w(-70 + (i % 2) * 8.5, T + 0.45, -24 + Math.floor(i / 2) * 8), oa);
  const tStart = 1.45 + i * 0.13;
  ke(screw, tStart, tStart + 0.18, gladomRoot, w(...pos), B, w(0, 4.5, 0), { arc: 12, split: 0.42, spin1: 6 * Math.PI, lin: true });
  Z(screw, 2, tStart, tStart + 0.07, tStart + 0.18);
  screw.exo = w(0, 4, 0);
});

// Removable Tray lifts high in arc and nests inside top ring:
k(gladomTray, 0, null, w(-56, T + 0.3, -30), B);
ke(gladomTray, 2.05, 2.85, gladomRoot, gladomTray.c, B, w(-20, 28, 0), { arc: 35, split: 0.55 });
Z(gladomTray, 3, 2.05, 2.45, 2.85);

// Step 4 demo: Tray lifts off slightly (6 cm) to show serving function, then settles:
ke(gladomTray, 3.1, 3.5, gladomRoot, w(0, 57.5, 0), B, w(0, 6, 0), { arc: 8, split: 0.5 });
ke(gladomTray, 3.55, 3.9, gladomRoot, gladomTray.c, B, w(0, -6, 0), { arc: 6, split: 0.5 });

// Hardware card for GLADOM
const gladomCards = {
  screw: ia(27, 22, (e, t, o, n=4) => {
    e.fillStyle="#f6f3ec"; e.fillRect(0,0,t,o); e.fillStyle="#16171a"; e.font="500 64px Outfit, sans-serif";
    e.fillText(n+"x", 22, o-26); e.save(); e.translate(t-26, o-24); e.rotate(-Math.PI/2);
    e.font="500 30px Outfit, sans-serif"; e.fillText("122202", 0, 0); e.restore();
  })
};
gladomCards.screw.position.set(-70, T + 0.03, -20);

// Steps for GLADOM
const gladomSteps = [
  { t: "What is in the box", pg: 1, box: [0.058, 0.053, 0.69, 0.154], d: 0, cam: { t: [0, 28, -30], yaw: -0.44, pitch: 0.44, dist: 13.5 } },
  { t: "Interlock frame legs", pg: 4, box: [0.148, 0.237, 0.95, 0.98], d: 7, cam: { t: [0, 26, -30], yaw: -0.42, pitch: 0.38, dist: 11.5 } },
  { t: "Attach upper ring", pg: 5, box: [0.083, 0.108, 0.93, 0.638], kind: "screw", d: 8, cam: { t: [0, 48, -30], yaw: -0.45, pitch: 0.56, dist: 9.8 } },
  { t: "Place removable tray", pg: 6, box: [0.073, 0.041, 0.90, 0.808], d: 6, cam: { t: [0, 38, -30], yaw: -0.46, pitch: 0.40, dist: 12.0 } },
  { t: "Done", pg: 7, box: [0.230, 0.041, 0.77, 0.762], d: 4, cam: { t: [0, 32, -30], yaw: -0.48, pitch: 0.32, dist: 11.5 } }
];
"""

# Insert ADDITIONAL_KITS_CODE right before const ar=[{t:
idx_ar = src.find('const ar=[{t:')
if idx_ar == -1:
    idx_ar = src.find('ar=[{t:')
assert idx_ar != -1, "Could not find ar= definition"
src = src[:idx_ar] + ADDITIONAL_KITS_CODE + "\n" + src[idx_ar:]

# 6. Update yt object to include marius and gladom
NEW_YT_ENTRIES = r""",
marius:{
  id:"marius",name:"THE KIT",title:"MARIUS",
  sub:"The real IKEA manual for the MARIUS stool: curved steel legs, four bolts and four screws. Built in 3D exactly as shown.",
  N:4,steps:mariusSteps,spreads:[[0,1],[2,3],[4,0]],
  hots:mariusSteps.map((e,t)=>({pg:e.pg,box:e.box,step:t,label:t?"Step "+t:"The kit"})),
  camEnd:{t:[0,22,-30],yaw:-.48,pitch:.28,dist:10.5},
  kindN:{screw:4,bolt:4},hw:mariusHw,
  hwList:[["screw","109566",4,"Screw"],["bolt","104875",4,"Bolt"]],
  items:mariusItems,panels:mariusPanels,cards:mariusCards,
  dir:"manual/marius/",ar:1241/875,hwTotal:8,panelTotal:5,ghostOff:[2.0,2.5],group:mariusGroup,
  tags:[["Perforated seat",[0,T+2.2,-30]],["4 tubular steel legs",[72,T+2.5,-45]],["4 screws & 4 bolts",[-68,T,0],"#ffb454"]],
  words(e){
    const bs=`<b>${kn("bolt")}</b> of 4 in`, ss=`<b>${kn("screw")}</b> of 4 in`;
    switch(e){
      case 0:return'A round perforated seat, four curved steel legs, four sleeve bolts (<span class="a">104875</span>) and four screws (<span class="a">109566</span>). Max load 110 kg. Lay the seat face down on something soft.';
      case 1:return`Cross the four legs at the center hub and insert the four sleeve bolts. ${bs}.`;
      case 2:return`Align the legs with the seat bosses and drive home all four screws. ${ss}.`;
      case 3:return'Turn the stool upright onto its rubber feet. Check all four touch the floor evenly.';
      default:return'Done: 34 \xD7 34 \xD7 45 cm. Stackable, sturdy, rated to 110 kg.';
    }
  },
  book:["MARIUS assembly instructions","AA-302068-12 \xB7 4 pages \xB7 as printed by IKEA","https://www.ikea.com/nl/nl/assembly_instructions/marius-kruk-zwart__AA-302068-12-2.pdf","2024"]
},
gladom:{
  id:"gladom",name:"THE KIT",title:"GLADOM",
  sub:"The real IKEA manual for the GLADOM tray table: interlocking tubular steel frame, upper ring and removable tray. Built in 3D step by step.",
  N:4,steps:gladomSteps,spreads:[[0,1],[2,3],[4,5],[6,7],[8,0]],
  hots:gladomSteps.map((e,t)=>({pg:e.pg,box:e.box,step:t,label:t?"Step "+t:"The kit"})),
  camEnd:{t:[0,32,-30],yaw:-.48,pitch:.32,dist:11.5},
  kindN:{screw:4},hw:gladomHw,
  hwList:[["screw","122202",4,"Screw"]],
  items:gladomItems,panels:gladomPanels,cards:gladomCards,
  dir:"manual/gladom/",ar:1754/1241,hwTotal:4,panelTotal:4,ghostOff:[2.2,2.8],group:gladomGroup,
  tags:[["Removable serving tray",[-56,T+2,-30]],["Tubular base frame",[54,T+2,-30]],["Upper support ring",[0,T+1,-76]],["4 screws",[-70,T,-20],"#ffb454"]],
  words(e){
    const s=`<b>${kn("screw")}</b> of 4 in`;
    switch(e){
      case 0:return'A pressed-steel removable tray, two folding tubular frame sections, an upper ring and four screws (<span class="a">122202</span>). An Allen key is included.';
      case 1:return'Open the two frame sections and interlock them at 90\xB0 at the center joint to form a rigid four-point base.';
      case 2:return`Seat the top support ring onto the four frame brackets and fasten each with a screw. ${s}.`;
      case 3:return'Lower the removable tray top into the ring; the raised lip keeps it centered.';
      default:return'Done: 45 \xD7 45 \xD7 53 cm. The tray lifts clear for serving and wipe-down.';
    }
  },
  book:["GLADOM assembly instructions","AA-2544925-1 \xB7 8 pages \xB7 as printed by IKEA","https://www.ikea.com/nl/nl/assembly_instructions/gladom-salontafel-met-dienblad-zwart__AA-2544925-1-2.pdf","2024"]
}
"""

target_str = 'lack-side-table-white__AA-2606170-1-100.pdf","2025"]}'
idx_lack_close = src.find(target_str)
assert idx_lack_close != -1, "Could not find LACK book string"
idx_end_bracket = idx_lack_close + len(target_str)
src = src[:idx_end_bracket] + NEW_YT_ENTRIES + src[idx_end_bracket:]

# 7. Add cards to Dt.cards
src = src.replace(
    'ie=yt.billy,Dt.cards.add(ca.screw);',
    'ie=yt.billy,Dt.cards.add(ca.screw),Dt.cards.add(mariusCards.screw),Dt.cards.add(mariusCards.bolt),Dt.cards.add(gladomCards.screw);'
)

# 8. Update On(e) switching logic to show/hide mariusGroup and gladomGroup
src = src.replace(
    'Ct.visible=e==="lack";',
    'Ct.visible=e==="lack";mariusGroup.visible=e==="marius";gladomGroup.visible=e==="gladom";'
)

# 9. Update URL hash update in On(e)
src = src.replace(
    'location.pathname+location.search+(e==="lack"?"#lack":"")',
    'location.pathname+location.search+(e==="billy"?"":"#"+e)'
)

# 10. Add interactive raycasting hover (so) for marius and gladom meshes
ADD_SO_CODE = r"""
for(const e of mariusPanels)e.g.traverse(t=>{t.isMesh&&!t.isInstancedMesh&&so(t,"panel",{o:e})});
so(mariusHw.screw.mesh,"hw",{k:"screw"});so(mariusHw.bolt.mesh,"hw",{k:"bolt"});
for(const e of gladomPanels)e.g.traverse(t=>{t.isMesh&&!t.isInstancedMesh&&so(t,"panel",{o:e})});
so(gladomHw.screw.mesh,"hw",{k:"screw"});
"""
idx_so_lack = src.find('so(lt.screw.mesh,"hw",{k:"screw"})')
assert idx_so_lack != -1, "Could not find so(lt.screw.mesh) call"
idx_after_so = src.find(';', idx_so_lack) + 1
src = src[:idx_after_so] + ADD_SO_CODE + src[idx_after_so:]

# 11. Update keyboard shortcut 'k' to cycle through all kits
src = src.replace(
    'else if(t==="k")On(ie.id==="billy"?"lack":"billy"),bt(ie.title);',
    'else if(t==="k"){const ids=Object.keys(yt);On(ids[(ids.indexOf(ie.id)+1)%ids.length]);bt(ie.title);}'
)

# 12. Support ?kit=, ?step= and #hash on boot
src = src.replace(
    'location.hash==="#lack"&&On("lack")',
    '(()=>{const p=new URLSearchParams(location.search).get("kit");const pStep=new URLSearchParams(location.search).get("step");if(p&&yt[p.toLowerCase()]){On(p.toLowerCase());if(pStep!==null&&!isNaN(+pStep))In(+pStep);return;}const h=location.hash?location.hash.replace("#","").toLowerCase():"";if(h&&yt[h]){On(h);if(pStep!==null&&!isNaN(+pStep))In(+pStep);return;}if(pStep!==null&&!isNaN(+pStep))In(+pStep);})()'
)

# 13. Expose yt, ie, On, and active objects to window
src = src.replace(
    'window.__dbg=()=>',
    'window.yt=yt,window.ie=()=>ie,window.On=On,window.__dbg=()=>'
)

# Write output to OUT_PATH and ROOT_PATH
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(src)
print(f"Wrote {len(src)} bytes to {OUT_PATH}")

with open(ROOT_PATH, "w", encoding="utf-8") as f:
    f.write(src)
print(f"Wrote {len(src)} bytes to {ROOT_PATH}")
