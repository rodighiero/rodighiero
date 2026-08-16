# Publication front matter

`layout` is never declared — it comes from `defaults:` in `_config.yml`.

## Required

| Field | Notes |
|---|---|
| `title` | quoted; question marks and colons are fine |
| `year` | four digits, or `Forthcoming` (which sorts first everywhere) |
| `venue` | **type-dependent** — see the table below |
| `type` | a key of `_data/publication_types.yml`: book, chapter, journal, conference, magazine, interview, map |
| `author` | ` and `-joined; may be replaced by `editor` when Dario did not author |
| `thumb` | path under `images/`, always inside the publication's own folder |

## What `venue` means, per type

| type | `venue` is | press goes in | JSON-LD `container` |
|---|---|---|---|
| book | the press | — | (omitted) |
| map | the press | — | (omitted) |
| chapter | the **book title** | `publisher` | `book` |
| conference | the proceedings | `publisher` | `book` |
| journal | the journal | `publisher` | `periodical` |
| magazine | the magazine | `publisher` | `periodical` |
| interview | the outlet or institution | `publisher` | (omitted) |

## Optional — enrich the citation and the search index

`editor`, `translator`, `publisher`, `place`, `volume`, `issue`, `pages`.

These do **not** appear in the visible meta line but do appear in the formatted Chicago
reference and in the homepage search haystack. `pages` may be Chicago-condensed
(`"301–9"`); the layout expands it back to a full `citation_lastpage` for Scholar while the
visible citation keeps the short form.

## Byline contributors

| Field | Renders as | JSON-LD |
|---|---|---|
| `author` | the byline | `author` |
| `editor` | "Ed." / "edited with…" | `editor` |
| `translator` | "Translated by…" | `translator` |
| `preface` | "Preface by…" | `contributor` |
| `interviewer` | "Interview by…" (interview type) | `contributor` |

Chicago cites an interview under the **interviewee**, so Dario stays `author` and the
interviewer goes in `interviewer`. All of these are searchable on the homepage. Every one
of them routes through `jsonld-people.html` → `jsonld-person.html`, which stamps Dario's
ORCID `@id` — the only thing telling a crawler that the author of sixty pages and the
subject of the homepage are one person.

## Identifiers

| Field | Visible? | Purpose |
|---|---|---|
| `doi` | yes | full `https://doi.org/…` URL |
| `issn` | no | Scholar + Zotero; ISSN-L, check digit may be `X` |
| `isbn` | no | Scholar + Zotero; unhyphenated |

Check-digit validate both before adding. Coverage is partial by design.

## Language and translation

| Field | Effect |
|---|---|
| `lang: it` / `fr` | `<html lang>`, `og:locale` (`it_IT`/`fr_FR`), `citation_language`, `DC.language`, JSON-LD `inLanguage`, and the homepage language search term (full names only — `italian`/`italiano`, `french`/`français`) |
| `translation_of: <slug>` | marks this file a translation: `hreflang` alternates with `x-default` on the original, `og:locale:alternate`, JSON-LD `translationOfWork`/`workTranslation`, and the forced dashed network edge. A translation is never embedded — it borrows its source's vector |

Absent `lang` means English. The homepage UI stays English; there is no per-language page tree.

## Other

| Field | Effect |
|---|---|
| `img_border: true` | hairline around the homepage card |
| `redirect_from` | string or list of site-absolute paths; each becomes a refresh stub canonicalised to the real page |
| `month`, `day` | validated 1–12 / 1–31; rarely used |

`page.date` is **derived**, not declared — `publication_date.rb` synthesizes it from `year`
purely as an RSS sort key (Jan 1 at noon plus offsets, so the feed reproduces the homepage
order). Don't add a `date:` field.

## Body

The body is the abstract. A **full-text** article puts the lead/abstract paragraph first,
then `<!--more-->`, then the text with `##` headings — the layout italicizes the lead, and
JSON-LD `abstract` takes exactly the part before the marker (split before `strip_html`,
since stripping tags would take the comment with them).

## Skeletons

Journal article:

```yaml
---
title: "Network Literacy: How to Understand, Design, and Read a Visual Relational Model"
year: 2025
venue: "Progetto Grafico"
type: "journal"
author: "Dario Rodighiero"
doi: "https://doi.org/10.…"
issn: "1824-1301"
thumb: "network-literacy-…/fig_001.webp"
---
```

Book chapter (note `venue` = book title, press in `publisher`):

```yaml
---
title: "Are We All Narcissists? The Pseudo-Narcissism of the Internet"
year: 2022
venue: "From Wisdom to Data: Philosophical Atlas on Visual Representations of Knowledge"
type: "chapter"
author: "Alexandre Rigal and Dario Rodighiero"
editor: "José Higuera Rubio and Alberto Romele and Dario Rodighiero and Celeste Pedro"
publisher: "University of Porto Press"
place: "Porto"
doi: "https://doi.org/10.…"
thumb: "are-we-all-narcissists-…/fig_002.webp"
---
```

Translation:

```yaml
---
title: "Alfabetizzazione delle reti: come comprendere, progettare e leggere modelli relazionali visivi"
year: 2025
venue: "Progetto Grafico"
type: "journal"
author: "Dario Rodighiero"
doi: "https://doi.org/10.…"
issn: "1824-1301"
thumb: "network-literacy-…/fig_001.webp"
lang: it
translation_of: network-literacy-how-to-understand-design-and-read-a-visual-relational-model
---
```
