#!/usr/bin/env node
/*
 * Precompute the home network view's force-directed layout.
 *
 * Reads {nodes, similarity} as JSON on stdin and writes
 * {seed, canvas, positions, links} as JSON on stdout, running the d3-force
 * simulation offline so the home page can draw the graph already settled.
 * The seed is randomized per build, so every run produces a fresh arrangement
 * (re-run to reroll); the settled cloud is then normalized to fit the canvas
 * with a uniform margin, so any seed yields a balanced, non-overflowing layout.
 *
 * Invoked automatically at the end of scripts/build-network.py. Standalone:
 *     node scripts/layout-network.js < _data/network.json
 *
 * The layout constants below are the single source of truth for the graph
 * geometry. _layouts/home.html only fit-scales these positions into the live
 * stage and draws the baked links; it no longer owns any layout math. Keep
 * NODE_RADIUS / STRONG_SIM in sync between the two (the layout bakes them here;
 * the page reuses NODE_RADIUS for drawing only).
 */
'use strict';

const path = require('path');
// d3 is a build-time dependency only — this script is the last thing that uses it,
// for d3-force. The page itself draws the baked result with plain DOM calls, which is
// why the library lives here beside its one consumer rather than in js/, where it
// would be published to readers who never load it.
const d3 = require(path.resolve(__dirname, 'vendor', 'd3.v7.min.js'));

// ── Layout constants (formerly in _layouts/home.html) ──
const NODE_RADIUS = 3;
// Collide radius = NODE_RADIUS + NODE_SPACING. Labels render only on hover (one
// at a time, plus a selection's neighbors), so this spacing governs marker/
// click separation, not label legibility — kept tight enough that linked nodes
// pull into visibly distinct cluster knots rather than a uniform blob.
const NODE_SPACING = 18;
// Node–edge clearance. A marker is filled with the page background and drawn
// over the link layer, so a node resting on an edge knocks that line out on
// both sides — which is exactly what a junction looks like, and the node then
// reads as connected to two publications it has no edge to. So no marker may
// come within EDGE_CLEARANCE of a segment it does not end: the marker itself
// plus its hover ring (NODE_RADIUS + 2), plus room to read as clear of it.
// The clearance is held twice — as a force during the simulation, which lets
// the arrangement settle around it, and as a deterministic pass afterwards,
// which guarantees it (see below: the pass runs after the fit, since a uniform
// scale under 1 shrinks every gap the force had won).
const EDGE_CLEARANCE = NODE_RADIUS + 6;
const EDGE_CLEAR_STRENGTH = 0.4;   // share of the shortfall applied per tick
const EDGE_CLEAR_PASSES = 60;      // cap on the sweeps that finish the job
// Overshoot of each repair, in px: a sweep that moves a node to exactly the
// clearance leaves it on the boundary, where float noise re-reports it as an
// incidence and the sweeps trade it back and forth until the cap. A hair past
// converges instead, and survives the 2-decimal rounding of the output.
const EDGE_CLEAR_EPSILON = 0.05;
// Floor on centre-to-centre distance in those sweeps: nudging a node off an
// edge must not park it on another node. Far below the simulation's collide
// radius (NODE_RADIUS + NODE_SPACING) — this is the marker-overlap floor, not
// the spacing that shapes the cloud.
const MIN_NODE_GAP = 2 * NODE_RADIUS + 4;
const CHARGE_STRENGTH = -280;
const STRONG_SIM = 0.65;
// Mutual k-nearest-neighbor: an English node pair is linked only when each
// ranks the other within its top MUTUAL_K most-similar English neighbors (and
// the similarity clears STRONG_SIM). This makes every similarity edge
// reciprocal — no one-sided "nearest neighbor" links — and lets a node carry
// more than one edge, so genuine clusters form. A handful of nodes with no
// reciprocated neighbor are left unconnected by design.
const MUTUAL_K = 2;
// Nearest-neighbor fallback: an English node that the mutual-kNN rule leaves
// with no edge at all (and that is not tied to a translation) is given a single
// edge to its most-similar English neighbor, but only if that similarity
// clears FALLBACK_SIM — so a publication similar to nothing stays honestly
// isolated rather than collecting a spurious link. These rescue edges are
// one-directional and weaker than the reciprocal backbone, so they are flagged
// (`fb`) and drawn at reduced opacity by the page. Kept below STRONG_SIM so the
// fallback forms a distinct weaker tier (a rescue link just above FALLBACK_SIM
// is faint, while the reciprocal backbone clears the higher STRONG_SIM), not a
// back door into the backbone: it relaxes both mutuality and the floor, but
// only for a node that would otherwise be isolated.
const FALLBACK_SIM = 0.60;
const GRAVITY = 0.9;
// Randomized per build: each run produces a fresh arrangement (re-run to
// reroll). The settled cloud is normalized to fit the canvas afterwards, so
// any seed yields a usable, non-overflowing layout. The seed used is printed
// to stderr and stored in the output as `seed` for reference.
const LAYOUT_SEED = (Math.random() * 0x100000000) >>> 0;
const LAYOUT_TICKS = 1400;
// Link-distance shaping (forceLink): distance = LINK_DIST_BASE + (1−sim)*LINK_DIST_SPAN.
const LINK_DIST_BASE = 10;
const LINK_DIST_SPAN = 38;
const CHARGE_DISTANCE_MAX = 520;
// Component-anchoring strategy: 'center' (all nodes share one gravity well) or
// 'ring' (largest component centred, others pinned around it on a perimeter
// ring). The mutual-kNN graph is many small components with no dominant hub, so
// 'ring' scatters the singletons into a perimeter halo — 'center' lets clusters
// settle as islands with unconnected nodes filling the gaps.
const ANCHOR = 'center';

