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

**Content** lives entirely in `_publications/` as Markdown files, one per publication. Each file's front matter drives everything: `title`, `year`, `venue`, `type` (book / chapter / journal / conference / magazine / map), `author`, `doi`, `img` / `img_width` / `img_height`, and optional `redirect_from` entries. The `layout: publication` is set globally via `defaults:` in `_config.yml`, so individual files do not declare it.

**Layouts** are self-contained HTML files with inlined CSS and JS — no external stylesheet or build step:
- `_layouts/home.html` — the publications list; handles both the homepage and the filtered sub-pages. The `filter` front matter variable on a page (e.g. `filter: journal`) drives which type is shown and sets the `<title>` and canonical URL. Client-side JS buttons let the user switch filters without a page reload.
- `_layouts/publication.html` — individual publication pages. Generates BibTeX in a hidden `<pre>` and copies it to the clipboard on "Cite" button click. Prev/next navigation is computed in Liquid, sorted by year descending then title descending.

**Filter pages** (`/books/`, `/journal-articles/`, `/conference-papers/`, `/book-chapters/`, `/magazine-articles/`, `/maps/`) are generated at build time by `_plugins/filter_pages.rb` — no static directories needed. To add or rename a filter, edit the `filters` array in that file.

**Bio** text lives in `README.md`, split into three paragraphs with `<!-- split -->` comments. `_plugins/readme_content.rb` reads it at each build cycle and exposes it as `site.data.readme_content` for the `home` layout. This way `README.md` doubles as the GitHub repo readme.

**Fonts** are self-hosted under `fonts/` (Nunito). No CDN dependencies.

**Plugins**: `jekyll-redirect-from` (legacy URL redirects), `jekyll-feed` (RSS for the `publications` collection), plus two local plugins in `_plugins/`.

## SEO

Both layouts share a common `<head>` structure:
- `<title>`, `meta description`, `meta keywords`, `rel=canonical`, `robots: index, follow`
- Open Graph (`og:title`, `og:description`, `og:url`, `og:type`, `og:image`, `og:image:alt`, `og:locale`)
- Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`)
- JSON-LD structured data

**`og:locale`** is set to `en_US` by default; publications with `lang: it` in their front matter get `it_IT`.

**OG/Twitter image**: `home.html` always uses the author portrait (`images/Dario-Rodighiero.webp`). `publication.html` uses `page.img` when present, falling back to the same portrait so social cards are never blank.

**JSON-LD types** on publication pages follow Schema.org: `Book`, `ScholarlyArticle` (journals, conferences, magazine articles, book chapters), and `Map`. `home.html` emits a `WebSite` + `Person` graph with `sameAs` links to ORCID, Google Scholar, GitHub, LinkedIn, and Zotero.
