# The publication page

`_layouts/publication.html` — what a single `_publications/*.md` renders into. The Markdown
file is the content; this file is the vocabulary that content is written against.

Its `<head>` is not documented here — every meta, link and JSON-LD tag on this page belongs
to the **`seo`** skill. The "Related publications" list is data, and belongs to the
**`network`** skill; this page only reads the `related` array on the node whose `url`
matches, and tags a non-English suggestion with its language.

## What the page assembles

| Part | From |
|---|---|
| Byline | `credit-block.html` → `credit-full.html` — every contributor in citation order. The `<title>` tag calls `credit-full.html` directly and caps it at a first author plus *et al.*, to stay inside Google's display budget |
| "Cite" button | `publication-cite.html` writes a Chicago author-date reference into a hidden `<pre class="cite-data">`; `site-scripts.html` copies it on click |
| Prev/next | `publication-nav.html`, reading the `prev_pub` / `next_pub` refs that `publication_neighbors.rb` precomputes — no page scans the collection in Liquid |
| Related publications | `site.data.network`, matched by `url` |

## The body vocabulary

Everything below is CSS in this file, scoped to `.body`. The publications are written
against it, so **these class names are an interface** — changing one means rewriting call
sites across the corpus and bumping every `commit_date`.

### Width modifiers — figures and tables share them

| Class | Effect |
|---|---|
| `narrow` | image at 33% of the text column, centred |
| `half` | 50% |
| `three-quarter` | 75% |
| `full` | 100% |
| `wide` | breaks out of the column to `min(990px, 100vw − 2 gutters)`, image capped at 660px tall |

`wide` breaks out against the **990px measure, not the viewport** — an earlier `100vw` ran
the figure edge to edge on a narrow window. Below 660px + gutters the breakout is already no
wider than the column, so nothing is lost by the clamp.

Captions are clamped between 3/4 and the full column: a figure narrowed to `half` or
`three-quarter` still gets a 3/4-width centred caption, so a short caption stays readable
without decoupling from its figure. `wide` and full-width tables keep a full-width caption.

### Figures

`figure-single.html` for one image, `figure-group.html` for a multi-panel figure (pipe-delimited
`images=`). A group's panels keep their intrinsic width and share one caption;
`figure-group.three-quarter` narrows the *panels* to 75% while the caption stays full width.

`bordered` (from `styles-base.css`) puts a hairline on an image whose own edges are white.

### Tables

Wrap a Markdown table in `<figure class="data-table" markdown="1">` — `markdown="1"` is what
opts the inner table into kramdown, and the `figure` is what gives it the shared margin and
caption styling. Cells are `white-space: nowrap` and the figure scrolls horizontally rather
than squeezing.

| Add | For |
|---|---|
| `wrap` | tables with long-form prose cells — opts back into wrapping, except in the first column |
| `media` | tables whose cells hold images: the table shrinks to its content and centres, and columns 2 and 3 get explicit 200px / 300px image widths so the fixed-size images don't leave gaps under a `wide` canvas |

### Equations

`<p class="equation"><span class="eq-formula">…</span></p>` — a centred flex line. There is
no math renderer; the formula is written as markup.

## Print

The page has a print stylesheet: figures avoid breaking across pages, `data-table` is allowed
to break with its `thead` repeating as a header group, and a script forces every lazy figure
to load before the print dialog opens.

## Invariants — don't break these

- **The width vocabulary is an interface, not a stylesheet detail.** Before renaming or
  dropping a class, count its call sites: `/usr/bin/grep -ho 'class="[^"]*"' _publications/*.md | sort | uniq -c | sort -rn`.
- **`markdown="1"` on a table's `<figure>` is load-bearing.** Without it kramdown skips the
  block and the table renders as literal pipes.
- **`.cite-btn` and `.cite-data` are behavioural hooks**, deliberately separate from the
  classes that style the button. See `naming.md`.
