# The eleven, in detail

Ordered by what they do, not alphabetically. Each heading gives the identifier the file
produces — which is what you are usually searching for.

## Liquid filters

### `system_image_size.rb` → `| image_size`

A pure-Ruby WebP parser returning `{ 'width' =>, 'height' => }`, so figure markup can set
`width`/`height` and avoid layout shift. No ImageMagick, no gem.

Handles the three WebP chunk types — `VP8 ` (lossy), `VP8L` (lossless), `VP8X` (extended) —
by reading the RIFF header and unpacking the dimension bits. Anything else returns
`{nil, nil}`, and so does a missing file; the templates guard on `.width` before emitting.

Results are memoised per path in a class-level cache, cleared on `pre_render` so a
long-running `jekyll serve` neither leaks nor serves stale dimensions after an image is
replaced.

It is the one `system_` file whose prefix is unambiguous: all four call sites emit a
machine-read attribute — `width`/`height` hints, `og:image:width` — never visible content.

### `publication_urls.rb` → `| autolink_urls`

Wraps bare `http(s)://` URLs in anchors when rendering full-text bodies.

The regexp is two alternatives, and the order matters:
`(<a…>.*?</a>|<[^>]*>)|(https?://[^\s <>"]+)`. Group 1 swallows existing anchors and any
other tag *first*, so a URL inside an `href`, `src` or `data-*` attribute is never rewrapped;
only group 2 — a bare URL in text — gets linked. Trailing `.,;:!?)` are peeled off the match
and re-emitted outside the anchor, so a URL ending a sentence doesn't swallow the period.

` ` is excluded explicitly because kramdown inserts a non-breaking space before the
footnote return arrow and Ruby's `\s` does not match it — without the exclusion the URL would
swallow the nbsp and whatever preceded it.

### `publication_decoder.rb` → `| decode_numeric_entities`

Turns `&#8217;` / `&#x2019;` into UTF-8 characters, applied to excerpts *before*
`escape_once`. `escape_once`'s exemption regexp covers named and decimal entities but not hex
ones, so a hex entity surviving `strip_html` would double-escape into a visible
`&amp;#x2019;` in a description meta tag.

**No publication source currently contains one**, so this is a guard, not a live
transformation — kept because the failure it prevents is invisible on the page and surfaces
only in a social card or a search snippet. Named entities are deliberately left alone:
`escape_once` handles those correctly, and decoding them would only hand it a bare `&` to
re-escape.

## Ordering and navigation

### `publication_order.rb` → `site.data.ordered_publications` + `Jekyll::OrderedPublications`

The site's single sort rule: **Forthcoming first, then year descending, title ascending within
a year.** Implemented as a sort key — `[dated ? 1 : 0, dated ? -year : 0, title.downcase]`,
where "dated" means the year matches `\A\d{4}\z`, so any non-four-digit year (not just the
literal "Forthcoming") sorts ahead of every dated work.

It reaches three places: the published `site.data.ordered_publications` for the gallery flow,
and the module itself, consumed by `publication_neighbors.rb` and `publication_date.rb`.
Naming the file after any one of the three would have lied about the other two; naming it for
the rule does not.

### `publication_neighbors.rb` → `prev_pub` / `next_pub`

A `post_read` hook giving each document its two neighbours up front, so the layout reads
`page.prev_pub` instead of scanning the collection in Liquid on each of sixty-odd pages.

Each ref is a **plain hash of url + title** — only what `publication-nav.html` reads. Storing
the neighbouring `Document` would make each pair reference the other through page data; the
hash keeps the graph acyclic.

It asks `Jekyll::OrderedPublications` for the order directly rather than reading
`site.data.ordered_publications`, because both are `post_read` hooks and calling the shared
module makes this one independent of which hook Jekyll happens to run first.

### `publication_date.rb` → `page.date`

Derives a date from `year` (+ optional `month`, `day`) so jekyll-feed's newest-first ordering
reproduces the homepage's order. **The value is a sort key, not a publication date.**

Within a year the entries are grouped in canonical order and each gets a small offset —
`Time.new(year, month, day, 12, 0, 0) + (size - 1 - i)` — so the alphabetically-first title
carries the *latest* timestamp and therefore leads the feed. Noon, so a timezone shift cannot
move the date. The offset is added as time arithmetic rather than passed as a seconds argument
to `Time.new`, which would raise once a year held more than 86,400 titles.

A non-numeric year yields `0` and is dated `site.time - i` — build time, so it sorts newest,
but never in the future, which would trip Jekyll's future-date filter and drop the page from
the build.

Its consumer is the gem, not a template in this repo.

## Decoration

### `publication_figures.rb` → `figures`

Collects the images that actually appear **inside** a publication's body, as site-absolute
paths, for `sitemap.xml` to declare. Not the `thumb`.

