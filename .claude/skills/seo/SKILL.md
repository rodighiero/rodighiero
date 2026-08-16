---
name: seo
description: Everything the site declares to machines rather than to readers — the two layouts' head tags, JSON-LD, hreflang and translation sets, the Google Scholar and Dublin Core citation tags, Zotero import, ISSN/ISBN, sitemap.xml, robots.txt, URL aliases and the 404. Use when adding a publication type, an identifier, a translation or a redirect alias, when a social card unfurls wrong or blank, when Scholar or Zotero imports an entry as the wrong item type, when a page's structured data fails validation, or when deciding what a new front-matter field should emit.
---

# The metadata object

Nothing in this skill is visible on the page. Every surface here is read by a machine, and
every mistake stays invisible until it shows up in a search result, a pasted link, or a
botched Zotero import — which is why the rules below are written down rather than rederived.

Four consumers, from one set of front-matter fields:

| Consumer | Reads |
|---|---|
| **search engines** | `<title>`, description, canonical, robots, JSON-LD, `sitemap.xml` |
| **social unfurlers** | Open Graph + Twitter Card |
| **Google Scholar** | the HighWire `citation_*` tags |
| **Zotero** | the same HighWire tags, falling back to `DC.type` |

## The one idea

**Every machine-facing claim is derived, never typed twice.** There is one `thumb` feeding
both the homepage card and the social image, so the two cannot diverge. The type taxonomy —
Schema.org `@type`, `DC.type`, which `citation_*` venue tag, how the venue is modelled —
lives once in `_data/publication_types.yml`. `lang` drives five separate declarations.
`commit_date` drives three. A new front-matter field earns its place by what it lets the page
*derive*, not by being present.

The corollary is that the front matter is the interface: to change what a page declares, you
usually edit `_data/publication_types.yml` or a plugin, not the sixty-odd publication files.

## Where things live

| Concern | File |
|---|---|
| Tags both `<head>`s share verbatim | `_includes/site-head.html` |
| Homepage tags + the `WebSite`/`ProfilePage`/`Person` graph | `_layouts/home.html` (head) |
| Publication tags + the work's JSON-LD | `_layouts/publication.html` (head) |
| `schema` / `dc` / `citation_venue` / `container` per type | `_data/publication_types.yml` |
| Person nodes, and Dario's ORCID `@id` | `_includes/jsonld-person.html`, `jsonld-people.html` |
| URL discovery and consolidation | `sitemap.xml`, `robots.txt`, `_plugins/publication_redirect.rb` |
| Which images a publication declares | `_plugins/publication_figures.rb` |
| `lastmod` / `dateModified` / `article:modified_time` | `_plugins/system_commit_date.rb` |
| RSS ordering | `_plugins/publication_date.rb` (consumer is jekyll-feed) |
| The missing-page case | `404.html` |

Per-tag inventory: `reference/head.md`. The structured-data graphs: `reference/jsonld.md`.
Sitemap, robots, aliases, feed and 404: `reference/discovery.md`.

## Operations

### Add or change a publication type
Add a key to `_data/publication_types.yml` with `label`, `schema`, `dc`, optionally
`citation_venue` and `container`. Those five keys are the whole contract — no layout branches
on a type name. Pick `dc` for **what Zotero maps firmly**, not for the most precise DCMI term
(`map`, not `image`; `image` leaves Zotero guessing at artwork). Pick `container` by asking
what `venue` names for that type: a serial (`periodical`), the book the work sits inside
(`book`), or the press itself (omit, and `venue` stays the publisher). See
`reference/jsonld.md` before choosing.

### Add an ISSN or ISBN
`issn:` / `isbn:` in the front matter; ISBNs unhyphenated, since hyphenating one correctly
needs the registrant-range tables. `publication_validator.rb` checks the shape **and the
check digit** (ISSN mod-11, ISBN-13 mod-10, ISBN-10 mod-11), so a transcription slip — the
realistic failure — surfaces in the build log. It only *warns*, so read the log: a bad
identifier still ships. Sources: Crossref by DOI, a Zotero
export of Dario's library, the journal's own site, a library registry, or Dario. Coverage is
partial **by design**: a venue where none could be confirmed carries no field, because a
wrong identifier is worse than a missing one.

### Add a translation
The translation carries `translation_of: <slug-of-original>`; the original carries nothing.
Everything else — reciprocal `hreflang` with `x-default` on the original,
`og:locale:alternate`, JSON-LD `translationOfWork` / `workTranslation` — is resolved from
that one field, for any number of language versions. Also set `lang:`, which drives
`<html lang>`, `og:locale`, `citation_language`, `DC.language` and `inLanguage`.

