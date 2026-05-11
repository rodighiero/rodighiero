# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
bundle exec jekyll serve   # local dev server (http://localhost:4000)
bundle exec jekyll build   # build to _site/
```

No test suite, no asset pipeline, no npm.

## Architecture

This is a Jekyll static site — the personal academic website of Dario Rodighiero at `dariorodighiero.com`.

**Content** lives entirely in `_projects/` as Markdown files, one per publication. Each file's front matter drives everything: `title`, `year`, `venue`, `type` (book / chapter / journal / conference / magazine / map), `author`, `doi`, `img` / `img_width` / `img_height`, and optional `redirect_from` entries.

**Layouts** are self-contained HTML files with inlined CSS and JS — no external stylesheet or build step:
- `_layouts/home.html` — the publications list; handles both the homepage and the filtered sub-pages. The `filter` front matter variable on a page (e.g. `filter: journal`) drives which type is shown and sets the `<title>` and canonical URL. Client-side JS buttons let the user switch filters without a page reload.
- `_layouts/project.html` — individual publication pages. Generates BibTeX in a hidden `<pre>` and copies it to the clipboard on "Cite" button click. Prev/next navigation is computed in Liquid, sorted by year descending then title descending.

**Filter pages** (`/books/`, `/journal-articles/`, `/conference-papers/`, `/book-chapters/`, `/magazine-articles/`, `/maps/`) are thin `index.html` files that each just set `layout: home` and a `filter` value, plus `redirect_from` entries for legacy URLs.

**Bio** text lives in `_includes/bio.md`, split into three paragraphs with `<!-- split -->` comments. The `home` layout includes it directly.

**Fonts** are self-hosted under `fonts/` (Nunito). No CDN dependencies.

**Plugins**: `jekyll-redirect-from` (legacy URL redirects), `jekyll-feed` (RSS for the `projects` collection).