Generators run before rendering, so `doc.content` is still raw source — the file scans it for
`{% include figure-single.html … %}` and `{% include figure-group.html … %}` with non-greedy
regexps (bounded at the first `%}` so a caption containing `%` can't swallow the rest of the
file). The two includes pass paths differently — `figure-single` an already-absolute
`src="/images/…"`, `figure-group` a pipe-delimited `images="slug/a.webp|…"` it prefixes
itself — so both are normalised, then deduplicated per document.

Two filters at the end: anything under `images/@cards/` is dropped (generated gallery crops,
not article imagery — including where an abstract-only entry opens on its own card image), and
a path missing from disk is skipped with a warning, since a 404 in an image sitemap is a crawl
error rather than a discovery.

### `system_commit_date.rb` → `commit_date`, per document and site-wide

Per publication: that file's last commit date as `YYYY-MM-DD`, feeding sitemap `lastmod`,
`article:modified_time` and JSON-LD `dateModified`. The fallback accepts only a four-digit
`year` (as `YYYY-01-01`) and otherwise falls through to today — `Forthcoming-01-01` would be
invalid in both the sitemap and the structured data.

All per-file dates come from **one** `git log --name-only` walk keyed by path, not a
subprocess per document: 61+ forks per build otherwise. Git is invoked via `Open3.capture2`
with `chdir: @source`, so the relative paths don't depend on where Jekyll was invoked from,
and a missing `git` warns rather than raising.

Site-wide, `site.data.commit_date` is the **homepage's** `lastmod`, and it is deliberately not
`HEAD`: it is the last commit touching a path that reaches `_site`. The exclusion list is read
from Jekyll's own `exclude:` rather than kept in step by hand, with two adjustments the config
cannot supply — `UNPUBLISHED` (`.claude`, `.github`, `.gitignore`: tracked dot-paths Jekyll
drops implicitly) and `PUBLISHED_ANYWAY` (`README.md`: excluded from the build, but it *is*
the homepage bio, so a change to it really is a change to the page).

This is the `system_` prefix used properly — everything it feeds is machine-facing, even where
it also writes a tag on a page.

### `system_readme.rb` → `site.data.readme_content`

Ten lines: read `README.md` whole at `post_read`, warn if absent. `home.html` splits it into
the three bio paragraphs on `<!-- split -->` comments, so `README.md` doubles as the GitHub
repo readme.

The weak fit for its prefix — its output *is* visible masthead prose. Read the prefix here as
"sourced from a repo file rather than from the collection".

## No identifier at all

### `publication_redirect.rb` → redirect stub pages

URL **aliases**. Any page or document may list `redirect_from` (a string or a list of
site-absolute paths); each becomes a small stub carrying an absolute `rel=canonical` on the
real page, a zero-delay `<meta refresh>` and a `location.replace`.

**No `noindex`, deliberately.** A `noindex` and a `rel=canonical` are contradictory
instructions and Google resolves the conflict by picking the canonical, so the tag only argued
with the line beneath it. The refresh is what keeps an alias out of the index; the canonical
then hands the real page credit for whatever links the alias earned, which a `noindex` would
throw away.

The target is relative (`site.baseurl + item.url`, so it works locally and in production)
while the canonical is absolute (what a search engine should keep). Path rules: no extension →
`<alias>.html`, served extensionless by both GitHub Pages and `jekyll serve`; a trailing `/` →
`<alias>/index.html`. Duplicate aliases and ones not starting with `/` are skipped with a
warning naming the source file. Stubs set `sitemap: false`, and `sitemap.xml` loops
`site.publications` only.

`priority :low` so every page it might alias already exists. It scans `site.pages +
site.documents`, which is why it is the one `publication_` file broader than its prefix
claims — a `redirect_from` on a top-level page would be honoured too; today every alias
happens to sit on a publication.

Local replacement for the removed `jekyll-redirect-from` gem, so no new dependency.

### `publication_validator.rb` → the build log, and an abort

A `priority :high` generator checking every publication's front matter. **Warnings are
advisory; an error raises `Jekyll::Errors::FatalException` and aborts the build**, so bad
metadata is caught on every deploy rather than shipped.

| Check | Severity |
|---|---|
| `title`, `year`, `venue`, `type`, `thumb` present | error |
| `author` present — waived when `editor` is | error |
| `year` is four digits or `Forthcoming` | error |
| `type` is a key in `publication_types.yml` | error |
| `thumb` resolves to a file under `images/` | error |
| `month` 1–12, `day` 1–31 | warning (the value is clamped downstream) |
| `doi` starts with `http(s)://` | warning |
| `issn` matches `\d{4}-\d{3}[\dX]` | warning |
| `isbn` is 13 digits, or 10 with an `X` allowed | warning |

Both identifier checks are **shape only** — no check-digit arithmetic, so a transcribed digit
passes. Validate ISSN mod-11 / ISBN-13 mod-10 by hand before adding one. The `[\dX]` is not an
oversight: `0024-094X` (*Leonardo*) and `2073-445X` (*Land*) both end in X.
