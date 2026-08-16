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

No test suite, no asset pipeline, no npm for the site itself. The build runs
`_plugins/publication_validator.rb`, which **aborts** on bad front matter — a failed build is
usually a publication, not the tooling.

Three artifacts are generated and committed. **Edit the script, never the artifact** — a
hand-edit passes review and is then silently reverted by the next rebuild.

| Artifact | Command | Rebuild when |
|---|---|---|
| `_data/network.json` + `_includes/network-*.svg` | `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` (minutes; it runs `build-cards.py` itself) | a publication is added, removed, or has its **body** edited |
| cluster-card text alone | `python3 scripts/build-cards.py` | rewording a cluster card — model-free, instant |
| `images/@cards/` | `python3 scripts/generate-thumbnails.py`, alongside `python3 scripts/optimize-images.py` | a `thumb` is added or replaced |

See the **`network`** and **`publication`** skills.

`node scripts/spring-easing.js` prints the CSS `linear()` spring curves to paste into `_layouts/home.html`, so retuning the gallery's tile motion is a parameter change rather than a hand-tweaked list of numbers. See the `layout` skill.

## Architecture

This is a Jekyll static site — the personal academic website of Dario Rodighiero at `dariorodighiero.com`.

**Content** lives entirely in `_publications/` as Markdown files, one per publication — there is no database. Each file's front matter drives the card, the page, the citation, the RSS entry, the sitemap, the JSON-LD and its position in the similarity network; the body is the abstract, or a lead plus `<!--more-->` plus the full text. The slug is the filename, and it is also the URL, the `images/<slug>/` folder name and the key other entries reference. The `type` taxonomy is defined once in `_data/publication_types.yml`, and `layout: publication` comes from `defaults:` in `_config.yml`, so individual files do not declare it.

Field-by-field schema, body conventions, figures and tables, house style, images and validation: the **`publication`** skill.

**Quotation marks**: use curly quotes (`“ ”`), never caporali/guillemets (`« »`), for Italian and English text. The only exception is French-language quotations, which keep French guillemets.

**Editing a publication file bumps its `commit_date`**, which is what feeds sitemap `lastmod` and JSON-LD `dateModified`. So a sweep across every file for a cosmetic reason republishes the whole corpus — worth it for a real correction, not for tidiness. What the value is and who reads it: the **`plugins`** skill.

**CSS** is fully inlined (no external stylesheets, to avoid render-blocking requests): `_includes/styles-base.css` holds the shared foundation (design tokens in `:root` — type scale, line heights, light/dark colors — plus base typography, `.card-meta`, `.authors`, `.cite-btn`, and the mode toggle) and `_includes/styles-font.css` the `@font-face` rules; both layouts `{% include %}` them at the top of their page-specific `<style>` block, and so does the standalone `404.html` for the fonts. JS is inlined in the layouts; shared snippets live in `_includes/site-scripts.html` (mode toggle, cite buttons), `_includes/site-head.html` (the page-invariant meta and link tags both `<head>`s share verbatim; the inventory is in the `seo` skill) and `_includes/site-scheme.html` (the pre-paint color-scheme restore, which `404.html` needs as well). There is no build step.

The site has two layouts:
- `_layouts/home.html` — the only top-level publications page: a **gallery** (custom JS masonry) and a **network** (the similarity graph), toggled in the search bar and persisted in `localStorage`, with one search box and three mutually exclusive filters (`?q=`, `?type=`, `?cluster=`) shareable in the URL. The whole page is laid out on the gallery's own columns — the card width is the constant and the column count follows from it, sizing the body, the header, the footer and the network stage alike. Grid arithmetic, the card system, the special/action/cluster tiles, motion and the bio collapse: the **`layout`** skill.
- `_layouts/publication.html` — individual publication pages: the Chicago author-date reference the "Cite" button copies (`publication-cite.html`), the full byline (`credit-block.html`), prev/next from the refs `_plugins/publication_neighbors.rb` precomputes (`publication-nav.html`), and a **"Related publications"** list read from the page's node in `site.data.network`. The figure and table class vocabulary the publication bodies are written against lives here too. Its `<head>` belongs to the **`seo`** skill, its `related` list to the **`network`** skill; the page itself is documented in the **`publication`** skill (`reference/page.md`).

