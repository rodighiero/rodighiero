# Cards, search and filters

## One card style, three kinds of tile

Every tile carries a shared **`.card`** class holding the common metrics — padding, radius,
cursor, hover — alongside the class that says what it is:

| Class | What it is | Source |
|---|---|---|
| `.publication` | a publication | `_publications/*.md`, via `site.data.ordered_publications` |
| `.action` | a one-off view/type/search trigger | `_data/home_cards.yml` |
| `.filter` | a cluster tile setting a persistent filter | `site.data.network.clusters` (generated) |

`.action` and `.filter` are deliberately distinct from `.publication` so the count, search
and network-clone logic ignores them. Masonry packs everything via a combined `tiles`
NodeList (`:scope > .card`) while count/search stay on `.publication`.

Every card titles itself with `.card-title` — the publication's is an `<h2>`, the action
card's a `<span>` — styled by one shared rule for size, margin and weight. That rule's
`display: inline-block` is **load-bearing**: an inline-block's top margin does not collapse
with the meta line's bottom margin, so a `display: block` title would sit at half the gap.

`styles-base.css` sets the sub-row type on `.authors, .card-text` together, and `.card-media`
is the one wrapper class for both media slots — a publication's `<img>` thumbnail or an
action/filter's inlined SVG miniature — framed by a single rule, the thumbnail's loading tint
being the only difference.

The only per-kind declaration left is the action/filter tile's hairline: an **inset
`box-shadow`** rather than a real border, since a border eats 1px of content width per side
that a plain publication card keeps, which would sit the two kinds on slightly different
inner grids.

## `_includes/card-action.html`

Both non-publication kinds render through it, as a plain gallery card with no image by
default:

- a two-line `.card-meta` — a literal `year` (or `year: now` → build year), then
  ` · {{ eyebrow }}`, then an optional italic `.venue` second line via `<br>`;
- a `.card-title`;
- an optional `media="<include>.svg"` param rendering an inlined SVG into a `.card-media`
  slot above the text (the `view:network` card and every research-cluster card use it);
- the standard `--tint-hover` gray on hover.

A `mousedown` `preventDefault` on the `.action`/`.filter` buttons stops a click from starting
a stray text selection over the publications behind it.

## Manual action cards — `_data/home_cards.yml`

Fields: `label`, `action`, optional `year` / `eyebrow` / `venue` / `sublabel`, optional
`pin: first` (renders the card as the leading gallery tile, before the forthcoming works).

`action` is one of:

- `view:<gallery|network>` — switch view
- `type:<publication-type>` — set the type filter
- `search:<terms>` — set a free-text query

## Auto research-cluster cards

One card per `site.data.network.clusters` entry, each carrying its member slugs in
`data-slugs` and a `cluster:<id>` action. **They are not edited here** — the text comes from
`scripts/build-cards.py` and the miniature from `build-network.py`; see the `network` skill.

They are interleaved into the year-sorted flow at the **midpoint of their span** (just before
the publication named by the cluster's `anchor_slug`), so the cards spread through the
timeline rather than clumping.

Like the `view:network` card, a cluster card reads as a **short title over a quieter
description** — the cluster's emitted `title` in the `.card-title` slot and its `description`
in the `.card-text` slot beneath, the same place, and via the shared `.authors, .card-text`
rule the same typography, a publication card gives its authors. Its meta line reads
`Research cluster <n>`, numbered by the order the cards are emitted down the gallery (the
`_cluster_n` counter in `home.html`), **not** by the cluster's internal `id`.

## Where special cards appear

- **Gallery view only** (hidden in network via CSS), and hidden whenever a filter is active.
- Unpinned actions render at the top of `#publications`.
- A `pin: first` card leads the flow.
- Cluster cards sit inline before their span-midpoint anchor, with a `view:network` card
  leading the dated flow just after the forthcoming works.
- Hidden below 921px along with the view toggle and the filter count.

Publications render in one ordered loop, year-descending then title-ascending (Forthcoming
first), so the `_card_i` priority counter stays correct.

## Search

A single full-width search bar filters across **title, authors, editor, translator, venue,
publisher, year, type label, volume, issue, pages, DOI and language**. In network view it
fades non-matching nodes and edges (and links touching them) instead of hiding them.

**Language** is searchable by name — `english`, `french`/`français`/`francais`,
`italian`/`italiano` — derived per card from the front-matter `lang` (absent = English) and
appended to each card's `data-search` haystack. Only distinctive full names are indexed, not
the 2-letter ISO codes, which as substrings would match unrelated words.

Author/editor/translator/preface lines come from `_includes/credit-short.html`, which strips
"Rodighiero" and prefixes with `with` / `edited with` / `translated with` / `preface with`
(or `edited by` / `translated by` / `preface by` when Dario is not in the list).

## The three filters

Free-text (`?q=`), `activeType` (`?type=`) and `activeCluster` (`?cluster=`, a Set of member
slugs) are **mutually exclusive** and all run through the same `applySearch` pipeline —
gallery hides non-matches, network fades them. Each card carries `data-type="{{ type }}"`,
which is what the type filter reads.

All three are shareable in the URL (alongside `?view=`) and cleared together by Escape or by
clicking the active view button.
