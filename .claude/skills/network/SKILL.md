---
name: network
description: Every operation on the publication similarity network — the graph behind the homepage network view, the research-cluster cards, and the "Related publications" list on each publication page. Use for rebuilding after publications change, rewording cluster cards, retuning link/layout/cluster parameters, regenerating the SVG miniatures, inspecting _data/network.json, or debugging a cluster that shifted, an orphan include, or an overlapping node.
---

# The network object

One artifact — **`_data/network.json`** (committed) — feeds three surfaces:

| Surface | Reads |
|---|---|
| Homepage network view (`_layouts/home.html`) | `nodes` (baked `x`/`y`), `links`, `canvas` |
| Homepage research-cluster cards | `clusters` (+ `_includes/network-cluster-<id>.svg`) |
| "Related publications" on each publication page (`_layouts/publication.html`) | each node's `related` |

Nothing is computed in the browser. The page only fit-scales baked coordinates.

## Schema of `_data/network.json`

```
seed     — the layout RNG seed of the run that produced these positions
canvas   — {w, h}; 564×564, the stage's own square (layout-network.js CANVAS_W/H)
nodes[]  — {i, slug, title, url, lang, related[3], x, y}
links[]  — {source, target, value}  (+ forced/fb flags where applicable)
clusters[] — {id, label, terms, slugs, year_start, year_end, span, size,
              anchor_slug, action, title, description, filter_label}
```

`nodes` / `links` are index-parallel to the DOM elements the view builds once and never re-renders. The similarity matrix is deliberately **not** shipped.

`clusters[].label`/`terms`/`slugs`/`years`/`size`/`anchor_slug` are **structural** (build-network.py); `title`/`description`/`filter_label` are **editorial** (build-cards.py).

## The two commands

```bash
# Full rebuild — embeddings, translation, similarity, layout, clusters, SVGs,
# then invokes build-cards.py at the end. Needs Node on PATH. Minutes.
KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py

# Card text only — model-free, reads and rewrites the same network.json. Instant.
python3 scripts/build-cards.py
```

Never hand-edit `_data/network.json`; it is generated output. Edit the script that produces the field, then rerun.

## Operations

### Rebuild after publications changed
Adding, removing or editing the body of any publication invalidates the graph. Run the full rebuild. Embeddings and translations are cached (`scripts/.embedding-cache.npz`, `scripts/.translation-cache.json`, both gitignored), so only changed texts are recomputed.

Then check, before committing:
- cluster count and labels (`python3 -c "import json;d=json.load(open('_data/network.json'));print([c['label'] for c in d['clusters']])"`);
- that every label still has a `CLUSTER_CARDS` key in `scripts/build-cards.py` — a shifted label silently falls back to auto text;
- the build's `node/edge clearance: N at settle, M after K pass(es)` line — `M` must be 0;
- `git status` for new/deleted `_includes/network-cluster-*.svg` (stale ones are auto-deleted).

**The layout seed is random per run**, so a rebuild moves every node even when nothing changed. Expect a large diff in `network.json` and in every SVG; that is normal, not a bug. Don't rebuild "to check" — rebuild when the inputs changed.

### Reword a cluster card
Edit the `CLUSTER_CARDS` table in `scripts/build-cards.py`, keyed on the cluster's auto `label`, then run `python3 scripts/build-cards.py` alone. Each entry is a `title` (the subject, as a name), a two-sentence `description` (what the work does to it, then why it matters), and an optional `filter` chip. Ground the text in the cluster's mutual core, not in its TF-IDF terms.

### Retune links, layout, or clusters
See `reference/tuning.md` for every constant, what it controls, and which file owns it. The rule that matters: **`scripts/layout-network.js` is the single source of truth for the link rule and the geometry**; `build-network.py` owns the text pipeline, the clusters, and the SVG miniatures. Any retune is a full rebuild.

### Regenerate the miniatures
They are written by `write_preview_svgs()` inside the full rebuild — there is no separate command, by design: a card must never show a different map than the view behind it. They are `_includes/` (not `images/`) and inlined so `currentColor` and the night toggle reach them.

### Add a source language
Add the `lang` code → opus-mt model to `OPUS_MODELS` in `build-network.py`, then rebuild. A non-English **original** is machine-translated into the English embedding space and competes as a first-class similarity node; a **translation** (`translation_of` in its front matter) borrows its source's vector and gets the forced dashed edge instead.

## Invariants — don't break these

- A **translation** is never embedded or ranked; it is attached to its original by a forced edge only.
- `related` picks the representative work **before** ranking, never deduplicates after — two vectors that are the same point cannot be ordered, and a translation displaced its own original when the order was reversed.
- Cluster **qualification** runs on the mutual backbone alone (fallback `fb` edges dropped, translations not counted toward `MIN_CLUSTER_SIZE`); **membership** is only then broadened along fallback edges and translations.
- The similarity matrix stays build-time. Don't write it to `network.json`.
- Miniatures are a true reduction of the live view: the `PREVIEW_*` constants mirror the live values, and the frame is computed over **all** nodes so the tiles stay registered with each other.

## Troubleshooting

| Symptom | Cause |
|---|---|
| A cluster card shows auto text | its `label` shifted; rekey the `CLUSTER_CARDS` entry |
| A cluster vanished | membership fell below `MIN_CLUSTER_SIZE` originals on the mutual backbone |
| Orphan `network-cluster-N.svg` | shouldn't happen (stale files are deleted); if it does, check `PREVIEW_CLUSTER_GLOB` |
| A node sits on a stranger's edge | `EDGE_CLEARANCE` pass failed — the build prints the residual count |
| Miniature is black in night mode | it got referenced as `<img>` instead of inlined through the card's `media` slot |
| Build fails at the layout step | Node missing from PATH (`scripts/layout-network.js` + vendored d3) |

Homepage/gallery behaviour that merely *consumes* the network (stage sizing, `--cols`, filters, view transitions) lives in `_layouts/home.html` and is documented in CLAUDE.md — not here.
