# Copilot Instructions for Rodighiero Personal Website

This is a Jekyll-based static site (https://dariorodighiero.com) with custom plugins, semantic SEO, and a publication network graph.

## Build, Test & Deploy

**Local development:**
```bash
bundle exec jekyll serve   # Start dev server at http://localhost:4000
bundle exec jekyll build   # Build static site to _site/
```

**Network graph regeneration** (after editing publications):
```bash
KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py
```
This rebuilds `_data/network.json` from publication abstracts using embeddings and force-directed layout. Requires Python 3 and Node.js on PATH.

**Thumbnail generation** (after adding/changing card images):
```bash
python3 scripts/generate-thumbnails.py
```

**Link validation** (run on deploy; can be invoked manually):
```bash
bundle exec jekyll build && python3 scripts/link-context.py lychee/out.md
```

No test suite. Deployment to GitHub Pages is triggered on push to `main` via `.github/workflows/deploy.yml`; link checking runs weekly via `links.yml`.

## High-Level Architecture

**Content model**: Publications live in `_publications/` as Markdown files. Each publication's YAML front matter is the single source of truth for all metadata (title, year, venue, type, authors, DOI, images, etc.); the body is the abstract or full text. The Liquid layout system (`_layouts/publication.html`) generates individual pages, while `_layouts/home.html` renders three interactive views (gallery, list, network).

**One image field, one purpose**: The `thumb` front-matter field is the only image field. It serves as:
- Homepage card thumbnail (`images/@thumbnails/{slug}.webp`, auto-generated at build time)
- OG/Twitter/JSON-LD social preview image (full-size, via `image_size` filter for intrinsic dimensions)
- Source for on-page figures (via `{% include figure.html %}` in the body, not a separate hero)

**No external dependencies**: CSS and JS are fully inlined (no stylesheet/script tags). Fonts are self-hosted (Nunito). D3 is vendored and lazy-loaded only in network view.

**Bio integration**: README.md is split into three sections (via `<!-- split -->` comments); the `readme_content.rb` plugin exposes it as `site.data.readme_content` so the bio drives both GitHub and homepage.

**Custom Liquid plugins** (`_plugins/`):
- `image_size.rb` — parses WebP dimensions to set `width`/`height` (prevents CLS)
- `git_mtime.rb` — adds `git_mtime` to each page (needs full git history; deploy uses `fetch-depth: 0`)
- `readme_content.rb` — exposes README.md as `site.data.readme_content`
- `publication_date.rb` — derives `page.date` from `year` (for RSS sort order)
- `autolink_urls.rb` — wraps bare URLs in anchors (skips already-linked URLs)
- `decode_numeric_entities.rb` — converts numeric character refs to UTF-8

**Semantic SEO**: Each layout declares `og:locale` (en_US / it_IT / fr_FR based on front-matter `lang`), generates BibTeX from front matter, and emits Schema.org JSON-LD (Book, ScholarlyArticle, Article, Map types mapped in `_data/publication_types.yml`).

## Key Conventions

### Publications (Front Matter)

Every publication requires:
- `title`, `year`, `venue`, `type`, `author`, `thumb`

Optional enrichment fields (non-display; affect BibTeX & search index):
- `editor`, `translator`, `preface` (byline contributors; joined with `with`/`by` in rendering)
- `publisher`, `place` (→ BibTeX `address`), `volume`, `issue`, `pages`, `isbn`, `doi`
- `month`, `day` (1-12 and 1-31; for precise RSS feed ordering within a year; defaults to 1)
- `lang: it` or `lang: fr` (defaults to English; affects `og:locale` and citation meta tags)
- `img_border: true` (draws hairline around card)

The `type` taxonomy is the single source of truth in `_data/publication_types.yml` (label, Schema.org type, DC.type, citation meta, BibTeX entry/venue field). Venue field meaning depends on type: for chapters/conferences it's booktitle, for journals/magazines it's journal name, for books/maps it's publisher.

### Publication Body (Markdown)

**Abstracts only**: Body is rendered as the lead paragraph, italicized.

**Full-text articles**: First paragraph (abstract), then `<!--more-->`, then full text with `##` section headings. Chicago author-date footnotes use kramdown syntax (`[^1]` … `[^1]:`).

**Figures**: Use `{% include figure.html %}` — it reads `width`/`height` from WebP intrinsic size and avoids CLS. Set `class="narrow"`, `class="three-quarter"`, or `class="wide"` for sizing (image-only: `class="full"` breaks to full viewport).

**Tables**: Wrap Markdown tables in:
```html
<figure class="data-table" markdown="1">
| Column 1 | Column 2 |
|:--|--:|
| Left | Right |
<figcaption>Table 1. Description.</figcaption>
</figure>
```
Add `narrow`, `three-quarter`, or `wide` class to `data-table` for column width.

**Quotation marks**: Use curly quotes (`" "`) for English/Italian; French text keeps guillemets (`« »`).

### Images

**Directory structure**:
- `images/@cards/` — full-size social preview images (referenced in `thumb` as `@cards/Name.webp`)
- `images/@thumbnails/` — auto-generated max-800px thumbnails (`{slug}.webp`); regenerate with `scripts/generate-thumbnails.py`
- `images/{slug}/` — per-publication figures (referenced in body as `{slug}/fig_001.webp`)
- `images/@icons/` — site icon set (favicon, app icons, manifest icons)

**Important**: The single `thumb` field drives both the homepage card thumbnail and social preview, so design card images to work at any aspect ratio (build-time intrinsic dimensions set the card space).

### Home Page Search & Views

The search bar filters across: title, authors, editor, translator, venue, publisher, year, type label, volume, issue, pages, DOI, language.

Language is searchable by full name (e.g., `english`, `français`, `italiano`) — derived from front-matter `lang` and added to each card's `data-search` haystack. Only distinctive names are indexed (not 2-letter ISO codes).

Three view modes (toggled in search bar, persisted in localStorage as `publicationView`):
- **Gallery**: Custom JS masonry (newest first, packed by shortest column)
- **List**: 4-column grid with abstracts
- **Network**: Force-directed publication similarity graph (pre-computed by `build-network.py`, lazy-loads D3)

On viewport ≤ 1024px, gallery is forced and toggle hidden.

### CSS & Inlining

All CSS is inlined in `<style>` blocks (no external stylesheets). Shared tokens live in:
- `_includes/main.css` — design tokens (`:root`), base typography, `.meta-line`, `.authors`, `.cite-btn`, mode toggle
- `_includes/nunito.css` — `@font-face` rules for Nunito

Both layouts include these at the top of their page-specific `<style>` block. The mode toggle (light/dark) and citation buttons are in `_includes/common-scripts.html`.

### Publication Type Taxonomy

Edit `_data/publication_types.yml` to add or modify types. Each entry defines:
- Display label
- Schema.org type (for JSON-LD)
- Dublin Core type
- Citation meta tag
- BibTeX entry type
- BibTeX venue field (booktitle/journal/publisher)

## Common Tasks

**Add a publication**:
1. Create `_publications/{slug}.md` with required front matter
2. Add `thumb` pointing to `images/@cards/{name}.webp` or a body figure
3. If using a new `@cards/` image, ensure it's WebP
4. Run `python3 scripts/generate-thumbnails.py` to create the thumbnail
5. Run `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` to regenerate the network graph

**Edit an existing publication**:
- Changing metadata (front matter) alone: no regeneration needed
- Changing text (abstract/body): regenerate network with `build-network.py`
- Changing card image: regenerate thumbnails and network

**Update site bio**:
- Edit `README.md` (maintain the three `<!-- split -->` sections)
- The bio appears on both GitHub and homepage automatically

**Adjust network layout**:
- Edit constants in `scripts/layout-network.js` (`NODE_SPACING`, `CHARGE_STRENGTH`, `STRONG_SIM`, `GRAVITY`, `LAYOUT_SEED`, `LAYOUT_TICKS`, `CANVAS_W`, `CANVAS_H`)
- Re-run `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` to bake new positions into `_data/network.json`
