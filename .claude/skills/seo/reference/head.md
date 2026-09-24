# The head tags

Three sources compose each `<head>`: `_includes/site-head.html` (verbatim on both pages), then
the page-specific block in `_layouts/home.html` or `_layouts/publication.html`.

## Shared — `_includes/site-head.html`

Everything here is page-invariant, which is the admission test: a tag whose value depends on
the page does not belong in this file.

`viewport`, `robots`, two `theme-color`s (light/dark), `color-scheme`, the RSS
`<link rel=alternate>`, `og:site_name`, `twitter:card`, the two Dublin Core schema links, and
the icon/manifest set. `<meta name="author">` is *not* here: it names the page's creators, so
each layout writes its own (Dario on the homepage, the creators list on a publication). It opens by including `_includes/site-scheme.html`, the pre-paint
`colorScheme` restore script — not metadata, but it must run before the first paint. That one
lives in its own file because `404.html` includes it directly and takes nothing else from here.

`robots` is `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1`.
Indexing was never blocked; the three `max-*` directives only lift the caps on how a result
may *render* in Search and Discover.

## The two derived strings on a publication page

Computed at the top of the head, before anything uses them:

| Assign | What it is |
|---|---|
| `_abstract` | `content \| split: '<!--more-->' \| first \| strip_html \| …` — the abstract whole, no budget |
| `_excerpt` | `_abstract \| snippet` — cut to the 160-character search-snippet budget, on a sentence end or a whole word plus `…` (see the `plugins` skill) |

`_excerpt` feeds `description`, `og:description`, `twitter:description`, `DC.description`
and JSON-LD `description`. `_abstract` feeds JSON-LD `abstract` only.

Two ordering rules are load-bearing. **Split on `<!--more-->` before `strip_html`** — an HTML
comment is a tag, so stripping first takes the marker with it and the abstract becomes the
whole article. And **`decode_numeric_entities` before `escape_once`** — `escape_once`'s
exemption regexp covers named and decimal entities but not hex, so a `&#x2019;` would
double-escape into a visible `&amp;#x2019;` in a social card. No source currently contains
one; it is a guard against an invisible failure, not a live transformation.

## `<title>`

The bare publication title, no names. Authorship is already declared three times over —
`citation_author`, the JSON-LD `author` with Dario's ORCID `@id`, the visible byline — and
Google takes the site name from the homepage's `WebSite` node, so a credit here only spent the
~60-character display budget, usually truncated off the end anyway. A fixed
`— Dario Rodighiero` suffix was rejected too: on papers he did not lead it reads as sole
authorship.

## Language and translation sets

`lang` (defaulting to `en`) drives, on one page: `<html lang>`, `og:locale`,
`citation_language`, `DC.language`, JSON-LD `inLanguage`, and the homepage's language search
term. Five of those are the bare code. `og:locale` is the exception — a lookup in
`_data/languages.yml` (`en: en_US`, `it: it_IT`, `fr: fr_FR`), which is also the list
`publication_validator.rb` refuses an unknown `lang` against, since that one declaration is
the only one an unlisted code would get silently wrong. Adding a language is a line in that
file and nothing else.

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
`citation_abstract_html_url`, `citation_fulltext_html_url` (when the body has a
`<!--more-->`, i.e. carries the full text beyond the abstract), `citation_language`.

The venue tag is **not fixed**: `publication_types.yml` says which one this type uses
(`citation_journal_title`, `citation_conference_title`, `citation_book_title`), and a type
with no `citation_venue` emits none.

**The page-range expansion.** Scholar reads first/last page as literal numbers, so a
Chicago-condensed `pages: "301–9"` would claim a nine-page-long article ending at page 9. The
head splits on the dash and, when the last part is shorter than the first, borrows the missing
leading digits — `309`. En dash, em dash and hyphen are all normalised first. The visible
citation keeps `301–9`; only the meta tag is expanded.

**Creators.** `citation_author`, `DC.creator` and `<meta name="author">` read one list: `author`,
or `editor` on an edited volume (the validator requires one of the two). Scholar has no editor
tag, so the editors stand in. The old fallback was the literal `Dario Rodighiero`, which
credited him alone with a four-editor book. JSON-LD does not take the fallback: it has a real
`editor` property, so an edited volume declares editors and no `author`. `article:author` is
one tag per name, and only for real authors.

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
| `article:modified_time` | `commit_date` — the file's last commit, as a full ISO 8601 timestamp |
| `citation_publication_date`, `DC.date`, JSON-LD `datePublished` | `year`, bare; omitted when `Forthcoming` |

**No `article:published_time` or `citation_cover_date`.** The front matter knows only the year,
and both used to emit `YYYY-01-01` — an invented 1 January that Google can print in a
snippet as the publication date. Don't reintroduce them without a real month and day.

Anything derived from `year` is skipped for `Forthcoming`, since `Forthcoming-01-01` is not a
date. `commit_date`'s own no-git fallback accepts only a four-digit year and otherwise falls
through to now.

`commit_date` is a **timestamp**, not a date: Search Console flags a bare `YYYY-MM-DD` on the
homepage's `ProfilePage` as "Invalid datetime value for dateModified". See the `plugins` skill
(`system_commit_date.rb`) before shortening it.

## The homepage's own tags

Title and description are two literal `assign`s at the very top of `home.html` — the only
page whose description is written by hand rather than derived. It also carries
`profile:first_name` / `last_name` / `username`, three `<link rel="me">` (GitHub, LinkedIn,
ORCID), `<link rel="image_src">`, and `DCTERMS.modified` from `site.data.commit_date` — the
same repo-wide date the sitemap declares for this page, not the build clock, so a deploy that
changes nothing a reader sees does not claim the page changed.

Its `og:image` is always the portrait, at a hardcoded `1200×675`. A publication's is always
`thumb` — a required field, so there is no portrait fallback — sized by `| image_size`, which is the one part still conditional: a file it
cannot parse yields no width or height rather than empty ones.
