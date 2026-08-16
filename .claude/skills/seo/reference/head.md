# The head tags

Three sources compose each `<head>`: `_includes/site-head.html` (verbatim on both pages), then
the page-specific block in `_layouts/home.html` or `_layouts/publication.html`.

## Shared — `_includes/site-head.html`

Everything here is page-invariant, which is the admission test: a tag whose value depends on
the page does not belong in this file.

`viewport`, `robots`, `author`, two `theme-color`s (light/dark), `color-scheme`, the RSS
`<link rel=alternate>`, `og:site_name`, `twitter:card`, the two Dublin Core schema links, and
the icon/manifest set. Plus the pre-paint `colorScheme` restore script — not metadata, but it
must run before the first paint and every page needs it.

`robots` is `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1`.
Indexing was never blocked; the three `max-*` directives only lift the caps on how a result
may *render* in Search and Discover.

## The two derived strings on a publication page

Computed at the top of the head, before anything uses them:

| Assign | What it is |
|---|---|
| `_excerpt` | `content \| strip_html \| decode_numeric_entities \| truncatewords: 22 \| truncate: 160` — the search-snippet budget |
| `_abstract` | `content \| split: '<!--more-->' \| first \| strip_html \| …` — the abstract whole, no budget |

`_excerpt` feeds `description`, `og:description`, `twitter:description`, `DC.description`
and JSON-LD `description`. `_abstract` feeds JSON-LD `abstract` only.

Two ordering rules are load-bearing. **Split on `<!--more-->` before `strip_html`** — an HTML
comment is a tag, so stripping first takes the marker with it and the abstract becomes the
whole article. And **`decode_numeric_entities` before `escape_once`** — `escape_once`'s
exemption regexp covers named and decimal entities but not hex, so a `&#x2019;` would
double-escape into a visible `&amp;#x2019;` in a social card. No source currently contains
one; it is a guard against an invisible failure, not a live transformation.

## `<title>`

`{{ title }} — {{ credit }}`, where the credit comes from `credit-full.html` — the same
formatter the page body uses — but **capped to `First Author et al.` past two names**, to stay
inside Google's ~60-character display budget. The body's version is uncapped. Two renderings
of one function, deliberately.

## Language and translation sets

`lang` (defaulting to `en`) drives, on one page: `<html lang>`, `og:locale`
(`en_US`/`it_IT`/`fr_FR`), `citation_language`, `DC.language`, JSON-LD `inLanguage`, and the
homepage's language search term.

Across pages, `translation_of` resolves once into two variables the rest of the head reads:

| Variable | What it holds |
|---|---|
| `_origin` | the original — this page, or the source it translates |
| `_siblings` | every translation of that original, **this page included** when it is one |
| `_translated_by` | siblings minus this page → JSON-LD `workTranslation` |
| `_alt_pages` | origin + siblings minus this page → `og:locale:alternate` |

`hreflang` covers origin + siblings, which always contains the page itself — that supplies the
required self-reference for free. `x-default` goes on the original. Because the set is
computed rather than paired, any number of language versions works, not just two.

## Google Scholar — the HighWire tags

`citation_title`, one `citation_author` per name, `citation_publication_date`,
`citation_volume`, `citation_issue`, `citation_firstpage`/`citation_lastpage`,
`citation_publisher`, `citation_issn`, `citation_isbn`, `citation_doi`,
`citation_abstract_html_url`, `citation_language`, `citation_cover_date`.

The venue tag is **not fixed**: `publication_types.yml` says which one this type uses
(`citation_journal_title`, `citation_conference_title`, `citation_book_title`), and a type
with no `citation_venue` emits none.

**The page-range expansion.** Scholar reads first/last page as literal numbers, so a
Chicago-condensed `pages: "301–9"` would claim a nine-page-long article ending at page 9. The
head splits on the dash and, when the last part is shorter than the first, borrows the missing
leading digits — `309`. En dash, em dash and hyphen are all normalised first. The visible
citation keeps `301–9`; only the meta tag is expanded.

`citation_author` falls back to `Dario Rodighiero` when `author` is absent, so an entry always
declares one.

## Zotero import

Zotero's Embedded Metadata translator reads the same tags, and **resolves the item type from
the HighWire venue tag first**:

| Tag present | Zotero item type |
|---|---|
| `citation_journal_title` | journalArticle |
| `citation_conference_title` | conferencePaper |
| `citation_book_title` | bookSection |
| none | falls back to `DC.type` |

That fallback is why the `dc` values in `publication_types.yml` are chosen for what Zotero
maps **firmly** rather than for DCMI precision: `map` → map, where the broader `image` leaves
Zotero guessing at artwork. `book` and `interview` already match Zotero item types by name.

One imprecision is left in place knowingly: a `magazine` piece carries
`citation_journal_title`, so Scholar and readers get the venue — which pins it to
journalArticle rather than magazineArticle. The venue is worth more than the type here.

## Dublin Core

`DC.title`, one `DC.creator` per author, `DC.description`, `DC.source` (the venue), `DC.date`,
`DC.type` (from the taxonomy, falling back to `text`), `DC.format`, `DC.language`,
`DC.identifier` (the URL, plus the DOI as a second one when present), `DC.publisher`, and
`DCTERMS.isPartOf` pointing at the site.

`DC.publisher` is the front-matter `publisher` when present, falling back to
`Dario Rodighiero` for self-published pages.

## Dates

| Tag | Source |
|---|---|
| `article:published_time` | `year`, as `YYYY-01-01`; omitted when `Forthcoming` |
| `article:modified_time` | `commit_date` — the file's last commit |
| `citation_cover_date` | `year`, as `YYYY-01-01`; omitted when `Forthcoming` |

Anything derived from `year` is skipped for `Forthcoming`, since `Forthcoming-01-01` is not a
date. `commit_date`'s own no-git fallback accepts only a four-digit year and otherwise falls
through to today.

## The homepage's own tags

Title and description are two literal `assign`s at the very top of `home.html` — the only
page whose description is written by hand rather than derived. It also carries
`profile:first_name` / `last_name` / `username`, three `<link rel="me">` (GitHub, LinkedIn,
ORCID), `<link rel="image_src">`, and `DCTERMS.modified` from `site.time`.

Its `og:image` is always the portrait; a publication's is `thumb`, falling back to the same
portrait, so no card is ever blank. Both emit `og:image:width`/`height` — from
`| image_size` for a `thumb`, hardcoded `1200×800` for the portrait.
