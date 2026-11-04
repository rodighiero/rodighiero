# SEO and Google Scholar review — 4 November 2026

The existing site has a strong technical foundation: each publication has its own
server-rendered page, canonical URL, visible title and lead/abstract, HighWire
citation metadata, JSON-LD, and a direct HTML link from the homepage. Publication
URLs are listed in the sitemap and robots.txt permits crawling. These mechanisms
already support ordinary search discovery and Scholar's technical requirements.

## Changes ready for deployment

- `citation_author` and `DC.creator` now name actual authors only. The editor-only
  *From Wisdom to Data* previously labelled its four editors as authors, contrary
  to [Scholar's author-tag guidance](https://scholar.google.com/intl/en/scholar/inclusion.html).
  Each credited editor now has a separate `citation_editor` and `DC.contributor`;
  JSON-LD continues to use `editor`. Zotero explicitly supports
  [citation_editor](https://github.com/zotero/translators/blob/master/Embedded%20Metadata.js).
- `citation_abstract` carries the full lead/abstract already displayed on the
  publication page. Zotero can import it instead of relying on the short search
  description. This tag is a citation-export improvement, not an additional
  Scholar inclusion requirement.
- The existing audit now accepts `--site-dir _site --strict`, checking the built
  HTML without network requests. It checks source metadata, author/editor roles,
  descriptions, canonical URLs, JSON syntax, abstract visibility, HTML full-text
  claims, translation self-links, PDF location, robots rules, homepage links and
  sitemap inclusion. Deployment runs this check before uploading the site.

## Verification

- Jekyll build passed; all 71 generated publication pages passed the strict audit.
- A separate temporary build copy with a removed author tag, `noindex`, and a
  robots.txt block was rejected with the three expected technical errors.
- All 71 live publication URLs returned HTTP 200. The homepage, robots.txt and
  sitemap also returned HTTP 200; shared discovery checks passed. The live
  comparison found only the expected pending changes: 71 new complete-abstract
  tags, editor tags on 20 pages, and corrected authorship on the editor-only book.
- Changes are local and have not been deployed. Detailed local and live snapshots
  from this review are `/tmp/rodighiero-scholar-build-audit.json` and
  `/tmp/rodighiero-scholar-live-audit.json`, with Markdown reports alongside them.

## Remaining editorial and indexing work

Two forthcoming papers have no verified publication year. Preserve that status
until their actual details are available. Maps, magazines, interviews, edited
volumes and catalogs require content review before treating them as eligible
scholarly papers. These are advisory findings, not broken metadata.

The automated comparison establishes that the declared abstract is visible; it
does not establish that every lead is the complete original author-written
abstract. Earlier publisher spot checks and external PDF findings remain in
[scholar-review.md](scholar-review.md). External repository PDFs stay visible
links: Scholar's `citation_pdf_url` must refer to the abstract's own directory.

Scholar index membership and ranking were not verified in this review. After
deployment, check exact paper titles in Scholar and inspect “All versions”.
Google cautions that `site:` result counts are unreliable for coverage and that
updates to existing records can take 6–9 months; see its
[inclusion and troubleshooting guidance](https://scholar.google.com/intl/en/scholar/inclusion.html).
