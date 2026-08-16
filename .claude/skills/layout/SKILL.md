---
name: layout
description: Every operation on _layouts/home.html, the homepage — the gallery grid and its masonry, the column arithmetic that sizes the whole page, the card system and the special/action/cluster tiles, the search and filter pipeline, the tile and view-switch motion, and the bio collapse. Use for retuning card width or gutters, adding or rewording an action card, changing what is searchable or filterable, adjusting the spring easing or the scroll behaviour, fixing a layout that overflows or a toggle that gets painted over, or working out why a tile jumps instead of sliding. It is the homepage layout only — _layouts/publication.html is a separate file this skill does not cover.
---

# The layout object

`_layouts/home.html` is the only top-level publications page. It has two view modes,
toggled in the search bar and persisted in `localStorage` under `publicationView`:

| View | What it is |
|---|---|
| **gallery** | custom JS masonry — newest first, packed by shortest column |
| **network** | the publication similarity graph (data and geometry: see the `network` skill) |

A third **list** view was removed; cards no longer carry an abstract/`.card-desc` at all.

## The one idea

**The card width is the constant and everything else follows from it** — the column count,
the page's own width, the header, the footer, the network stage. There are no hand-picked
breakpoints. `--card-w` (270px), `--card-gap` (24px) and `--page-gutter` (32px) are declared
once in `_includes/styles-base.css` and read at runtime by the masonry
(`CARD_W`/`GAP_X`/`PAGE_PAD`, via `getComputedStyle`) rather than copied into it, so
retuning a card is a one-place edit that every other block picks up on its own.

`syncPageWidth()` sizes `document.body` to exactly what the current column count spans and
publishes that count as **`--cols`** (the number to compute with) and **`data-cols`** (the
hook for rules that cannot compute) on `<body>`.

Full arithmetic, thresholds and the per-block grids: `reference/grid.md`.

## Where things live

| Concern | File |
|---|---|
| Markup, all JS, page-specific CSS | `_layouts/home.html` |
| Tokens, `.card*`, `.authors`, `.card-meta`, mode toggle | `_includes/styles-base.css` |
| Every card's markup (publication, action, cluster) | `_includes/card-action.html`, `_includes/card-meta.html` |
| Manual action cards | `_data/home_cards.yml` |
| Cluster cards + graph miniatures | `_data/network.json`, `_includes/network-*.svg` (generated) |
| Bio prose | `README.md` (via `_plugins/system_readme.rb`) |
| Spring curve generator | `scripts/spring-easing.js` |

## Operations

### Retune the card, the gap or the gutter
Edit the token in `styles-base.css` — nothing else copies it. Two consequences to carry
through by hand: the `_mobile_max` Liquid assign at the top of `home.html` is
`gridWidth(3) + PAGE_PAD - 1`, so it moves whenever `--page-gutter` does; and
`--page-gutter` is a **sum**, not a taste — redo it if you touch the toggle, its inset,
the icon or the focus ring. Both are worked out in `reference/grid.md`.

### Add or reword an action card
Append to `_data/home_cards.yml`: `label`, `action`, optional `year` / `eyebrow` / `venue` /
`sublabel`, optional `pin: first`. `action` is `view:<gallery|network>`, `type:<publication-type>`
or `search:<terms>`. **Research-cluster cards are not edited here** — they are generated from
`network.json`; reword them in `scripts/build-cards.py` (see the `network` skill).
Card anatomy and the filter pipeline: `reference/cards.md`.

### Change what is searchable or filterable
The haystack is each card's `data-search` attribute, built in the Liquid loop; the three
content filters (`?q=`, `?type=`, `?cluster=`) are mutually exclusive and all run through
one `applySearch`. Adding a field means adding it to `data-search` and, if it should be
filterable on its own, giving the card a `data-*` attribute the way `data-type` works.

### Retune the motion
`node scripts/spring-easing.js` prints the CSS `linear()` curves to paste into
`_layouts/home.html`. It writes nothing — the point is that a retune is a parameter change
rather than a hand-tweaked list of numbers. Which mechanism runs when, and what is
deliberately cut rather than animated: `reference/motion.md`.

