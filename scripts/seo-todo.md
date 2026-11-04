# SEO and Google Scholar TODO

Remaining work from the independent review of commit `47cf813` on 4 November 2026.
Citation corrections for Surprise Machines, Four Guiding Principles, and
Super-Vision are complete and pushed in `ac7cb21`.

This file lives under `scripts/`, which Jekyll excludes from the published site.

- [ ] **Correct full-text declarations.** Replace the assumption that `<!--more-->`
  means complete full text with an explicit distinction between abstracts,
  excerpts, and full works. Review every publication currently emitting
  `citation_fulltext_html_url`, particularly *From Wisdom to Data* and
  *Mapping Affinities*. Emit the tag only for complete works; retain appropriate
  abstract metadata for excerpts. Verify generated HTML after building.

- [ ] **Strengthen `scripts/audit-scholar.py`.** The independent temporary fixtures
  passed despite a hidden abstract, incorrect first page, missing last page,
  missing language alternates, an unrelated JSON-LD headline, and an empty article
  body retaining its full-text claim. Compare pagination and structured data with
  source records, derive expected translation sets, and detect hidden abstracts
  and missing article content. Clearly distinguish source consistency, actual
  Scholar requirements, and optional citation-export conventions such as
  `citation_abstract` and `citation_editor`. Text presence alone must not be
  reported as proof of visibility or completeness.

- [ ] **Use ordered bibliography markup.** The review found 60 generated pages
  with reference headings followed by `<ul>`. Scholar documents `<ol>` for HTML
  references. Update bibliography rendering and the publication skill's house
  style; preserve the intended visual appearance with CSS. Do not claim this
  discrepancy has caused indexing failures without evidence.

- [ ] **Review shared DOIs on translations.** `_layouts/publication.html` suppresses
  identifiers when a translation shares its original's DOI. Check the bilingual
  Progetto Grafico records and preserve verified identifiers in citation exports
  where appropriate. Keep separate canonical URLs and reciprocal language links.
  The claim that suppression prevents unwanted Scholar merging remains unverified.

- [ ] **Check abstract visibility in a browser.** Inspect desktop and mobile
  publication pages, especially those placing cover images before abstract text.
  Confirm the abstract is easy to see without interaction. The review could not
  perform viewport checks because the browser host was unavailable.

- [ ] **Verify actual Scholar coverage.** Search exact titles for several dozen
  representative papers and inspect “All versions” for personal-site copies.
  Record the date, query, observed result and version URL. Distinguish inaccessible
  search results from missing papers. HTTP 200, ordinary Google results, and
  `site:` result counts do not establish Scholar inclusion or exclusion.

- [ ] **Resolve remaining editorial questions.** Verify publication status and
  dates for *Curatorial A(i)gents* and *Data Storytelling* before replacing
  `Forthcoming`. Check *From Wisdom to Data* editor ordering against the book's
  title page; the publisher listing differs from the local order. Review scholarly
  eligibility of maps, magazines, interviews, catalogs and edited volumes without
  assuming that an academic website makes every item a scholarly paper.

## Sources and validation

- [Google Scholar inclusion guidelines](https://scholar.google.com/intl/en/scholar/inclusion.html)
- [Google language-version guidance](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Zotero Embedded Metadata translator](https://github.com/zotero/translators/blob/master/Embedded%20Metadata.js)

For implementation changes, run `bundle exec jekyll build` followed by
`uv run scripts/audit-scholar.py --site-dir _site --strict`, and independently
inspect the affected rendered tags. An audit pass is not proof of Scholar indexing.
Follow the repository's publication/network instructions if publication bodies
are changed.
