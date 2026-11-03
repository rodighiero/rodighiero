# Scholar publisher and PDF review — 3 November 2026

See [the live technical audit](scholar-audit.md) for all 71 pages. These are
technical readiness findings. Scholar index membership could not be checked:
Scholar search was inaccessible through the web tool, and the browser host was
unavailable. Ordinary search results show site pages, but do not establish Scholar
inclusion. No pages have been labelled “not indexed” on that basis.

## Verified correction (local; deployment pending)

**Orchestrating Cultural Heritage** had a repository PDF in its `doi` field.
The PDF’s cover sheet and publisher text identify DOI
[10.1145/3603163.3609066](https://doi.org/10.1145/3603163.3609066).
The source now uses this DOI, enabling `citation_doi`, DOI-based Dublin Core
identification and the canonical work identity. The original accessible
[repository PDF](https://pure.rug.nl/ws/portalfiles/portal/780076742/3603163.3609066.pdf)
is preserved in `pdf_url`, displayed as a separate PDF button.

This external PDF is deliberately not emitted as `citation_pdf_url`. Scholar’s
[guidelines](https://scholar.google.com/intl/en/scholar/inclusion.html) require that
PDF to be hosted in the abstract page’s own subdirectory. The paper already has
server-rendered HTML full text. No copies were republished as part of this audit.

## Publisher comparisons

Sixteen public Crossref records were retrieved successfully for title, author and
year comparison. Of the other 27 DOI records attempted, 17 returned 404 (a DOI may
belong to a different registration agency) and 10 returned 429 (rate limited).
This is a partial publisher comparison, not a complete certification of all records.

Three differences were reviewed rather than copied automatically:

- **Super-Vision:** [Crossref’s deposited author order](https://api.crossref.org/works/10.1515%2FJDH-2023-0004)
  lists Sarah Kenderdine, Philippe Rivière, Dario Rodighiero. The
  [journal’s interactive article](https://journalofdigitalhistory.org/en/article/Yn8z7XNPKzy4)
  and [Groningen record](https://research.rug.nl/en/publications/super-vision-tracing-epfl-history-through-8000-doctoral-theses)
  list Dario Rodighiero, Philippe Rivière, Sarah Kenderdine, matching this site.
  Preserve the site’s order; the publisher’s records conflict.
- **The Hermeneutic Circle of Data Visualization:**
  [Crossref](https://api.crossref.org/works/10.5840%2Ftechne202081126)
  includes “Philosophy Documentation Center” as an additional organizational author.
  The site’s two named researchers were preserved; no organization was added.
- **La città analoga, second revised edition:**
  [Crossref](https://api.crossref.org/works/10.21827%2F6a5e18e30b11d)
  has a shorter title, “La città analoga: The map / de kaart”. The site’s additional
  edition qualifier was preserved; this is not an indexing blocker.

## Direct PDF access

All three existing direct PDF links returned HTTP 200 and text could be extracted
with `pdftotext`. This checks text accessibility, not a complete visual or licensing review.

| Publication | Source PDF | Size | Finding |
| --- | --- | --- | --- |
| Orchestrating Cultural Heritage | [Repository](https://pure.rug.nl/ws/portalfiles/portal/780076742/3603163.3609066.pdf) | 946,502 bytes | Readable; title, author list and DOI verified against the paper |
| Circulation of Opinions in Visualization Reading | [CEUR](https://ceur-ws.org/Vol-1658/paper3.pdf) | 676,968 bytes | Readable; first-page title, author and abstract agree with the site |
| Collective Care: VISAP ’25 Catalog | [VISAP](https://visap.net/2025/downloads/visap-2025-booklet.pdf) | 9,761,398 bytes | Above Scholar’s 5 MB file limit; an entire catalog is also not a single scholarly paper |

## Remaining limits and follow-up

- The two forthcoming entries lack a real year. Preserve this until their actual
  publication details can be verified; do not invent dates to satisfy an indexer.
- Maps, catalogs, interviews and magazine pieces are not automatically eligible for
  Scholar. Their presence on an academic website does not make them research articles.
- All 71 live pages have nonempty lead/abstract text and advertise HTML full text;
  that automated check does not prove every lead is the complete author-written abstract.
  The three publication sources reviewed above provided useful spot checks.
- This pass checked the three direct PDF links, not every publisher/repository link
  or every reference in the full texts.
- Once the DOI correction is deployed, rerun the live audit. Check Scholar manually
  using `site:dariorodighiero.com` and exact paper titles, including “All versions”.
  A paper may be grouped under a publisher version even when the personal-site copy
  is discovered. Do not interpret a missing site result alone as proof the paper is absent.
- Google notes that updates can take days to 6–9 months. This audit does not promise
  inclusion, higher ranking, or immediate recrawling.
