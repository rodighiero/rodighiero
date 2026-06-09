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

The body of each file is the abstract. Full-text articles (the complete published text, not just an abstract) put the lead/abstract paragraph first, then a `<!--more-->` marker, then the full text using `##` for section headings. The layout italicizes the part before `<!--more-->` as the lead. Footnotes/references inside full-text articles use kramdown footnote syntax (`[^1]` … `[^1]:`) and follow **Chicago author-date** style (e.g. `Author, First. Year. *Title*. Place: Publisher.`).

**Quotation marks**: use curly quotes (`“ ”`), never caporali/guillemets (`« »`), for Italian and English text. The only exception is French-language quotations, which keep French guillemets.

**CSS** is split in two: `css/main.css` holds the shared foundation (design tokens in `:root` — type scale, line heights, light/dark colors — plus base typography, `.meta-line`, `.authors`, `.cite-btn`, and the mode toggle), while each layout inlines its own page-specific styles in a `<style>` block. JS is inlined in the layouts; shared snippets (mode toggle, cite buttons) live in `_includes/common-scripts.html`. No build step:
- `_layouts/home.html` — the only top-level publications page. Two view modes, toggled in the search bar and persisted in `localStorage` under `publicationView`: a **gallery** (custom JS masonry — newest first, packed by shortest column, `GAP_X`/`GAP_Y` in the inline script) and a **list** (4-column grid with abstracts). A single full-width search bar filters across title, authors, editor, translator, venue, year, type label, volume, issue, pages and DOI. The `.at-top` class is added by JS to suppress the top hairline on first-visible (list) or y=0 (gallery) cards. Author/editor/translator lines come from `_includes/authors-home.html`, which strips "Rodighiero" and prefixes with `with` / `edited with` / `translated with` (or `edited by` / `translated by` when Dario is not in the list).
- `_layouts/publication.html` — individual publication pages. Generates BibTeX in a hidden `<pre>` and copies it to the clipboard on "Cite" button click. Prev/next navigation is computed in Liquid, sorted by year descending then title descending. Uses `_includes/authors.html` (the full citation, not the homepage shorthand).

**Bio** text lives in `README.md`, split into three paragraphs with `<!-- split -->` comments. `_plugins/readme_content.rb` reads it at each build cycle and exposes it as `site.data.readme_content` for the `home` layout. This way `README.md` doubles as the GitHub repo readme.

**Fonts** are self-hosted under `fonts/` (Nunito). No CDN dependencies.

**Plugins**: `jekyll-redirect-from` (legacy URL redirects), `jekyll-feed` (RSS for the `publications` collection), plus five local plugins in `_plugins/`:
- `autolink_urls.rb` — Liquid filter that wraps bare `http(s)://` URLs in anchors when rendering full-text bodies (skips URLs already inside `<a>` tags)
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
