# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
bundle exec jekyll serve   # local dev server (http://localhost:4000)
bundle exec jekyll build   # build to _site/
```

No test suite, no asset pipeline, no npm for the site itself. The home network view consumes a pre-computed similarity graph and layout — when publications change, re-run `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` to regenerate `_data/network.json` (committed; the script shells out to Node for the layout step, so Node must be on PATH). See **Network view** below.

## Architecture

This is a Jekyll static site — the personal academic website of Dario Rodighiero at `dariorodighiero.com`.

**Content** lives entirely in `_publications/` as Markdown files, one per publication. Each file's front matter drives everything: `title`, `year`, `venue`, `type` (book / chapter / journal / conference / magazine / map), `author`, `doi`, `img` / `img_width` / `img_height`, and optional `redirect_from` entries. Optional bibliographic fields enrich the generated BibTeX (and the homepage search index) without appearing in the visible meta line: `editor`, `translator`, `publisher`, `place` (→ BibTeX `address`), `volume`, `issue`, `pages`, `isbn`. Note `venue` is type-dependent (its BibTeX target is set per type by `bibtex_venue`: `booktitle` for chapters/conferences, `journal` for journals/magazines, `publisher` for books/maps), so for a book chapter `venue` is the **book title** and the press goes in `publisher`; JSON-LD reads `publisher | default: venue`. The `type` taxonomy is defined once in `_data/publication_types.yml` (label, Schema.org type, DC.type, citation meta tag, BibTeX entry/venue field) — adding a new type means adding one entry there. The `layout: publication` is set globally via `defaults:` in `_config.yml`, so individual files do not declare it.

The body of each file is the abstract. Full-text articles (the complete published text, not just an abstract) put the lead/abstract paragraph first, then a `<!--more-->` marker, then the full text using `##` for section headings. The layout italicizes the part before `<!--more-->` as the lead. Footnotes/references inside full-text articles use kramdown footnote syntax (`[^1]` … `[^1]:`) and follow **Chicago author-date** style (e.g. `Author, First. Year. *Title*. Place: Publisher.`).

**Quotation marks**: use curly quotes (`“ ”`), never caporali/guillemets (`« »`), for Italian and English text. The only exception is French-language quotations, which keep French guillemets.

**CSS** is fully inlined (no external stylesheets, to avoid render-blocking requests): `_includes/main.css` holds the shared foundation (design tokens in `:root` — type scale, line heights, light/dark colors — plus base typography, `.meta-line`, `.authors`, `.cite-btn`, and the mode toggle) and `_includes/nunito.css` the `@font-face` rules; both layouts `{% include %}` them at the top of their page-specific `<style>` block. (`fonts/nunito.css` still exists only for the standalone `404.html`.) JS is inlined in the layouts; shared snippets live in `_includes/common-scripts.html` (mode toggle, cite buttons) and `_includes/head-init.html` (pre-paint color-scheme restore, included in both `<head>`s). No build step:
- `_layouts/home.html` — the only top-level publications page. Three view modes, toggled in the search bar and persisted in `localStorage` under `publicationView`: a **gallery** (custom JS masonry — newest first, packed by shortest column, `GAP_X`/`GAP_Y` in the inline script), a **list** (4-column grid with abstracts), and a **network** (publication similarity graph — see **Network view** below). A single full-width search bar filters across title, authors, editor, translator, venue, publisher, year, type label, volume, issue, pages and DOI; in network view it fades non-matching nodes and edges (and links touching them) instead of hiding them. The `.at-top` class is added by JS to suppress the top hairline on first-visible (list) or y=0 (gallery) cards. Author/editor/translator lines come from `_includes/authors-home.html`, which strips "Rodighiero" and prefixes with `with` / `edited with` / `translated with` (or `edited by` / `translated by` when Dario is not in the list). On `<= 1024 px` viewports the layout forces gallery (the toggle is hidden via CSS).
- `_layouts/publication.html` — individual publication pages. Generates BibTeX in a hidden `<pre>` and copies it to the clipboard on "Cite" button click. Prev/next navigation is computed in Liquid, sorted by year descending then title descending. Uses `_includes/authors.html` (the full citation, not the homepage shorthand).

**Bio** text lives in `README.md`, split into three paragraphs with `<!-- split -->` comments. `_plugins/readme_content.rb` reads it at each build cycle and exposes it as `site.data.readme_content` for the `home` layout. This way `README.md` doubles as the GitHub repo readme.

