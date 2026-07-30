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
const d3 = require(path.resolve(__dirname, '..', 'js', 'd3.v7.min.js'));

// ── Layout constants (formerly in _layouts/home.html) ──
const NODE_RADIUS = 3;
// Collide radius = NODE_RADIUS + NODE_SPACING. Labels render only on hover (one
// at a time, plus a selection's neighbours), so this spacing governs marker/
// click separation, not label legibility — kept tight enough that linked nodes
// pull into visibly distinct cluster knots rather than a uniform blob.
const NODE_SPACING = 18;
const CHARGE_STRENGTH = -280;
const STRONG_SIM = 0.60;
// Mutual k-nearest-neighbour: an English node pair is linked only when each
// ranks the other within its top MUTUAL_K most-similar English neighbours (and
// the similarity clears STRONG_SIM). This makes every similarity edge
// reciprocal — no one-sided "nearest neighbour" links — and lets a node carry
// more than one edge, so genuine clusters form. A handful of nodes with no
// reciprocated neighbour are left unconnected by design.
const MUTUAL_K = 2;
// Nearest-neighbour fallback: an English node that the mutual-kNN rule leaves
// with no edge at all (and that is not tied to a translation) is given a single
// edge to its most-similar English neighbour, but only if that similarity
// clears FALLBACK_SIM — so a publication similar to nothing stays honestly
// isolated rather than collecting a spurious link. These rescue edges are
// one-directional and weaker than the reciprocal backbone, so they are flagged
// (`fb`) and drawn at reduced opacity by the page. Set to the STRONG_SIM floor:
// the fallback relaxes the *mutuality* requirement, not the similarity floor.
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

// Canonical stage the layout is baked into. Approximates a desktop `.stage`
// box: body max-width 1200 − 2×1.5rem padding → 1152 content; the network grid
// gives the stage 3 of 4 columns (≈ 856 px wide); height ≈ 80vh − 9rem on a
// typical viewport. The client fit-scales these coords into the real stage, so
// at a desktop size the scale stays ≈ 1 and markers/labels keep their rhythm.
const CANVAS_W = 856;
const CANVAS_H = 600;
// Uniform margin kept clear on every side when the settled layout is
// normalized to fit the canvas.
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
  // strongest distinct neighbour, not to its own translation).
  const isTrans = new Array(N).fill(false);
  const transOf = new Array(N).fill(-1);
  if (data.translations) {
    Object.keys(data.translations).forEach(function (k) {
      const t = +k;
      isTrans[t] = true;
      transOf[t] = data.translations[k];
    });
  }

  // Non-English publications are never embedded (the similarity network is
  // English-only), so their similarity row is all zeros — they are never a
  // link source or candidate for anyone else. They still take part in the
  // layout as regular nodes (see isTrans above for translation duplicates).
  const isNonEnglish = pubs.map(function (p) { return (p.lang || 'en') !== 'en'; });

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

  // ── buildLinks: the core network is English-only and uses mutual k-nearest-
  // neighbour edges. For each English node we rank the other English nodes by
  // similarity; a pair (i, j) is linked only when j is within i's top MUTUAL_K
  // AND i is within j's top MUTUAL_K, and sim clears STRONG_SIM. This keeps
  // every similarity edge reciprocal and lets a node carry several edges, so
  // real clusters emerge. A node whose top picks never reciprocate would stay
  // unconnected, so a nearest-neighbour fallback (see below) then gives each
  // such node one weaker edge to its strongest match above FALLBACK_SIM —
  // unless it is similar to nothing, in which case it stays isolated by design.
  // Non-English publications are then attached on top: a translation gets a
  // forced 1.00 link to its original; any other non-English original does not
  // search for a match at all and stays unconnected. ──
  const seen = new Set();
  const links = [];
  function add(i, j, v, fb) {
    const key = i < j ? i + ':' + j : j + ':' + i;
    if (seen.has(key)) return;
    seen.add(key);
    const link = { source: i, target: j, value: v };
    if (fb) link.fb = true;   // nearest-neighbour fallback edge (drawn fainter)
    links.push(link);
  }
  // Per-English-node ranking of the other English nodes, most similar first.
  const topK = new Array(N).fill(null);
  for (let i = 0; i < N; i++) {
    if (isNonEnglish[i] || isTrans[i]) continue;
    const cands = [];
    for (let j = 0; j < N; j++) {
      if (i === j || isNonEnglish[j] || isTrans[j]) continue;
      cands.push(j);
    }
    cands.sort(function (a, b) { return sim[i][b] - sim[i][a]; });
    topK[i] = cands.slice(0, MUTUAL_K);
  }
  for (let i = 0; i < N; i++) {
    if (isTrans[i]) { add(i, transOf[i], 1); continue; }
    if (isNonEnglish[i]) continue;
    topK[i].forEach(function (j) {
      if (sim[i][j] <= STRONG_SIM) return;      // similarity floor
      if (topK[j] && topK[j].indexOf(i) !== -1)  // reciprocated?
        add(i, j, sim[i][j]);
    });
  }

  // ── Nearest-neighbour fallback ──
  // Any English node still carrying no edge (no reciprocated mutual neighbour,
  // and not attached to a translation) is linked to its single most-similar
  // English neighbour when that similarity clears FALLBACK_SIM. Degree counts
  // every edge added so far (mutual + forced translation edges), so a node that
  // is already visibly connected — including via a dashed translation edge — is
  // not rescued. degree is updated as we go, so two mutually-isolated nodes that
  // pick each other share one edge and neither collects a second.
  const degree = new Array(N).fill(0);
  links.forEach(function (l) { degree[l.source]++; degree[l.target]++; });
  for (let i = 0; i < N; i++) {
    if (isNonEnglish[i] || isTrans[i] || degree[i] > 0) continue;
    let best = -1, bestSim = -Infinity;
    for (let j = 0; j < N; j++) {
      if (i === j || isNonEnglish[j] || isTrans[j]) continue;
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

  const positions = nodes.map(function (n) {
    return [Math.round(n.x * 100) / 100, Math.round(n.y * 100) / 100];
  });

  process.stdout.write(JSON.stringify({
    seed: LAYOUT_SEED,
    canvas: { w: CANVAS_W, h: CANVAS_H },
    positions: positions,
    links: links,
  }));
}

readStdin().then(main).catch(function (err) {
  process.stderr.write(String(err && err.stack || err) + '\n');
  process.exit(1);
});
