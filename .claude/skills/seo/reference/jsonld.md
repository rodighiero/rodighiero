# Structured data

Three graphs: the homepage's `@graph`, a publication's work node, and a `BreadcrumbList` on
every publication page.

## The publication work node

`@type` comes from `publication_types.yml`:

| Type | `@type` | Why |
|---|---|---|
| `book` | `Book` | |
| `chapter`, `journal`, `conference` | `ScholarlyArticle` | peer-reviewed scholarly venues |
| `magazine`, `interview` | `Article` | not peer-reviewed, so the general type |
| `map` | `Map` | |

Fallback is `ScholarlyArticle`. The node carries `@id` (the page URL), `headline` + `name`,
the person properties, `datePublished` / `dateModified`, the container or publisher, `url`,
`sameAs` (the DOI), `pagination`, translation links, `image`, `mainEntityOfPage`,
`inLanguage`, `abstract` and `description`.

## People — the one identity that matters

`jsonld-person.html` emits a single `Person` node and gives Dario
`"@id": "https://orcid.org/0000-0002-1405-7062"` plus `url`. **That `@id` is identical to the
`Person` `@id` in the homepage `@graph`, and that is the entire mechanism** tying sixty-odd
publication pages to the homepage's subject. Break it and each page declares an unrelated
person who happens to share a name. Co-authors stay bare names — there is no stable
identifier for them, and inventing one would be worse than none.

`jsonld-people.html` wraps it into a whole person-valued property from an `" and "`-joined
front-matter field, emitting a bare node for one name and an array for several.

**Every byline role goes through it**, mapped to what Schema.org actually defines:

| Front matter | JSON-LD property |
|---|---|
| `author` (default `Dario Rodighiero`) | `author` |
| `editor` | `editor` |
| `translator` | `translator` |
| `interviewer`, `preface` | `contributor` (concatenated) |

`interviewer` and `preface` have no Schema.org equivalent, so they fold into the general
`contributor`. This is not tidiness — the interviews are cited under the interviewee and the
two *Analogous City* maps under Rossi et al., so on those pages `contributor` / `editor` is
Dario's **only** appearance in the graph. Dropping the non-author roles would remove him from
the works he did not author.

## Container vs. publisher

`venue` means something different per type, so `publication_types.yml` carries `container` to
say how to model it:

| `container` | Emits |
|---|---|
| `periodical` | `isPartOf` a `Periodical`, nested through `PublicationVolume` / `PublicationIssue` when `volume` / `issue` are known |
| `book` | `isPartOf` a `Book` — the containing book or the proceedings |
| *omitted* | `venue` names the press itself, so it stays `publisher` |

Omitted is right for `book` and `map`, whose venue is a press (Métis Presses, EPFL Archizoom),
and for `interview`, whose venue may be an institution rather than a serial.

Where `container` is set, `publisher` is emitted **only** from a real `publisher` field and is
otherwise dropped — rather than repeating the venue as an Organization that published it,
which would be a different and false claim.

The nesting is built inside-out in Liquid (issue wraps volume wraps periodical), so the
opening and closing braces are counted by matching `{% if %}` pairs. Edit it carefully; a
brace mismatch produces invalid JSON that no consumer reports back to you.

## Identifiers land on what they identify

- **`issn` only ever sits on a `Periodical` node.** Schema.org does not define `issn` for
  `Book`.
- **`isbn` sits on the `isPartOf` book** where the type has a container, and **on the entity
  itself** where it does not — there the work *is* the book.

## Translations

`translationOfWork` points at the origin; `workTranslation` lists the sibling translations.
Each nested node carries its **own** `@type` from the taxonomy (an Italian chapter of an
English chapter is a `ScholarlyArticle` in its own right), plus `@id`, `name` and
`inLanguage`. Fallback for a nested type is `CreativeWork`.

Note this is a different mechanism from the "Related publications" list at the foot of a
publication page — that comes from `network.json` and is nearest-neighbour similarity, not a
declared relationship. See the `network` skill.

## Two descriptions

`description` is the 22-word/160-char truncation the meta description uses — it must fit a
snippet. `abstract` has no budget and carries the abstract whole: on a full-text article the
lead before `<!--more-->`, which *is* the abstract; on any other entry the body, which is the
abstract already. Emitting the same string twice would waste the one field that can hold the
real thing.

## BreadcrumbList

Two levels — site title → page title. Flat by design: publications have no category pages to
sit under, so a deeper trail would invent structure the site does not have.

## The homepage `@graph`

Three nodes, cross-linked by `@id`:

| Node | `@id` | Points at |
|---|---|---|
| `WebSite` | `/#website` | — |
| `ProfilePage` | `/#profilepage` | `isPartOf` the website, `mainEntity` the Person, `primaryImageOfPage` the portrait |
| `Person` | the ORCID URI | — |

The `Person` node holds `name`, `url`, an `ImageObject` for the portrait (with
`representativeOfPage`), `description`, `jobTitle`, `worksFor`, three `affiliation`s, `sameAs`
(GitHub, Google Scholar, LinkedIn, ORCID, Zotero), `knowsAbout` and `knowsLanguage`.

All of it is **literal** — none derives from front matter or from `README.md`. A change of
affiliation or job title is edited here by hand, and the bio in `README.md` is a separate
text that must agree in fact but not in wording.

`ProfilePage.dateModified` uses `site.time` (build time), not `commit_date`. The homepage's
*sitemap* `lastmod` uses the repo-wide `commit_date` instead — see `reference/discovery.md`.
