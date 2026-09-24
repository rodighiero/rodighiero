# The twelve, in detail

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

### `publication_decoder.rb` → `| decode_numeric_entities`, `| snippet`

Turns `&#8217;` / `&#x2019;` into UTF-8 characters, applied to excerpts *before*
`escape_once`. `escape_once`'s exemption regexp covers named and decimal entities but not hex
ones, so a hex entity surviving `strip_html` would double-escape into a visible
`&amp;#x2019;` in a description meta tag.

**No publication source currently contains one**, so this is a guard, not a live
transformation — kept because the failure it prevents is invisible on the page and surfaces
only in a social card or a search snippet. Named entities are deliberately left alone:
`escape_once` handles those correctly, and decoding them would only hand it a bare `&` to
re-escape.

`snippet` cuts the abstract to the 160-character description budget, ellipsis included. It
replaced `truncatewords: 22 | truncate: 160`, which cannot see punctuation and so shipped
endings like `Consolascio,...`, `global....` and `starting from ...`. It ends on a full
sentence when one closes in the back half of the budget; otherwise it cuts at the last whole
word, drops dangling punctuation and appends a single `…`. Text already within budget passes
through untouched. It shares the file because it guards the same surface — the description
tags, read only in a snippet or a card — rather than earning a thirteenth plugin.

## Ordering and navigation

### `publication_order.rb` → `site.data.ordered_publications` + `Jekyll::OrderedPublications`

The site's single sort rule: **year descending; within the current year, newest-added first;
within every other year, title ascending.** Forthcoming — any year not matching `\A\d{4}\z` —
counts as the current year (`year_of`), so it sits among this year's additions by when it was
added instead of pinned above everything, and giving it its real year later leaves it in place.
The sort key is `[-year, recency, title.downcase]`, with `recency` the negated epoch of the
commit that added the file for the current year and `0` for every other. The add dates come
from one `git log --name-status --diff-filter=AR` walk; a rename hands the new path the old
one's add date, so renaming a publication never moves it. The current-year test is
`Time.now.year`, so on 1 January the outgoing year turns alphabetical by itself.

It reaches three places: the published `site.data.ordered_publications` for the gallery flow
and for `publication_date.rb` (a Generator, so it runs after the hook that publishes it), and
the module itself, called by `publication_neighbors.rb` (a `post_read` hook like this one). The
git walk is redone per call rather than memoized, since a module-level memo outlives the build
under `jekyll serve`.
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

Derives a date from `year` — the only date a publication carries — so jekyll-feed's
newest-first ordering reproduces the homepage's order. **The value is a sort key, not a
publication date.**

Within a year the entries are all dated to January 1st and each gets a small offset —
`Time.new(year, 1, 1, 12, 0, 0) + (size - 1 - i)` — so whichever title the homepage puts
first carries the *latest* timestamp and therefore leads the feed. Noon, so a timezone shift cannot
move the date. The offset is added as time arithmetic rather than passed as a seconds argument
to `Time.new`, which would raise once a year held more than 86,400 titles.

Years are grouped by `Jekyll::OrderedPublications.year_of`, the same year the order sorts
on, so a Forthcoming entry is dated inside the current year, where the homepage places it. The
build clock never enters: it would re-date entries on every deploy and tell feed readers they
had just been published.

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

Per publication: that file's last commit time as a full ISO 8601 timestamp
(`git log --date=iso-strict`, e.g. `2026-08-16T14:16:37+02:00`), feeding sitemap `lastmod`,
`article:modified_time` and JSON-LD `dateModified`. The fallback accepts only a four-digit
`year` (as `YYYY-01-01T00:00:00+00:00`) and otherwise falls through to now —
`Forthcoming-01-01` would be invalid in both the sitemap and the structured data.

**Why the long form and not `YYYY-MM-DD`.** Google Search Console reports a date alone on the
homepage's `ProfilePage` as *"Invalid datetime value for dateModified"* — that parser wants a
timestamp, unlike the `Article` one, which is happy with a date. A timestamp is valid in every
surface a date was valid in, so the plugin emits one format rather than two.

All per-file dates come from **one** `git log --name-only` walk keyed by path, not one
subprocess per document. Git is invoked via `Open3.capture2` with `chdir: @source`, so the
relative paths don't depend on where Jekyll was invoked from, and a missing `git` warns
rather than raising.

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

### `system_network_client.rb` → `site.data.network_client`

A `priority :high` generator projecting `_data/network.json` down to the part the browser
actually reads, for `home.html`'s `#net-data` tag.

The file feeds three surfaces with three appetites. `publication.html` walks
`nodes[].related` for its "Related publications" list and `home.html`'s Liquid builds the
cluster cards from `clusters` and quotes `params` in the legend — both at **build** time.
The network view's JavaScript needs a much smaller thing at **run** time, and inlining the
whole file served it from the union of all three: **79 KB in every homepage response**, about
half of it unread, paid for by the majority of readers who never open the view.

What survives: `nodes[]` as `slug`, `title`, `url`, `x`, `y`, `tr?` and
`related[]{slug, sim}`; `links[]` as `source`, `target`, `fb?`; plus `canvas` and `params`.
What goes: `clusters` (no JS touches it), `related[].title`/`url`/`lang` (the panel maps
`r.slug` to a node index and reads those off `nodes` — the same strings a second time, and the
bulk of the saving), `nodes[].i` (the array position), `nodes[].lang` and `links[].value`.
That is **38 KB rather than 79 KB**, and a homepage 12% smaller.

`tr` and `fb` are omitted where false rather than written as `false`, because the JS reads
both through `!!`. The set of fields was established by grepping the module for every property
read off the parsed JSON, not by inspection — if the view ever needs another one, add it to
the projection rather than reverting to inlining the file whole.

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
| `lang` is a key in `languages.yml` | error |
| `thumb` resolves to a file under `images/` | error |
| `doi` starts with `http(s)://` | warning |
| `issn` matches `\d{4}-\d{3}[\dX]`, then its mod-11 check digit | warning |
| `isbn` is 13 digits (mod-10) or 10 with an `X` allowed (mod-11), then its check digit | warning |
| `translation_of` names a slug in the collection | warning |

The `[\dX]` is not an oversight: `0024-094X` (*Leonardo*) and `2073-445X` (*Land*) both end in
X, and the mod-11 rule is what produces that X. Both identifier checks are warnings rather
than errors — a wrong identifier is bad metadata, not a broken site, so it should not block a
deploy; it does mean the log has to be read.

`translation_of` is checked against the whole collection, so it needs every slug before it can
judge any one document — that is why the generator collects them up front rather than
resolving per document.
