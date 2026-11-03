# Author identifiers

Run `uv run scripts/fetch-orcids.py` to refresh `_data/people.json` from
Crossref's public DOI records. Commit the snapshot with any template changes;
Jekyll reads it locally, with no network dependency for builds or visitors.

The importer only accepts a unique, complete author-name match within the
publication's own DOI record and a valid ORCID checksum. It records source URLs,
keeps previously verified identifiers when a record is unavailable, and aborts on
conflicting identifiers. Initials, spelling variants, and publications outside
Crossref are left unresolved. It does not overwrite publication text or metadata.

Publication credits and JSON-LD look up the exact credited name. Dario's identity
continues to come from `site.orcid` in `_config.yml`.
