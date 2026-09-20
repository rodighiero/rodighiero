# Network tuning constants

Every knob, what it does, and which file owns it. Changing any of these means a full
`KMP_DUPLICATE_LIB_OK=TRUE uv run scripts/build-network.py`.

## Link rule and geometry — `scripts/layout-network.js`

This file is the single source of truth for both. The link rule lives here (not in the
Python) because the layout is what consumes it.

| Constant | Default | What it decides |
|---|---|---|
| `MUTUAL_K` | 2 | a pair is linked only if each ranks the other in its top-K |
| `STRONG_SIM` | 0.65 | floor for a reciprocal (backbone) edge |
| `FALLBACK_SIM` | 0.60 | floor for the single rescue edge given to an unreciprocated node; kept **below** `STRONG_SIM` so these stay a distinct weaker tier (drawn at reduced opacity, flagged `fb`) |
| `NODE_RADIUS` | 3 | marker radius, fixed px in the live view |
| `NODE_SPACING` | 10 | collide radius — marker/click separation, not label legibility. Must stay **below** the link rest lengths and **above** half the page's hit circle: at 18 it was the binding constraint and the whole cloud jammed into a hexagonal crystal (see the note below) |
| `MIN_NODE_GAP` | `2·R + 4` | node–node overlap relaxed to this in the deterministic pass |
| `EDGE_CLEARANCE` | `R + 6` | a marker may not come this close to an edge it does not end |
| `EDGE_CLEAR_STRENGTH` | 0.4 | share of the shortfall applied per tick, as a force |
| `EDGE_CLEAR_PASSES` | 60 | cap on the deterministic sweeps that finish the job |
| `EDGE_CLEAR_EPSILON` | 0.05 | overshoot per nudge, so float noise doesn't re-report the same offender |
| `LAYOUT_ATTEMPTS` | 12 | bakes drawn from fresh scatters; the cleanest is kept (see below). Raise it only if crossings start surviving |
| `CHARGE_STRENGTH` | −280 | repulsion |
| `CHARGE_DISTANCE_MAX` | 520 | repulsion cutoff |
| `GRAVITY` | 0.45 | pull toward the well. Above ~0.6 it overpowers the link force and every edge is drawn at the same length |
| `LINK_DIST_BASE` / `LINK_DIST_SPAN` | 10 / 38 | edge length as a function of similarity |
| `LAYOUT_TICKS` | 1400 | simulation length |
| `ANCHOR` | `center` | one gravity well, so clusters settle as islands. `ring` centres the largest component and pins the rest on a perimeter — wrong for this many-small-components graph, which it scatters into a halo |
| `CANVAS_W` / `CANVAS_H` | 564 / 564 | the stage's own square, so the client's fit is 1:1 on desktop and everything baked in px is drawn at the size it was measured at |
| `FIT_MARGIN` | 40 | label headroom — a hovered two-line title reaches ~37px above its node |

**Edge crossings are selected away, not repaired.** Two edges that cross read as a junction
between publications that have no edge — the same misreading `EDGE_CLEARANCE` exists to stop
for a node resting on a stranger's line. But there is no local repair: uncrossing two edges
means walking whole components past each other. So `layout-network.js` bakes the arrangement
up to `LAYOUT_ATTEMPTS` times from fresh scatters, counts residual incidences and crossings on
each, and keeps the best — clearance first, then crossings — stopping early on a clean one.
Only the scatter-dependent half repeats; the link rule, the components and the anchors are
computed once. The build prints `edge crossings: N in the layout kept, chosen from M bake(s)`
and warns if `N` is non-zero. On the current corpus a single bake is crossing-free about five
times in six, so `M` is usually 1 and rarely above 3; an `M` that starts climbing means the
graph is getting hard to draw flat, not that the constant is too low.

**Keep the layout amorphous.** `NODE_SPACING` and `GRAVITY` decide together whether node
*position* carries any information, and the failure is quiet: with spacing at 18 and gravity
at 0.9, collide was the binding constraint and 67 equal disks pressed into one well jammed
into hexagonal close packing — every node exactly 59px from its neighbours, every edge drawn
at that same length, so a linked pair was indistinguishable from an unlinked one. It looks
tidy, which is why it survived. Measure it rather than eyeballing it: take each node's bond
angles to its nearest neighbours mod 60° and compute the circular order parameter. Near 1 is
a crystal, near 0 is amorphous; the retune took it from 0.99 to ~0.11. Both knobs are needed
— dropping spacing alone unjams the packing but leaves edge length pinned to the spacing.

The clearance is enforced **twice**: as a force during the simulation (which clears most
starting scatters on its own) and as a deterministic pass **after** fit-normalization, since a uniform
scale under 1 shrinks the distance to a line as surely as the distance between markers.
Each sweep nudges, clamps inside the margin box, relaxes any overlap it created, and
measures again. The build prints `node/edge clearance: N at settle, M after K pass(es)`;
`M` must be 0.

Four of these constants are **shipped to the page** in `network.json`'s `params`:
`NODE_RADIUS` (which the view draws its markers at) and `MUTUAL_K` / `STRONG_SIM` /
`FALLBACK_SIM` (which the network view's legend quotes, via Liquid). Retuning any of them
therefore updates the page by itself — there is no copy in `_layouts/home.html` to chase.
The change still needs a rebuild to reach the JSON.

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

`order_cluster_cards()` then sorts the array into the order the cards run down the
homepage: by the cluster's **median original member**, newest first. `slugs` is already
year-descending, so that is the middle one — no averaging, and a Forthcoming work stays
newest instead of dropping out of the arithmetic; translations are skipped for the same
reason `size` skips them. The sort is stable, so two clusters whose middle work shares a
year keep the size order `id` was assigned in.

The homepage owns the *spacing* and reads nothing but this order — it emits one card
every `publications / (clusters + 1)` entries. Reordering the array therefore moves the
cards; it does **not** renumber anything, since `id` (and so `cluster:<id>`, the `?cluster=`
URLs and `network-cluster-<id>.svg`) is assigned by size before this sort runs.

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