// Canonical stage the layout is baked into — a square two grid columns wide,
// which is exactly what `.stage` now measures: 2 × --card-w (270) + --card-gap
// (24). Because the card width is the constant and the page is sized to its
// grid, that is 564 px at every column count the view is reachable at, so the
// client's fit-scale is 1:1 on a desktop and markers, labels and the clearance
// below all keep the size they were baked at. A square frame also spends the
// stage on the graph rather than on the empty bands a wide canvas left above
// and below it when fitted into a tall box.
const CANVAS_W = 564;
const CANVAS_H = 564;
// Uniform margin kept clear on every side when the settled layout is
// normalized to fit the canvas. It is also the page's label headroom: a title
// renders above its node (two lines reach y = −25 plus the ascent), so a node
// at the top edge needs ~37px of canvas above it to keep its label inside the
// stage. The margin is baked in here, which is why the client centres the
// canvas and adds nothing of its own.
const FIT_MARGIN = 40;

function readStdin() {
  return new Promise(function (resolve, reject) {
    let buf = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', function (c) { buf += c; });
    process.stdin.on('end', function () { resolve(buf); });
    process.stdin.on('error', reject);
  });
}

function main(input) {
  const data = JSON.parse(input);
  const pubs = data.nodes;
  const sim = data.similarity;
  const N = pubs.length;

  // Translations: index → original index. They lay out as regular nodes but
  // their sole edge is a forced 1.00 link to their original, and they are never
  // a similarity-link candidate for anyone else (so an original links to its
  // strongest distinct neighbor, not to its own translation).
  const isTrans = new Array(N).fill(false);
  const transOf = new Array(N).fill(-1);
  if (data.translations) {
    Object.keys(data.translations).forEach(function (k) {
      const t = +k;
      isTrans[t] = true;
      transOf[t] = data.translations[k];
    });
  }

  // Seeded RNG — identical LCG to the former makeRng() in home.html.
  let s = LAYOUT_SEED >>> 0;
  function rand() { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }

  // Nodes, seeded in index order (each consumes rand() x then y), same as the
  // browser's seedPosition() but against the canonical canvas.
  const nodes = pubs.map(function (p, i) {
    const n = { i: i };
    n.x = CANVAS_W / 2 + (rand() - 0.5) * Math.min(CANVAS_W, CANVAS_H) * 0.6;
    n.y = CANVAS_H / 2 + (rand() - 0.5) * Math.min(CANVAS_W, CANVAS_H) * 0.6;
    n.vx = 0; n.vy = 0;
    return n;
  });

  // ── buildLinks: the core network uses mutual k-nearest-neighbor edges over
  // all original works (English + non-English originals, which share one
  // embedding space). For each original we rank the other originals by
  // similarity; a pair (i, j) is linked only when j is within i's top MUTUAL_K
  // AND i is within j's top MUTUAL_K, and sim clears STRONG_SIM. This keeps
  // every similarity edge reciprocal and lets a node carry several edges, so
  // real clusters emerge. A node whose top picks never reciprocate would stay
  // unconnected, so a nearest-neighbor fallback (see below) then gives each
  // such node one weaker edge to its strongest match above FALLBACK_SIM —
  // unless it is similar to nothing, in which case it stays isolated by design.
  // Translations do not take part in this similarity search: each gets a forced
  // 1.00 link to its original instead (a cross-language edge is otherwise drawn
  // just like a native one). ──
  const seen = new Set();
  const links = [];
  function add(i, j, v, fb) {
    const key = i < j ? i + ':' + j : j + ':' + i;
    if (seen.has(key)) return;
    seen.add(key);
    const link = { source: i, target: j, value: v };
    if (fb) link.fb = true;   // nearest-neighbor fallback edge (drawn fainter)
    links.push(link);
  }
  // Per-original ranking of the other originals, most similar first.
  const topK = new Array(N).fill(null);
  for (let i = 0; i < N; i++) {
    if (isTrans[i]) continue;
    const cands = [];
    for (let j = 0; j < N; j++) {
      if (i === j || isTrans[j]) continue;
      cands.push(j);
    }
    cands.sort(function (a, b) { return sim[i][b] - sim[i][a]; });
    topK[i] = cands.slice(0, MUTUAL_K);
  }
  for (let i = 0; i < N; i++) {
    if (isTrans[i]) { add(i, transOf[i], 1); continue; }
    topK[i].forEach(function (j) {
      if (sim[i][j] <= STRONG_SIM) return;      // similarity floor
      if (topK[j] && topK[j].indexOf(i) !== -1)  // reciprocated?
        add(i, j, sim[i][j]);
    });
  }

  // ── Nearest-neighbor fallback ──
  // Any original still carrying no edge (no reciprocated mutual neighbor, and
  // not attached to a translation) is linked to its single most-similar
  // neighbor when that similarity clears FALLBACK_SIM. Degree counts
  // every edge added so far (mutual + forced translation edges), so a node that
  // is already visibly connected — including via a dashed translation edge — is
  // not rescued. degree is updated as we go, so two mutually-isolated nodes that
  // pick each other share one edge and neither collects a second.
  const degree = new Array(N).fill(0);
  links.forEach(function (l) { degree[l.source]++; degree[l.target]++; });
  for (let i = 0; i < N; i++) {
    if (isTrans[i] || degree[i] > 0) continue;
    let best = -1, bestSim = -Infinity;
    for (let j = 0; j < N; j++) {
      if (i === j || isTrans[j]) continue;
      if (sim[i][j] > bestSim) { bestSim = sim[i][j]; best = j; }
    }
    if (best !== -1 && bestSim > FALLBACK_SIM) {
      add(i, best, sim[i][best], true);
      degree[i]++; degree[best]++;
    }
  }

  // ── Component anchoring targets (uses link indices; run before forceLink) ──
  const adj = Array.from({ length: N }, function () { return []; });
  links.forEach(function (l) { adj[l.source].push(l.target); adj[l.target].push(l.source); });
  const comp = new Array(N).fill(-1);
  let c = 0;
  for (let i = 0; i < N; i++) {
    if (comp[i] !== -1) continue;
    const stack = [i];
    while (stack.length) {
      const x = stack.pop();
      if (comp[x] !== -1) continue;
      comp[x] = c;
      adj[x].forEach(function (y) { if (comp[y] === -1) stack.push(y); });
    }
    c++;
  }
  const groups = Array.from({ length: c }, function () { return []; });
  comp.forEach(function (cc, i) { groups[cc].push(i); });
  groups.sort(function (a, b) { return b.length - a.length; });
  const targets = new Array(N);
  const cy0 = CANVAS_H * 0.45;
  if (ANCHOR === 'center') {
    // Single shared gravity well: every node is pulled to the same centre and
    // charge/collide spread them into one balanced cloud. Linked nodes cohere
    // via forceLink into islands; unconnected nodes fill the gaps rather than
    // being exiled to a perimeter ring. Suits a many-small-components graph
    // (mutual-kNN) where there is no single dominant hub.
    for (let i = 0; i < N; i++) targets[i] = { x: CANVAS_W / 2, y: cy0 };
  } else {
    // Ring anchoring: the largest component sits at the centre, every other
    // component is pinned around it on a ring. Suits one big hub + a few
    // satellites; degrades to a scattered halo when components are many.
    (groups[0] || []).forEach(function (i) { targets[i] = { x: CANVAS_W / 2, y: cy0 }; });
    const numSatellites = Math.max(1, groups.length - 1);
    const r = Math.min(CANVAS_W, CANVAS_H) * 0.25;
    for (let k = 1; k < groups.length; k++) {
      const angle = (k - 1) / numSatellites * 2 * Math.PI - Math.PI / 2;
      const cx = CANVAS_W / 2 + Math.cos(angle) * r;
      const cy = cy0 + Math.sin(angle) * r;
      groups[k].forEach(function (i) { targets[i] = { x: cx, y: cy }; });
    }
  }

  // ── Node–edge incidences ──
  // Walk every (node, edge) pair where the node is not one of the edge's two
  // ends and lies closer to it than EDGE_CLEARANCE, calling `visit` with the
  // unit vector pointing off the segment and the shortfall to make up. Returns
  // the count, so the same walk both measures and repairs. Reads positions
  // live, which is what lets the repair pass re-check its own work.
  function edgeIncidences(visit) {
    let count = 0;
    for (let k = 0; k < links.length; k++) {
      const si = links[k].source, ti = links[k].target;
      const a = nodes[si], b = nodes[ti];
      const dx = b.x - a.x, dy = b.y - a.y;
      const len2 = dx * dx + dy * dy;
      if (len2 < 1e-9) continue;               // degenerate segment: nothing to clear
      for (let i = 0; i < N; i++) {
        if (i === si || i === ti) continue;
        const n = nodes[i];
        const t = ((n.x - a.x) * dx + (n.y - a.y) * dy) / len2;
        if (t < 0 || t > 1) continue;          // off the end: collide governs there
        let ox = n.x - (a.x + t * dx), oy = n.y - (a.y + t * dy);
        let d = Math.sqrt(ox * ox + oy * oy);
        if (d >= EDGE_CLEARANCE) continue;
        if (d < 1e-6) {                        // exactly on the line: take its normal,
          const len = Math.sqrt(len2);         // so the direction is not seed noise
          ox = -dy / len; oy = dx / len;
        } else { ox /= d; oy /= d; }
        count++;
        if (visit) visit(n, a, b, ox, oy, EDGE_CLEARANCE - d, t);
      }
    }
    return count;
  }

  // The force half: push the node off the line, and let the segment yield half
  // as much, split between its ends by where along it the node sits — so a long
  // edge bows away rather than the node alone having to find room.
  function forceEdgeClear(alpha) {
    const k = EDGE_CLEAR_STRENGTH * alpha;
    edgeIncidences(function (n, a, b, ox, oy, short, t) {
      const f = short * k;
      n.vx += ox * f; n.vy += oy * f;
      a.vx -= ox * f * 0.5 * (1 - t); a.vy -= oy * f * 0.5 * (1 - t);
      b.vx -= ox * f * 0.5 * t;       b.vy -= oy * f * 0.5 * t;
    });
  }

  // forceLink mutates link.source/target into node refs — give it a copy so the
  // emitted `links` keep their integer indices.
  const simLinks = links.map(function (l) { return { source: l.source, target: l.target, value: l.value }; });

  const simulation = d3.forceSimulation(nodes)
    .alphaDecay(0.005)
    .force('link', d3.forceLink(simLinks).id(function (d) { return d.i; })
      .distance(function (d) { return LINK_DIST_BASE + (1 - d.value) * LINK_DIST_SPAN; })
      .strength(function (d) { return 0.5 + d.value * 0.5; }))
    .force('charge', d3.forceManyBody().strength(CHARGE_STRENGTH).distanceMax(CHARGE_DISTANCE_MAX))
    .force('x', d3.forceX(function (d) { return targets[d.i].x; }).strength(GRAVITY))
    .force('y', d3.forceY(function (d) { return targets[d.i].y; }).strength(GRAVITY))
    .force('collide', d3.forceCollide().radius(NODE_RADIUS + NODE_SPACING))
    .force('edgeClear', forceEdgeClear)
    .stop();
  for (let i = 0; i < LAYOUT_TICKS; i++) simulation.tick();

  // Normalize the settled cloud to fit the canvas with a uniform margin, so
  // every (randomized) seed yields a balanced, non-overflowing layout. Uniform
  // scale preserves the shape; the translation centers it. The page then
  // fit-scales this canvas into the live stage as before.
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  nodes.forEach(function (n) {
    if (n.x < minX) minX = n.x;
    if (n.x > maxX) maxX = n.x;
    if (n.y < minY) minY = n.y;
    if (n.y > maxY) maxY = n.y;
  });
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);
  const fit = Math.min((CANVAS_W - 2 * FIT_MARGIN) / spanX, (CANVAS_H - 2 * FIT_MARGIN) / spanY);
  const tx = (CANVAS_W - spanX * fit) / 2 - minX * fit;
  const ty = (CANVAS_H - spanY * fit) / 2 - minY * fit;
  nodes.forEach(function (n) { n.x = n.x * fit + tx; n.y = n.y * fit + ty; });

  // ── Node–edge clearance, guaranteed ──
  // The force above shapes the arrangement around the clearance while the
  // simulation is warm, but it is one force among several, it fades with alpha,
  // and the fit just applied rescales every gap it won (a uniform scale under 1
  // shrinks the distance to a line as surely as the distance between markers).
  // So the invariant is established here, in the units the page will draw:
  // sweep the incidences, move each offender straight out to the clearance,
  // keep it inside the margin box and off its neighbours, then measure again —
  // a nudge can create the next incidence, which is why this iterates instead
  // of sweeping once. A node in a pocket too dense to free is left where it is
  // and counted, rather than the map being distorted to satisfy a constant.
  const clearAtSettle = edgeIncidences(null);
  let clearPasses = 0;
  for (; clearPasses < EDGE_CLEAR_PASSES; clearPasses++) {
    let moved = 0;
    edgeIncidences(function (n, a, b, ox, oy, short) {
      const step = short + EDGE_CLEAR_EPSILON;
      n.x += ox * step; n.y += oy * step;
      moved++;
    });
    if (!moved) break;
    nodes.forEach(function (n) {
      n.x = Math.max(FIT_MARGIN, Math.min(CANVAS_W - FIT_MARGIN, n.x));
      n.y = Math.max(FIT_MARGIN, Math.min(CANVAS_H - FIT_MARGIN, n.y));
    });
    for (let i = 0; i < N; i++) {          // one relaxation sweep at the
      for (let j = i + 1; j < N; j++) {    // marker-overlap floor
        const p = nodes[i], q = nodes[j];
        let dx = q.x - p.x, dy = q.y - p.y;
        let d = Math.sqrt(dx * dx + dy * dy);
        if (d >= MIN_NODE_GAP) continue;
        if (d < 1e-6) { dx = 1; dy = 0; d = 1; }   // coincident: split along x
        const push = (MIN_NODE_GAP - d) / d / 2;
        p.x -= dx * push; p.y -= dy * push;
        q.x += dx * push; q.y += dy * push;
      }
    }
  }
  const clearRemaining = edgeIncidences(null);

  const positions = nodes.map(function (n) {
    return [Math.round(n.x * 100) / 100, Math.round(n.y * 100) / 100];
  });

  process.stdout.write(JSON.stringify({
    seed: LAYOUT_SEED,
    // Reported by build-network.py beside the seed: stderr here is captured and
    // shown only on failure, so what the build should say travels in the result.
    clearance: { atSettle: clearAtSettle, remaining: clearRemaining, passes: clearPasses },
    canvas: { w: CANVAS_W, h: CANVAS_H },
    positions: positions,
    links: links,
  }));
}

readStdin().then(main).catch(function (err) {
  process.stderr.write(String(err && err.stack || err) + '\n');
  process.exit(1);
});
