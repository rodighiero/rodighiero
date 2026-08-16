---
name: publication
description: Every operation on a publication — the Markdown files in _publications/, the publication page they render into, and everything downstream. Use for adding a new entry, editing front matter or body text, adding a translation, adding or replacing images and thumbnails, adding figures or tables, styling a data table or an equation, fixing a dead reference, renaming or retiring an entry, or checking why the build aborts on one. Which field to type is here; what that field then declares to machines is the seo skill.
---

# The publication object

One Markdown file in `_publications/` **is** the publication. Its front matter drives the
card, the page, the citation, the RSS entry, the sitemap, the JSON-LD, and its position in
the similarity network. There is no database and no per-page layout declaration —
`layout: publication` comes from `defaults:` in `_config.yml`.

The slug is the filename. It is also the URL, the `images/<slug>/` folder name, the
`images/@cards/<slug>.webp` name, and the key other entries reference in `translation_of`
and `redirect_from`. Renaming a file means renaming all of those.

| Reference | Holds |
|---|---|
| `reference/front-matter.md` | field-by-field schema, per type |
| `reference/images.md` | image layout, compression, the portrait ladder, the icon set |
| `reference/page.md` | `_layouts/publication.html` — the figure, table and equation vocabulary the bodies are written against |
| `reference/naming.md` | how `_includes/` are named, and the renames already settled |

## Adding a publication — the whole sequence

1. **Write `_publications/<slug>.md`.** Slug = lowercased, hyphenated title. Front matter per `reference/front-matter.md`; body is the abstract (or lead + `<!--more-->` + full text).
2. **Put images in `images/<slug>/`** — numbered `fig_00N.webp` for body figures, plus `cover.webp` only when the card image is not one of the figures.
3. **Point `thumb:`** at one of them, path relative to `images/` (`<slug>/fig_002.webp`).
4. `python3 scripts/optimize-images.py` — re-encodes new WebPs at method 6, visually lossless, idempotent. `--dry-run` to preview.
5. `python3 scripts/generate-thumbnails.py` — writes `images/@cards/<slug>.webp`, the only image set the homepage loads.
6. `bundle exec jekyll build` — `publication_validator.rb` **aborts on error**, so this is the check that matters.
7. `KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py` — the new entry has no node, no `related`, and no cluster membership until this runs. See the `network` skill.

Steps 4–7 are also what a *changed body* or a *changed image* needs; a front-matter-only
edit that doesn't touch `thumb` or the abstract needs only step 6.

## Operations

### Edit an existing entry
Body text changes shift its embedding, so they need a network rebuild. Front-matter
metadata (venue, DOI, ISSN, pages) does not. Either way, every edit bumps the file's
`commit_date` — so avoid sweeping the whole corpus for a cosmetic reason. What that value
feeds: the **`plugins`** skill (`system_commit_date.rb`).

### Add a translation
The translation is its own file with its own slug and its own front matter, carrying
`lang: it|fr` and `translation_of: <original-slug>`. It shares the original's `thumb`.
That one field then drives the whole alternates set (the **`seo`** skill) and the forced
dashed network edge (the **`network`** skill, which also explains why a translation is
never embedded).

### Add figures or a table
Figures: `{% include figure-single.html src="/images/<slug>/fig_00N.webp" caption="…" %}`,
or `figure-group.html` with a pipe-delimited `images=`. Width modifiers: `narrow` (33%),
`half` (50%), `three-quarter` (75%), `wide` (~990px breakout), `full` (images only).
Tables wrap a Markdown table in `<figure class="data-table" markdown="1"> … <figcaption>Table N. …</figcaption></figure>`
— the `markdown="1"` is what opts the inner table into kramdown.

The rest of the vocabulary — `wrap`, `media`, `bordered`, the `equation` pair, how captions
are sized and what `wide` actually breaks out of — is `reference/page.md`.

Only figures that appear **in the body** are declared in the image sitemap; `@cards/` copies
are excluded. Why, and by which plugin: the **`plugins`** skill (`publication_figures.rb`).

### Replace a card image
Change `thumb:`, rerun `generate-thumbnails.py`. `thumb` is the single image field: it is
the homepage card **and** `og:image` / `twitter:image` / JSON-LD image. `og:image` always
points at the full-size original in the publication's own folder, never at the `@cards/`
downsize. A `cover.webp` is not displayed automatically — an entry whose content *is* one
image (book, map, magazine spread) opens its body with a caption-less lead figure.