**Bio** text lives in `README.md`, split into three paragraphs with `<!-- split -->` comments, so the file doubles as the GitHub repo readme; `_plugins/system_readme.rb` exposes it as `site.data.readme_content`. The masthead collapse: the **`layout`** skill.

**Includes are named `<family>-<member>`** — a family noun that groups siblings, then which one of them this is: `credit-` (block, full, join, names, short), `card-` (action, meta), `figure-` (group, single), `jsonld-` (people, person), `publication-` (cite, nav), `site-` (analytics, head, scheme, scripts, toggle), `styles-` (base, font), plus the generated `network-*.svg`. The family word classifies, so it comes first and is always a noun, never a verb phrase; a helper that would found a family of one folds into the family it serves instead. The same shape carries into the behavioural class hooks the JS selects on, which stay separate from the classes that style them: `.cite-btn` and `.cite-data` are one `cite-` family, wearing `.pill-btn` for their looks. Renaming `figure-single`/`figure-group` is the one move to think twice about — they are called from nearly every publication, so a rename rewrites the corpus and bumps every `commit_date`. Why each family is named what it is, and the renames already settled: the **`publication`** skill (`reference/naming.md`).

**Images** all live under `images/`, on one rule: **every source image belongs to its publication**, in `images/<publication-slug>/`. Two folders are exceptions and both are generated or shared — `images/@cards/` (the homepage's thumbnails) and `images/@icons/` (the site icon set); the author portrait sits directly in `images/`. There is **one** image field, `thumb`, feeding both the homepage card and the social preview, so the two can never diverge. Compression policy, the `@` prefix, the portrait's `srcset` ladder and which path each surface uses: the **`publication`** skill (`reference/images.md`).

**Fonts** are self-hosted under `fonts/` (Nunito). **The site ships no JS library at all** — `js/` holds only `count.js` (the analytics snippet); every line of behaviour is hand-written and inlined in the layouts. D3 still exists in the repo, but purely as **build-time tooling**: `scripts/vendor/d3.v7.min.js`, required by `scripts/layout-network.js` for `d3-force`. It sits beside its one consumer rather than in `js/`, and `_config.yml` excludes `scripts/` from the build, so it is never published. No CDN dependencies.

**Network view** is a publication similarity graph, pre-computed offline into `_data/network.json` — the browser runs no simulation and loads no library. One file feeds three surfaces (the network view, the homepage's research-cluster cards, and each publication page's "Related publications"), so they can never disagree. The link rule, the embeddings and machine translation, the cluster rule, the miniatures and every tuning constant: the **`network`** skill.

**Plugins**: `jekyll-feed` (RSS for the `publications` collection), plus eleven local plugins in `_plugins/` — the layer that lets templates *read* derived values instead of computing them. Like the includes they are named in two words, and the first word is one of **two**: **`publication_`** (eight files) for the `publications` collection, **`system_`** (three) for everything else. They run only because the site deploys through **GitHub Actions** rather than GitHub's branch build, which ignores `_plugins/` entirely; and none of them depends on a gem. What each produces, who reads it, the naming edge cases and the invariants: the **`plugins`** skill.

**SEO and machine metadata** — everything the site says to a machine rather than to a reader: both layouts' `<head>`, JSON-LD, `hreflang` and translation sets, the Google Scholar and Dublin Core citation tags, Zotero import, ISSN/ISBN, `sitemap.xml`, `robots.txt`, the redirect stubs and the 404. One thing worth knowing without loading the skill: `_data/publication_types.yml` is the single source deciding a type's Schema.org `@type`, its `DC.type`, which `citation_*` venue tag it uses and how its `venue` is modelled. All of it: the **`seo`** skill.

**Continuous integration** is two GitHub Actions workflows in `.github/workflows/`:
- `deploy.yml` — builds and publishes the site on every push (GitHub Actions deployment, not branch deployment, so the local `_plugins/` run at all). It checks out with `fetch-depth: 0` because `system_commit_date.rb` needs full history, and deletes the parked `/feed/posts.xml` that `jekyll-feed` always emits alongside the real `/feed.xml`
- `links.yml` — a weekly **lychee** crawl of the built `_site/`, plus `workflow_dispatch`. A red result is normal maintenance rather than a broken build. Reading its report, and repairing a dead reference with a Wayback capture appended beside the original URL rather than replacing it: the **`links`** skill
