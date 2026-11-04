# Author identifiers

Run `uv run scripts/fetch-orcids.py` to refresh `_data/people.json` from
Crossref's public DOI records, falling back to DataCite for DOIs outside Crossref.
Commit the snapshot with any template changes;
Jekyll reads it locally, with no network dependency for builds or visitors.

The importer only accepts a unique, complete author-name match within the
publication's own DOI record and a valid ORCID checksum. It records source URLs,
keeps previously verified identifiers when a record is unavailable, and aborts on
conflicting identifiers. Initials and spelling variants are left unresolved by
the importer. It does not overwrite publication text or metadata.

The snapshot also contains manually verified identities from institutional
profiles, publisher pages and public ORCID records. Each entry records its evidence
in `sources`; check affiliations or publications as well as the name before adding
one. A spelling variant can have its own exact-name key when those sources verify
that it is the same person. The importer preserves these entries and their sources.
An unlinked contributor does not imply they have no ORCID, only that it has not
been verified. `orcid-review.md` records the remaining names from the latest audit.

Publication credits and JSON-LD look up the exact credited name. Dario's identity
continues to come from `site.orcid` in `_config.yml`.

# Scholar audit

Run `uv run scripts/audit-scholar.py` to check the live publication pages,
homepage links, robots.txt and sitemap against the current publication records.
It writes `scripts/scholar-audit.md` and a detailed JSON snapshot in
`/tmp/rodighiero-scholar-audit.json`. Network access is required. This checks
technical readiness, not membership of Google Scholar’s index. Publisher comparisons
and verified corrections are documented separately in `scholar-review.md`.

Run `uv run scripts/audit-scholar.py --site-dir _site --strict` after a Jekyll
build to check the generated site without network requests. Deployment runs the
same check. Technical errors fail the command; forthcoming dates, editor-only
works and publication types needing scholarly eligibility review remain advisory.
Local reports default to `/tmp/rodighiero-scholar-build-audit.md` and `.json`, so
they do not overwrite the live audit. Use `--report` and `--snapshot` to choose
other destinations. See `seo-review.md` for the latest implementation review.
