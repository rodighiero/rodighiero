# SEO and Google Scholar TODO

Remaining work from the independent review of commit `47cf813` on 4 November 2026.
Citation corrections for Surprise Machines, Four Guiding Principles, and
Super-Vision are complete and pushed in `ac7cb21`.

This file lives under `scripts/`, which Jekyll excludes from the published site.

- [ ] **Verify actual Scholar coverage.** Search exact titles for several dozen
  representative papers and inspect “All versions” for personal-site copies.
  Record the date, query, observed result and version URL. Distinguish inaccessible
  search results from missing papers. HTTP 200, ordinary Google results, and
  `site:` result counts do not establish Scholar inclusion or exclusion.

## Sources and validation

- [Google Scholar inclusion guidelines](https://scholar.google.com/intl/en/scholar/inclusion.html)
- [Google language-version guidance](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Zotero Embedded Metadata translator](https://github.com/zotero/translators/blob/master/Embedded%20Metadata.js)

For implementation changes, run `bundle exec jekyll build` followed by
`uv run scripts/audit-scholar.py --site-dir _site --strict`, and independently
inspect the affected rendered tags. An audit pass is not proof of Scholar indexing.
Follow the repository's publication/network instructions if publication bodies
are changed.