**Images** all live under `images/`: `images/@publications/` holds the full-size card/hero images (the front-matter `img` values carry the `@publications/` prefix); per-article figures sit in `images/<publication-slug>/` subfolders; `images/@thumbnails/` holds one flat max-800px card thumbnail per publication, named `<slug>.webp` after the publication's .md filename (generated by `scripts/generate-thumbnails.py`, which always re-encodes at thumbnail quality, committed to the repo — rerun it after adding or changing a card image); the author portrait sits directly in `images/` (full-size `Dario-Rodighiero.webp` for OG cards/JSON-LD, downsized `Dario-Rodighiero-640.webp` for the homepage header); `images/@icons/` holds the site icon set — `favicon.ico` (legacy tab icon, ~5 KB), the vector `icon.svg` (modern browsers), `apple-touch-icon.png` (180px, iOS/Android home screen), and `icon-192.png` / `icon-512.png` referenced by the root `site.webmanifest`. All are derived from one orthographic graticule-sphere source on a white background; both layouts declare them in `<head>` (SVG preferred, `.ico` as fallback) plus `<link rel="manifest">`. The `@` prefix sorts those folders first in listings; an underscore would not work, since Jekyll excludes underscore-prefixed paths from the build. Publication pages, OG/Twitter cards, and JSON-LD use `/images/{{ img }}`; homepage cards use `/images/@thumbnails/{{ slug }}.webp`.

**Fonts** are self-hosted under `fonts/` (Nunito). **JS** dependencies are self-hosted under `js/` (only D3 v7 today, loaded lazily by the network view). No CDN dependencies.

**Network view** is a publication similarity graph rendered with D3 from `js/d3.v7.min.js` (lazy-loaded on first open). Everything it needs — similarity **and the layout itself** — is pre-computed offline by `scripts/build-network.py`, which: (i) parses Markdown abstracts and strips footnotes, headings, links, code, and bibliographies; (ii) machine-translates non-English abstracts via `Helsinki-NLP/opus-mt-{lang}-en` (cached on disk in `_data/translations-cache.json` keyed by content hash); (iii) embeds title + abstract with `sentence-transformers/all-MiniLM-L6-v2` (its window is raised from the default 256 to the model's 512-token maximum via `MAX_SEQ_LENGTH`, so more of each text informs the vector); (iv) computes pairwise cosine similarity; (v) shells out to **`scripts/layout-network.js`** (Node + the vendored d3) to bake the force-directed arrangement; and (vi) writes `_data/network.json` (committed) — the node list (slug, title, url, index, **baked `x`/`y`**), the similarity matrix, the **`links`** array (each node's single strongest neighbour plus any pair above `STRONG_SIM = 0.80`), and the **`canvas`** size the positions were baked into. `layout-network.js` is the single source of truth for the graph geometry — it owns the force constants (`NODE_SPACING`, `CHARGE_STRENGTH`, `STRONG_SIM`, `GRAVITY`, `LAYOUT_SEED`, `LAYOUT_TICKS`) and the `CANVAS_W`/`CANVAS_H` it lays out into. The page consumes the data via Liquid and only **fit-scales** the baked positions into the live stage (uniform scale + center, fixed-px markers/labels; re-fit on resize) and draws the baked links — no force simulation runs in the browser. Re-run `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` after editing publications (it needs Node on PATH for the layout step).

**Plugins**: `jekyll-redirect-from` (legacy URL redirects), `jekyll-feed` (RSS for the `publications` collection), plus six local plugins in `_plugins/`:
- `autolink_urls.rb` — Liquid filter that wraps bare `http(s)://` URLs in anchors when rendering full-text bodies (skips URLs already inside `<a>` tags)
- `decode_numeric_entities.rb` — Liquid filter turning numeric character references (`&#8217;` / `&#x2019;`) into UTF-8 characters; applied to publication excerpts before `escape_once`, which would double-escape hex entities
- `git_mtime.rb` — adds `git_mtime` (last commit date) to each publication and `site.data` for sitemap `lastmod`; needs full git history (the deploy workflow uses `fetch-depth: 0`)
- `image_size.rb` — Liquid filter returning a WebP's intrinsic pixel dimensions (pure-Ruby parser), used by `_includes/figure.html` to set `width`/`height` and avoid CLS
- `publication_date.rb` — derives `page.date` from `year` so the RSS feed preserves the homepage sort order
- `readme_content.rb` — exposes `README.md` as `site.data.readme_content` (see Bio above)

## SEO

Both layouts share a common `<head>` structure:
- `<title>`, `meta description`, `meta keywords`, `rel=canonical`, `robots: index, follow`
- Open Graph (`og:title`, `og:description`, `og:url`, `og:type`, `og:image`, `og:image:alt`, `og:locale`)
- Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`)
- JSON-LD structured data

**`og:locale`** is set to `en_US` by default; publications with `lang: it` in their front matter get `it_IT`.

**OG/Twitter image**: `home.html` always uses the author portrait (`images/Dario-Rodighiero.webp`). `publication.html` uses `page.img` when present, falling back to the same portrait so social cards are never blank.

**JSON-LD types** on publication pages follow Schema.org: `Book`, `ScholarlyArticle` (journals, conferences, magazine articles, book chapters), and `Map`. `home.html` emits a `WebSite` + `Person` graph with `sameAs` links to ORCID, Google Scholar, GitHub, LinkedIn, and Zotero.
