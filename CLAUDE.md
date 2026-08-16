# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Skills

The detail behind each of the six objects this repo is made of lives in `.claude/skills/`,
not here. Load the skill before working on one; this file keeps only what is true across all
of them.

| Skill | Owns |
|---|---|
| `publication` | `_publications/*.md` and everything downstream — front matter, bodies, figures, images, translations, identifiers, validation |
| `network` | the similarity graph — `_data/network.json`, the build scripts, clusters, cluster-card text, the SVG miniatures |
| `layout` | `_layouts/home.html` — the grid and its column arithmetic, the card system, search and filters, motion, the bio collapse |
| `seo` | everything declared to machines — both `<head>`s, JSON-LD, hreflang, the Scholar/Dublin Core tags, Zotero, `sitemap.xml`, `robots.txt`, aliases, the 404 |
| `plugins` | the eleven Ruby files in `_plugins/` — what each produces and who reads it, the naming scheme, the build-order rules |
| `links` | link rot — the weekly lychee crawl, its report, and the Wayback fallback for a dead reference |

## Commands

```bash
bundle exec jekyll serve   # local dev server (http://localhost:4000)
bundle exec jekyll build   # build to _site/
```

No test suite, no asset pipeline, no npm for the site itself. Two generated artifacts are committed and have their own commands — `_data/network.json` and the graph miniatures (`KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py`, then the fast model-free `python3 scripts/build-cards.py` for card text alone; see the `network` skill), and the homepage thumbnails in `images/@cards/` (`python3 scripts/generate-thumbnails.py`, alongside `python3 scripts/optimize-images.py`; see the `publication` skill).

`node scripts/spring-easing.js` prints the CSS `linear()` spring curves to paste into `_layouts/home.html`, so retuning the gallery's tile motion is a parameter change rather than a hand-tweaked list of numbers. See the `layout` skill.

## Architecture

This is a Jekyll static site — the personal academic website of Dario Rodighiero at `dariorodighiero.com`.

**Content** lives entirely in `_publications/` as Markdown files, one per publication — there is no database. Each file's front matter drives the card, the page, the citation, the RSS entry, the sitemap, the JSON-LD and its position in the similarity network; the body is the abstract, or a lead plus `<!--more-->` plus the full text. The slug is the filename, and it is also the URL, the `images/<slug>/` folder name and the key other entries reference. The `type` taxonomy is defined once in `_data/publication_types.yml`, and `layout: publication` comes from `defaults:` in `_config.yml`, so individual files do not declare it.

Field-by-field schema, body conventions, figures and tables, house style, images and validation: the **`publication`** skill.

**Quotation marks**: use curly quotes (`“ ”`), never caporali/guillemets (`« »`), for Italian and English text. The only exception is French-language quotations, which keep French guillemets.