### Add a URL alias
`redirect_from:` on the publication (a string or a list of site-absolute paths).
`publication_redirect.rb` emits a stub carrying an absolute `rel=canonical` on the real page,
a zero-delay `<meta refresh>` and a `location.replace` — and **deliberately no `noindex`**;
see `reference/discovery.md` for why the two would contradict each other. Stubs stay out of
`sitemap.xml` on purpose — an alias is not a URL to declare.

### Change the homepage's own identity
The bio prose, job title, affiliations, `sameAs` and `knowsAbout` are literals in
`_layouts/home.html`'s `@graph`, not derived from anything. The masthead bio in `README.md`
is a *separate* text — changing one does not change the other, and they are allowed to differ
in register, but not in fact.

### Check what a page actually emits
Build, then read `_site/<slug>.html`. Liquid whitespace control makes the head hard to read
in source but the output is plain. Validate structured data at
`https://validator.schema.org/` or Google's Rich Results Test by pasting the rendered JSON-LD,
not the template.

## Invariants — don't break these

- **One author identity.** Every name renders through `jsonld-person.html`, which stamps
  Dario's ORCID as his `@id` — identical to the `Person` `@id` in the homepage `@graph` (the
  value is in `reference/jsonld.md`, and in the include itself). That shared identifier is the
  only thing telling a crawler the author of sixty-odd pages and the subject of the homepage
  are one entity. Without it each page declares an unrelated person who happens to share a name.
- **Every byline role goes through `jsonld-people.html`**, not just `author` — `editor`,
  `translator`, and `interviewer`/`preface` folded into `contributor`. That is what keeps
  Dario in the graph of works he did not author (the interviews, the two *Analogous City*
  maps), where it is his only appearance on the page.
- **Two descriptions, two budgets.** `description` must fit a search snippet, so it stays the
  22-word/160-char truncation; `abstract` has no budget and carries the abstract whole. Split
  on `<!--more-->` **before** `strip_html` — stripping tags takes the comment with it, and the
  abstract then silently becomes the entire article.
- **`issn` only ever lands on a `Periodical`.** Schema.org does not define it for `Book`. An
  `isbn` lands on the `isPartOf` book where the type has a container, and on the entity itself
  where it does not — there the work *is* the book.
- **Scholar reads page numbers as literal integers**, so a Chicago-condensed `pages: "301–9"`
  is expanded to `citation_lastpage: 309` by borrowing the leading digits. The *visible*
  citation keeps the condensed form. Don't "fix" one to match the other.
- **`og:image` is never blank** — `page.thumb`, falling back to the portrait.
- **The `hreflang` set always contains the page itself.** A self-reference is required; it
  comes for free from listing origin + siblings, so don't "optimise" the page out of its own
  list.
- **`404.html` carries no `rel=canonical`.** Pointing one at the homepage would ask crawlers
  to consolidate every missing URL into it. It also breaks analytics: `count.js` derives its
  path from `link[rel=canonical]` when that points at this host, so every 404 would be logged
  as `/`.
- **The homepage's `lastmod` is not `HEAD`.** It is the last commit touching a path that
  reaches `_site`, so committing prose about the code beside the code does not tell crawlers
  the page changed.
- **The sitemap declares `figures`, not `thumb`** — what the page actually shows.
  `images/@cards/` copies are excluded as crops, not content. They are *not* thereby
  deindexed; they remain on the page and as `og:image`.
- **Don't reintroduce dead sitemap fields.** `changefreq` and `priority` (unread since 2023),
  and `image:title` / `caption` / `license` / `geo_location` (discontinued August 2022).

## Troubleshooting

| Symptom | Cause |
|---|---|
| Social card shows the portrait on a publication | no `thumb` in the front matter — the fallback fired |
| A visible `&amp;#x2019;` in a search snippet or card | a hex numeric entity reached `escape_once` without `decode_numeric_entities` |
| JSON-LD `abstract` is the whole article | the `<!--more-->` split ran after `strip_html` |
| Zotero imports a chapter as a journal article | `citation_venue` in `publication_types.yml` points at the wrong HighWire tag — it wins over `DC.type` |
| Zotero imports as "Document" or guesses artwork | no venue tag *and* a `dc` value it cannot map |
| A magazine piece imports as journalArticle | known and accepted — it carries `citation_journal_title` so the venue survives |
| Scholar shows a one-page article | `citation_lastpage` missing or shorter than `citation_firstpage` |
| A translation shows no alternates | `translation_of` names a slug that does not resolve — the validator warns about this by name |
| `dateModified` is today on an old entry | `year: Forthcoming` (no valid date to fall back to) or the deploy checked out shallow — `deploy.yml` needs `fetch-depth: 0` |
| Build aborts on a publication | `publication_validator.rb` **error** — see the **`publication`** skill. An ISSN/ISBN only ever *warns*, so a bad one ships unless the log is read |
| An alias 404s | the redirect stub was skipped — the **`plugins`** skill has the two reasons and the warning to look for |
