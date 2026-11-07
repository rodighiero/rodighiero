# Search Console review — 7 November 2026

Reviewed the signed-in Search Console property in Safari and exported the
Performance and 404 reports. This covers Google organic search, not on-site
visitor behaviour or GoatCounter traffic. No live site or Search Console
settings were changed during the review. Implementation is recorded below.

## Implemented after review

- Added 76 reviewed migration routes in `_data/legacy_redirects.yml`: 74 of the
  81 confirmed 404 URLs, plus the two shortened publication paths in the
  crawled-but-unindexed report. Categories open the matching gallery filter;
  publication routes go directly to their canonical publication.
- The seven unresolved historical paths are `/(2022)`, `/Affinity-Map`,
  `/Surprise-Machines-2`, `/Visual-Communication`, `/Filter`, `/Header` and
  `/Lexical-Cartography-of-Scientific-Communities`. They remain 404 because the
  evidence reviewed does not identify a unique replacement (some are fragments).
- Added curated navigation connecting six Analogous City maps, language versions
  and research publications. It replaces automatic related links on those pages.
- Added focused search/social descriptions to Extending Museum, Digital Habitus
  and Visual Abstraction. Scholarly titles, citation abstracts, publication
  bodies, translation identities and the generated network remain unchanged.
- Verified the Jekyll build, strict metadata audit of all 71 publications,
  all 76 rendered redirects and navigation for all six series members.

## Search performance

Web search, 5 August–4 November 2026: 430 clicks, about 27,200 impressions,
1.6% CTR, average position 8.6.

| Period | Clicks | Impressions | CTR |
| --- | ---: | ---: | ---: |
| 10 September–7 October | 143 | 7,272 | 1.97% |
| 8 October–4 November | 114 | 5,734 | 1.99% |

Clicks fell 20.3% and impressions 21.1%, while CTR stayed essentially flat.
This establishes a visibility/demand decline, not its cause. These small counts
do not justify a broad title rewrite or establish an algorithmic penalty.

The homepage received 81 clicks. URLs containing `analog` or `rossi` received
166 clicks, 38.6% of the total, spread across maps, translations and articles.
The first-edition English map alone received 70 clicks from 1,607 impressions.
Keep those distinct works and language versions intact; prioritize useful
connections between editions, the map and the associated research.

Candidates for a focused query/snippet review:

| Page | Clicks | Impressions | CTR | Average position |
| --- | ---: | ---: | ---: | ---: |
| Extending Museum Beyond Physical Space | 42 | 2,859 | 1.47% | 6.44 |
| Digital Habitus | 7 | 920 | 0.76% | 9.14 |
| Visual Abstraction | 4 | 498 | 0.80% | 6.01 |

These are investigation candidates, not proof of bad snippets: query intent,
country, search appearance and ranking also affect CTR. For example, the exact
query `visual abstraction` had 157 impressions, one click and position 6.39.
Inspect the actual search results and page-specific query sets before changing
the visible lead or description; preserve scholarly titles and citation tags.

## Highest priority: restore moved publication URLs

The indexing report, last updated 23 October, lists 106 404 URLs. A live HTTP
check on 7 November found 81 still returning 404 and 25 now returning HTML
redirect stubs to current publications. Do not count those 25 as outstanding
failures simply because the report has not refreshed.

The accompanying `search-console-broken-urls-2026-11-07.csv` records all 81
current failures and candidate replacements for 57 with a unique existing slug
prefix or alias match. These candidates require review before implementation.
Many are former `/projects/<slug>.html` URLs and truncated publication slugs.

Examples:

- `/projects/printing-walkable-visualizations.html` → `/printing-walkable-visualizations`
- `/ethical-and-aesthetical-questions-on-stock-images-the-case-o` → `/ethical-and-aesthetical-questions-on-stock-images-the-case-of-ais-depictions`
- `/projects/four-guiding-principles-for-rethinking-organizational-charts.html` → `/four-guiding-principles-for-rethinking-organizational-charts`

Use explicit, reviewed mappings to the actual replacement. The existing
`publication_redirect.rb` supports HTML refresh/canonical aliases on GitHub
Pages; server-side permanent redirects would require hosting support. Avoid
redirect chains. Review retired category routes separately; a category archive
may have a useful matching gallery filter. Junk fragments and removed content
without a replacement can appropriately remain 404.

Google recommends a permanent redirect when a page has moved or has a clear
replacement, and 404/410 where no equivalent content remains:
https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors

## Other indexing and health findings

- 73 indexed URLs; the report's 127 excluded URLs are not 127 broken current
  publications. Exclusions include old URLs, aliases and utility pages.
- The one reported redirect error is the HTTP Surprise Machines URL, last
  crawled 15 June. It now reaches the HTTPS publication with HTTP 200.
- Three “crawled, currently not indexed” examples are the RSS feed and two
  historical shortened publication paths. The feed does not need search
  indexing; check the short paths for redirects to their complete URLs.
- Five noindex examples are old checkout/cart/followingframe routes, last
  crawled in February 2025. These do not demonstrate that current publications
  are blocked and should not be made indexable indiscriminately.
- Sitemap: Success, last read 5 November, 72 discovered pages.
- HTTPS: 70 HTTPS URLs and zero non-HTTPS issues in the overview.
- Breadcrumbs: 69 valid, zero invalid. ProfilePage: one valid, zero invalid;
  historical dateModified warning passed with zero affected items.
- Core Web Vitals: no field data for mobile or desktop. This is inconclusive
  about speed, not a passing performance score. A separate lab measurement is
  needed before recommending performance changes.
- Links report: 132 external links, with 121 attributed to the homepage, and
  479 internal links. This is Google's reported sample, not an exhaustive link
  inventory. Most reported external links point at the homepage; clear internal
  paths from it to the publications remain useful. No link-removal or disavow
  action is supported by this overview alone.

## Suggested order

1. Review and restore the moved-publication URLs listed in the CSV.
2. Inspect query intent and actual snippets for the high-impression pages above.
3. Strengthen useful navigation among the popular Rossi maps and related research.
4. Measure field/lab performance separately and review the next comparable
   28-day period after deployment. Do not attribute changes to edits before
   collecting post-change data.

Search Console report entry points:

- https://search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Adariorodighiero.com
- https://search.google.com/search-console/index?resource_id=sc-domain%3Adariorodighiero.com
- https://search.google.com/search-console/sitemaps?resource_id=sc-domain%3Adariorodighiero.com