**CSS** is fully inlined (no external stylesheets, to avoid render-blocking requests): `_includes/styles-base.css` holds the shared foundation (design tokens in `:root` — type scale, line heights, light/dark colors — plus base typography, `.card-meta`, `.authors`, `.cite-btn`, and the mode toggle) and `_includes/styles-font.css` the `@font-face` rules; both layouts `{% include %}` them at the top of their page-specific `<style>` block. (`fonts/nunito.css` still exists only for the standalone `404.html`.) JS is inlined in the layouts; shared snippets live in `_includes/site-scripts.html` (mode toggle, cite buttons) and `_includes/site-head.html` (everything both `<head>`s share verbatim: the pre-paint color-scheme restore plus the page-invariant meta/link tags — viewport, robots, author, theme-color, `og:site_name`, `twitter:card`, the RSS link, the Dublin Core schema links and the icon/manifest set). No build step:
- `_layouts/home.html` — the only top-level publications page: a **gallery** (custom JS masonry) and a **network** (the similarity graph), toggled in the search bar and persisted in `localStorage`, with one search box and three mutually exclusive filters (`?q=`, `?type=`, `?cluster=`) shareable in the URL. The whole page is laid out on the gallery's own columns — the card width is the constant and the column count follows from it, sizing the body, the header, the footer and the network stage alike. Grid arithmetic, the card system, the special/action/cluster tiles, motion and the bio collapse: the **`layout`** skill.
- `_layouts/publication.html` — individual publication pages. Generates a formatted Chicago author-date reference in a hidden `<pre>` (via `publication-cite.html`) and copies it to the clipboard on "Cite" button click. Prev/next navigation reads the `prev_pub`/`next_pub` refs precomputed by `_plugins/publication_neighbors.rb` (via `publication-nav.html`), so no page scans the whole collection in Liquid. Uses `_includes/credit-block.html` (the full citation, not the homepage shorthand; it includes `credit-full.html`, the same byline formatter `publication.html`'s `<title>` tag uses directly, capped there to a first author plus *et al.*). Above the footer nav it renders a **"Related publications"** list — the page's three closest works, read from its node's `related` array in `site.data.network` (matched by `url`); a non-English suggestion carries a small language tag. See **Network view** for how `related` is computed (and note it works for **every** language, unlike the English-only graph).

**Includes are named `<family>-<member>`** — a family noun that groups siblings, then which one of them this is: `credit-` (block, full, join, names, short), `card-` (action, meta), `figure-` (group, single), `jsonld-` (people, person), `publication-` (cite, nav), `site-` (analytics, head, scripts, toggle), `styles-` (base, font), plus the generated `network-*.svg`. The family word is what classifies, so it comes first and is always a noun — not a verb phrase like the `join-and.html` this rule replaced. A helper that would otherwise found a family of one folds into the family it serves rather than starting its own: `credit-join.html` joins name lists for both the homepage byline and the Chicago reference, so it is a `credit-`, not a `list-`. That family was `byline-` until it grew past the word: a byline is strictly the *author* line, while these files also render "Ed.", "Translated by", "Preface by" and "Interview by", which `credit-` covers without stretching. Its two leading members are named for the **voice** rather than the surface — `credit-full` names every contributor in citation order (publication page and `<title>`), `credit-short` writes from Dario's point of view with his own name stripped ("with X and Y", homepage cards) — because the old `-text`/`-home` pair named a format and a place while the real distinction between them is neither. The word "byline" survives in prose and in `publication_validator.rb`'s error message, where it means the author line and is exactly right. Renaming `figure-single`/`figure-group` is the one move to think twice about — they are called 335 times across 61 of the 64 publications, and rewriting those files would bump every publication's `commit_date`, which is what feeds sitemap `lastmod` and JSON-LD `dateModified`. The same two-word shape carries into the behavioural class hooks the JS selects on, which are deliberately separate from the classes that style them: `.cite-btn` (the trigger) and `.cite-data` (the hidden `<pre>` it copies) are one `cite-` family, wearing `.pill-btn` for their looks.

**Motion** on the homepage is CSS, not a library — there is no animation dependency, and no rendering one either: `js/` holds only the analytics snippet. A view switch cross-fades the page; a gallery filter change animates the real tiles on a sampled spring and deliberately does not use a view transition; moves the reader cannot follow are cut rather than animated, and `prefers-reduced-motion` cuts everything. The page scrolls for the reader in exactly one case. All of it: the **`layout`** skill.

**Bio** text lives in `README.md`, split into three paragraphs with `<!-- split -->` comments. `_plugins/system_readme.rb` reads it at each build cycle and exposes it as `site.data.readme_content` for the `home` layout, so `README.md` doubles as the GitHub repo readme. The masthead collapses behind a toggle whose state is one attribute on `<html>`, restored before the first paint — see the **`layout`** skill before touching it, the collapse deliberately stores no height at rest.

**Images** all live under `images/`, on one rule: **every source image belongs to its publication**, in `images/<publication-slug>/`. Two folders are exceptions and both are generated or shared: `images/@cards/` (one flat max-800px copy per publication — the only image set the homepage loads, never a source for a social card) and `images/@icons/` (the site icon set). The author portrait sits directly in `images/`. The `@` prefix sorts them first in listings; an underscore would not work, since Jekyll excludes underscore-prefixed paths from the build. There is **one** image field, `thumb`, feeding both the homepage card and the social preview, so the two can never diverge. Compression policy, the portrait's `srcset` ladder, and which path each surface uses: the **`publication`** skill (`reference/images.md`).

**Fonts** are self-hosted under `fonts/` (Nunito). **The site ships no JS library at all** — `js/` holds only `count.js` (the analytics snippet); every line of behaviour is hand-written and inlined in the layouts. D3 still exists in the repo, but purely as **build-time tooling**: `scripts/vendor/d3.v7.min.js`, required by `scripts/layout-network.js` for `d3-force`. It sits beside its one consumer rather than in `js/`, and `_config.yml` excludes `scripts/` from the build, so it is never published. No CDN dependencies.

**Network view** is a publication similarity graph. Everything it needs — the similarity, the clusters and the force-directed layout itself — is pre-computed offline by `scripts/build-network.py` into the committed `_data/network.json`, plus the graph miniatures in `_includes/network-*.svg`. The browser runs no simulation and loads no library: it fit-scales the baked coordinates into the stage and draws the baked links with plain DOM calls. One file feeds three surfaces — the network view, the homepage's research-cluster cards, and the "Related publications" list on each publication page — so they can never disagree. The link rule, the embeddings and machine translation, the cluster rule, the miniatures and every tuning constant: the **`network`** skill.

**Plugins**: `jekyll-feed` (RSS for the `publications` collection), plus eleven local plugins in `_plugins/` — the layer that lets templates *read* derived values instead of computing them. Like the includes they are named in two words, and the first word is one of **two**: **`publication_`** (eight files) for everything that reads, orders, validates or decorates the `publications` collection, and **`system_`** (three) for everything else. Two prefixes with no third case means there is nothing to adjudicate: a plugin either works on the collection or it does not. Every plugin opens with a header comment naming what it registers, publishes or attaches, and who reads it — that line is the index, and it is the only place the coupling is written down, since a filename like `publication_decoder.rb` does not say `| decode_numeric_entities`. They run only because the site deploys through **GitHub Actions** rather than GitHub's branch build, which ignores `_plugins/` entirely; and none of them depends on a gem. What each one does, the three edge cases in the naming rule, the two schemes tried and rejected, and the invariants: the **`plugins`** skill.

**Continuous integration** is two GitHub Actions workflows in `.github/workflows/`:
- `deploy.yml` — builds and publishes the site on every push (GitHub Actions deployment, not branch deployment, so the local `_plugins/` run at all). It checks out with `fetch-depth: 0` because `system_commit_date.rb` needs full history, and deletes the parked `/feed/posts.xml` that `jekyll-feed` always emits alongside the real `/feed.xml`
- `links.yml` — a weekly **lychee** crawl of the built `_site/`, plus `workflow_dispatch`. Because a link can rot without anything in the repo changing, the run is scheduled rather than push-triggered, and a red result is normal maintenance rather than a broken build. Reading its report and repairing a dead reference: the **`links`** skill

**Dead references get an archive fallback rather than a deletion** — the cited URL stays exactly where it is, since rewriting it would falsify the citation, and a verified Wayback capture is appended beside it. Procedure and the rules for picking a capture: the **`links`** skill.

## SEO

Everything the site says to a machine rather than to a reader — both layouts' `<head>`,
JSON-LD, `hreflang` and translation sets, the Google Scholar and Dublin Core citation tags,
Zotero import, ISSN/ISBN, `sitemap.xml`, `robots.txt`, the redirect stubs and the 404 — is the
**`seo`** skill. Two things worth knowing without loading it: `_data/publication_types.yml` is
the single source deciding a type's Schema.org `@type`, its `DC.type`, which `citation_*`
venue tag it uses and how its `venue` is modelled; and Dario's ORCID is used as a JSON-LD
`@id` on every page, which is the only thing tying the publications to the homepage's `Person`.