### Fix a dead reference
Never delete or rewrite the original URL — it is what the publication cited. Append a
verified Wayback link in parentheses instead. Full procedure, and how to tell rot from a bot
wall: the **`links`** skill.

### Rename or retire an entry
Renaming the file changes the URL. Add the old path to `redirect_from:` (a string or list
of site-absolute paths) — `publication_redirect.rb` emits a refresh stub with a canonical
to the real page (no `noindex`; see the `seo` skill for why). Also rename `images/<slug>/`, delete the stale `images/@cards/<slug>.webp`,
update any `translation_of` pointing at the old slug, and rebuild the network.

### Add an ISSN/ISBN
`issn:` (ISSN-L, hyphenated, check digit may be `X`) and `isbn:` (unhyphenated). The build
verifies both check digits and warns on a slip. Both are invisible on the page and exist
purely for Google Scholar and Zotero, so the **`seo`** skill owns them — where to source one,
and why coverage is partial.

### Add a publication type
One entry in `_data/publication_types.yml` — `label`, `schema`, `dc`, optional
`citation_venue` and `container`; no template or plugin needs changing. Choosing the right
`schema` / `dc` / `container` values is a machine-metadata decision: the **`seo`** skill.

## House style

- **Curly quotes** (`“ ”`) for English and Italian; French guillemets only inside French quotations.
- **American English** in English entries (`livable`, not `liveable`). Italian and French entries keep their own orthography.
- **Chicago author-date** throughout, in three places that are not the same thing:
  - the **bibliography** — a `## References` (or `Bibliography` / `Références` / `Bibliographie`) section of `- ` bullets, in 57 of the 64 files: `Bertin, Jacques. 1981. *Graphics and Graphic Information-Processing*. Berlin and New York: De Gruyter.`
  - **inline citations** — parenthetical `(Author Year)`, no comma before the year;
  - **footnotes** — kramdown (`[^1]` … `[^1]:`), for discursive notes rather than for bare references.

  The network scrubber strips the bibliography section, the footnote definitions and the parenthetical asides before embedding, so citation formatting never influences a similarity score.
- `venue` is type-dependent: for a chapter it is the **book title** (press → `publisher`); for a book or map it *is* the press.

## Validation

`bundle exec jekyll build` runs `publication_validator.rb` at high priority. It **errors**
(aborting the build) on: a missing required field (`title`, `year`, `venue`, `type`,
`thumb`, and `author` unless `editor` is present), a `year` that is neither four digits nor
`Forthcoming`, a `type` absent from `publication_types.yml`, or a `thumb` missing from
disk. It **warns** on a DOI that isn't a URL, an out-of-range `month`/`day`, an ISSN or ISBN
that fails its shape or its check digit, and a `translation_of` naming no publication.
Warnings ship — read the log.

Broken external links are a separate, scheduled concern — a red `links.yml` run is
maintenance, not a broken build. See the `links` skill.

## Invariants — don't break these

- Don't hand-edit `_data/network.json`, `_includes/network-*.svg` or anything in `images/@cards/` — all are generated, and a hand-edit is silently reverted by the next rebuild.
- Don't add a second image field. There is one, `thumb`, and the card and social preview must not diverge.
- Don't rename `figure-single` / `figure-group`: they are called from nearly every publication, so a rename rewrites the corpus and bumps every `commit_date`. Count the call sites before arguing otherwise — `/usr/bin/grep -ro "include figure-" _publications | /usr/bin/wc -l`.
- Don't put a source image outside its publication's own folder.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Build aborts naming a publication | a required field is missing, or `year` / `type` / `thumb` is invalid — the validator's message names the file and the field |
| A new entry has no `related` list and sits in no cluster | the network was not rebuilt after it was added |
| Card image is right, social preview is wrong (or vice versa) | impossible by construction — both read `thumb`; if they differ, one surface is reading a stale `@cards/` copy, so rerun `generate-thumbnails.py` |
| A table renders as literal pipes | the wrapping `<figure>` is missing `markdown="1"` |
| A figure is missing from the image sitemap | it isn't in the body — only body figures are declared |