### Touch the bio collapse
`.bio-shell` is the collapsing wrapper; the state is one attribute (`data-bio-visible`) on
`<html>`, persisted under `bioVisible` and restored before first paint. **At rest the
collapse holds no measurement** — open is `height: auto`, closed is 0. A pixel height
exists only during the travel, pinned by `setBioVisible` and handed back on `transitionend`
*and* `transitioncancel`. See the invariant below before changing any of that.

### Work on the network view
Stage sizing, `--cols` and the filter fade live here; the graph's data, layout, clusters and
miniatures live in the `network` skill. The seam: this page only **fit-scales** baked
coordinates into the stage (uniform scale + centre, fixed-px markers and labels, re-fit on
resize) and draws the baked links — no simulation runs in the browser.

It is drawn with **plain DOM calls** — `createElementNS` for the SVG, `setAttribute` for the
geometry, `classList.toggle` for highlight/filter state — and no library. It builds once on
first open and is never re-rendered: the nodes and links come baked out of `build-network.py`
and never change identity, so `nodeEls` / `labelEls` / `linkEls` stay index-parallel to
`nodes` / `links` and an index is the only lookup anything needs. Only coordinates move (on a
re-fit) and classes toggle. Keep it that way — a keyed data-join earned its place only while
the browser ran the force simulation and the graph really did change; once the layout moved
offline it was ceremony over a one-time build, and D3 was a 93KB-gzipped dependency for
`select`/`attr`/`classed`.

## Invariants — don't break these

- **Measure `document.documentElement.clientWidth`, never `window.innerWidth`.** The latter
  counts a classic scrollbar as page width, and the grid then overhangs the body by exactly
  the scrollbar's width — a horizontal scrollbar on the whole page.
- **The 921px boundary is asked for as a `matchMedia` query**, not by measuring `innerWidth`,
  so the JS runs the identical test the CSS does. A media query excludes the scrollbar and
  `innerWidth` includes it; in the band between the two answers the view toggle would be
  hidden with the network still live — a reader stuck in a view with no way out.
- **The 921 literal is written once**, as `{% assign _mobile_max = 921 %}`, and interpolated
  into all three consumers (the pre-paint `<head>` script, the `@media` rule, the
  `matchMedia` call).
- **The bio collapse must not store its open height.** The header's height *is* a function
  of the column count, so any remeasure races a layout that already changed shape and a
  stale number clips the bio under its own `overflow`. `auto` cannot go stale.
- **A gallery filter change must not use a view transition.** It rasterises the live page,
  so a tile in flight becomes a *picture* of a card cross-fading against a snapshot — which
  is how a large photograph dropped out of its tile mid-slide.
- **The tile transition is armed only while a change is in flight** (`.animating` on
  `#publications`). The first layout and the no-op resize passes write transforms too, and
  those must stay instant.
- **`.card-title` is `display: inline-block`** and that is load-bearing: an inline-block's
  top margin does not collapse with the meta line's bottom margin, so `display: block` would
  halve the gap.
- **The action/filter tile's hairline is an inset `box-shadow`**, not a border — a border
  eats 1px of content width per side that a publication card keeps, sitting the two kinds on
  slightly different inner grids.
- **Cluster miniatures are inlined**, never `<img>`: an `<img>` is an isolated document that
  can see neither `currentColor` nor the site's manual night toggle.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Horizontal scrollbar on the whole page | something measured `innerWidth` instead of `clientWidth` |
| Mode toggle painted over by the filter bar | content escaping `--page-gutter`; both carry `z-index: 10` and the bar is later in the DOM |
| Header collapses to one full-width column | the `minmax(min(var(--card-w), 100%), 1fr)` form was changed, or the body stopped being grid-sized |
| Footer wider than the page at one column | `grid-column: -3 / -1` with no second-to-last line; the `data-cols="1"` rule is missing |
| Network view live with no toggle visible | the JS boundary test drifted from the CSS one — use `matchMedia` |
| Network stage stuck at 4 columns | the `setView` network branch didn't call `syncPageWidth()` itself (`layoutMasonry()` must not run there) |
| A tile jumps instead of sliding | it travelled further than `window.innerHeight` (class `snapping`), or the column count crossed the one-column boundary, or the pass shortened the page under the reader |
| Tiles restart on every keystroke | `SEARCH_SETTLE` (180 ms) debounce lost |
| Bio clipped under its own overflow | an open height got pinned and went stale |
| Empty frame where a card's image should be | the after-idle thumbnail warming (`lazy` → `eager`) didn't run |
