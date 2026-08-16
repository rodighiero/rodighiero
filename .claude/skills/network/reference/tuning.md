# Network tuning constants

Every knob, what it does, and which file owns it. Changing any of these means a full
`KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py`.

## Link rule and geometry — `scripts/layout-network.js`

This file is the single source of truth for both. The link rule lives here (not in the
Python) because the layout is what consumes it.

| Constant | Default | What it decides |
|---|---|---|
| `MUTUAL_K` | 2 | a pair is linked only if each ranks the other in its top-K |
| `STRONG_SIM` | 0.65 | floor for a reciprocal (backbone) edge |
| `FALLBACK_SIM` | 0.60 | floor for the single rescue edge given to an unreciprocated node; kept **below** `STRONG_SIM` so these stay a distinct weaker tier (drawn at reduced opacity, flagged `fb`) |
| `NODE_RADIUS` | 3 | marker radius, fixed px in the live view |
| `NODE_SPACING` | 18 | collide radius — marker/click separation, not label legibility |
| `MIN_NODE_GAP` | `2·R + 4` | node–node overlap relaxed to this in the deterministic pass |
| `EDGE_CLEARANCE` | `R + 6` | a marker may not come this close to an edge it does not end |
| `EDGE_CLEAR_STRENGTH` | 0.4 | share of the shortfall applied per tick, as a force |
| `EDGE_CLEAR_PASSES` | 60 | cap on the deterministic sweeps that finish the job |
| `EDGE_CLEAR_EPSILON` | 0.05 | overshoot per nudge, so float noise doesn't re-report the same offender |
| `CHARGE_STRENGTH` | −280 | repulsion |
| `CHARGE_DISTANCE_MAX` | 520 | repulsion cutoff |
| `GRAVITY` | 0.9 | pull toward the well |
| `LINK_DIST_BASE` / `LINK_DIST_SPAN` | 10 / 38 | edge length as a function of similarity |
| `LAYOUT_SEED` | random per run | why every rebuild produces a full diff; recorded as `seed` in the JSON |
| `LAYOUT_TICKS` | 1400 | simulation length |
| `ANCHOR` | `center` | one gravity well, so clusters settle as islands. `ring` centres the largest component and pins the rest on a perimeter — wrong for this many-small-components graph, which it scatters into a halo |
| `CANVAS_W` / `CANVAS_H` | 564 / 564 | the stage's own square, so the client's fit is 1:1 on desktop and everything baked in px is drawn at the size it was measured at |
| `FIT_MARGIN` | 40 | label headroom — a hovered two-line title reaches ~37px above its node |

The clearance is enforced **twice**: as a force during the simulation (which clears most
seeds on its own) and as a deterministic pass **after** fit-normalization, since a uniform
scale under 1 shrinks the distance to a line as surely as the distance between markers.
Each sweep nudges, clamps inside the margin box, relaxes any overlap it created, and
measures again. The build prints `node/edge clearance: N at settle, M after K pass(es)`;
`M` must be 0.

## Text pipeline and embeddings — `scripts/build-network.py`

| Constant | Default | Notes |
|---|---|---|
| `MODEL_NAME` | `Alibaba-NLP/gte-base-en-v1.5` | 768-dim |
| `MAX_SEQ_LENGTH` | 8192 | long enough that full-text articles embed whole rather than truncated |
| `DEVICE` | `cpu` | override with `NETWORK_DEVICE` |
| `EXCERPT_SEPARATOR` | `<!--more-->` | lead/abstract marker in full-text bodies |
| `RELATED_K` | 3 | suggestions per publication page |
| `OPUS_MODELS` | fr, it | per-`lang` offline MT into the English space; add a code to support a new source language |
| `TRANS_CACHE_PATH` | `scripts/.translation-cache.json` | gitignored, keyed by model + source text |
| `CACHE_PATH` | `scripts/.embedding-cache.npz` | gitignored |
| `_TRANS_CHARS` | 1200 | per-chunk char budget, under the 512-token MT window |

Scrubbing before embedding strips footnotes, bibliographies, headings, links, inline code,
HTML, Liquid, blockquote markers, emphasis, and every parenthetical aside, plus leftover
list markers. **Figure captions are deliberately kept** — they carry real content.

## Clusters — `scripts/build-network.py`

| Constant | Default | Notes |
|---|---|---|
| `MIN_CLUSTER_SIZE` | 3 | counted in **original** works on the mutual backbone; translations never count |
| `CLUSTER_TERMS` | 3 | keywords kept per cluster; `label` is `terms[0]` |
| `_CLUSTER_STOP` | — | English/French/Italian stopwords for the TF-IDF labelling |

Labels are TF-IDF unigrams plus a recurring bigram when both its words are top terms.
`anchor_slug` is the first work at or below the cluster's span midpoint — the gallery tile
the card renders just before.

## Miniatures — `scripts/build-network.py`, `write_preview_svgs()`

| Constant | Default | Mirrors |
|---|---|---|
| `PREVIEW_NODE_R` | 3.0 | live `NODE_RADIUS` |
| `PREVIEW_LINK_STROKE` / `PREVIEW_NODE_STROKE` | 0.5 | live link stroke |
| `PREVIEW_TRANS_STROKE` / `PREVIEW_TRANS_DASH` | 0.9 / `3 2.5` | the dashed translation edge |
| `PREVIEW_FALLBACK_OPACITY` | 0.5 | the weaker `fb` tier |
| `PREVIEW_DIM_OPACITY` | 0.5 | everything outside a cluster, as `.filtered-out` |
| `PREVIEW_INK` | `currentColor` | why the tiles invert in night mode — and why they must be inlined, not `<img>` |
| `PREVIEW_NODE_FILL` | `var(--bg, #fff)` | so links never show through markers |
| `PREVIEW_MARGIN` | 18 | keeps edge nodes off the viewBox border |

The viewBox is framed on the node **barycentre** — each axis extends symmetrically to
whichever side reaches further — so the centre of mass lands in the middle of the tile.
The frame is computed over **all** nodes in every miniature, which is what keeps the cards
reading as small multiples of one map.

## Rejected, don't re-derive

- Title-only and body-only embeddings — both tested, both worse than title + full text.
- A multilingual embedding model — rejected in favour of MT into one English space.
- `ANCHOR: ring` — see above.
