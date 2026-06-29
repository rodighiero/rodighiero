#!/usr/bin/env node
/*
 * Precompute the home network view's force-directed layout.
 *
 * Reads {nodes, similarity} as JSON on stdin and writes
 * {canvas, positions, links} as JSON on stdout. It reuses the EXACT same
 * d3-force configuration, seed, and constants the browser used to run at
 * render time, so the baked positions are identical to what _layouts/home.html
 * produced live — only now they are computed once, offline.
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
const NODE_SPACING = 24;
const CHARGE_STRENGTH = -280;
const STRONG_SIM = 0.70;
const GRAVITY = 1.2;
const LAYOUT_SEED = 1;
const LAYOUT_TICKS = 1400;

// Canonical stage the layout is baked into. Approximates a desktop `.stage`
// box: body max-width 1200 − 2×1.5rem padding → 1152 content; the network grid
// gives the stage 3 of 4 columns (≈ 856 px wide); height ≈ 80vh − 9rem on a
// typical viewport. The client fit-scales these coords into the real stage, so
// at a desktop size the scale stays ≈ 1 and markers/labels keep their rhythm.
const CANVAS_W = 856;
const CANVAS_H = 600;

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

  // ── buildLinks: each node's single strongest neighbour, but only if that
  // best similarity clears STRONG_SIM — otherwise the node is left unconnected.
  // Translation nodes instead get a forced 1.00 link to their original. ──
  const seen = new Set();
  const links = [];
  function add(i, j, v) {
    const key = i < j ? i + ':' + j : j + ':' + i;
    if (seen.has(key)) return;
    seen.add(key);
    links.push({ source: i, target: j, value: v });
  }
  for (let i = 0; i < N; i++) {
    if (isTrans[i]) { add(i, transOf[i], 1); continue; }
    let bestJ = -1, bestS = -Infinity;
    for (let j = 0; j < N; j++) {
      if (i === j || isTrans[j]) continue;
      if (sim[i][j] > bestS) { bestS = sim[i][j]; bestJ = j; }
    }
    if (bestJ >= 0 && bestS > STRONG_SIM) add(i, bestJ, bestS);
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
  const numComp = Math.max.apply(null, comp) + 1;
  const groups = Array.from({ length: numComp }, function () { return []; });
  comp.forEach(function (cc, i) { groups[cc].push(i); });
  groups.sort(function (a, b) { return b.length - a.length; });
  const targets = new Array(N);
  const cy0 = CANVAS_H * 0.45;
  (groups[0] || []).forEach(function (i) { targets[i] = { x: CANVAS_W / 2, y: cy0 }; });
  const numSatellites = Math.max(1, groups.length - 1);
  const r = Math.min(CANVAS_W, CANVAS_H) * 0.25;
  for (let k = 1; k < groups.length; k++) {
    const angle = (k - 1) / numSatellites * 2 * Math.PI - Math.PI / 2;
    const cx = CANVAS_W / 2 + Math.cos(angle) * r;
    const cy = cy0 + Math.sin(angle) * r;
    groups[k].forEach(function (i) { targets[i] = { x: cx, y: cy }; });
  }

  // forceLink mutates link.source/target into node refs — give it a copy so the
  // emitted `links` keep their integer indices.
  const simLinks = links.map(function (l) { return { source: l.source, target: l.target, value: l.value }; });

  const simulation = d3.forceSimulation(nodes)
    .alphaDecay(0.005)
    .force('link', d3.forceLink(simLinks).id(function (d) { return d.i; })
      .distance(function (d) { return 15 + (1 - d.value) * 45; })
      .strength(function (d) { return 0.5 + d.value * 0.5; }))
    .force('charge', d3.forceManyBody().strength(CHARGE_STRENGTH).distanceMax(520))
    .force('x', d3.forceX(function (d) { return targets[d.i].x; }).strength(GRAVITY))
    .force('y', d3.forceY(function (d) { return targets[d.i].y; }).strength(GRAVITY))
    .force('collide', d3.forceCollide().radius(NODE_RADIUS + NODE_SPACING))
    .stop();
  for (let i = 0; i < LAYOUT_TICKS; i++) simulation.tick();

  const positions = nodes.map(function (n) {
    return [Math.round(n.x * 100) / 100, Math.round(n.y * 100) / 100];
  });

  process.stdout.write(JSON.stringify({
    canvas: { w: CANVAS_W, h: CANVAS_H },
    positions: positions,
    links: links,
  }));
}

readStdin().then(main).catch(function (err) {
  process.stderr.write(String(err && err.stack || err) + '\n');
  process.exit(1);
});
