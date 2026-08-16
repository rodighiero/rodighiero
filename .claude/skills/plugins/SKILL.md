---
name: plugins
description: The eleven local Ruby plugins in _plugins/ — what each registers, publishes or attaches, who reads it, and the naming scheme and cross-cutting rules they all follow. Use when adding or editing a plugin, when a Liquid filter or a page-data field is missing at render time, when a build warning or fatal error names a plugin, when working out where a derived value comes from, or when deciding whether a new behaviour belongs in a plugin at all.
---

# The plugin layer

Eleven Ruby files in `_plugins/`, plus one gem (`jekyll-feed`). They exist so that templates
read values rather than derive them: a Liquid loop that scans the whole collection on each of
sixty-odd pages is the thing these replace.

They run **only because the site deploys through GitHub Actions** rather than GitHub's branch
build, which whitelists gems and ignores `_plugins/` entirely. That is not a preference; the
site would silently lose all eleven under branch deployment.

**No plugin depends on a gem.** `system_image_size.rb` is a hand-written WebP parser rather
than ImageMagick, and `publication_redirect.rb` replaced `jekyll-redirect-from` outright.

## The one idea

**A derived value is computed once, up front, and attached where the template will look for
it.** Everything here is one of three shapes:

| Shape | Registered how | Examples |
|---|---|---|
| A **Liquid filter** | `Liquid::Template.register_filter` | `image_size`, `autolink_urls`, `decode_numeric_entities` |
| A **field on a document** | a generator or `post_read` hook writing `doc.data[…]` | `commit_date`, `figures`, `prev_pub`/`next_pub`, `date` |
| A **site-wide datum** | writing `site.data[…]` | `ordered_publications`, `readme_content`, `commit_date` |

Two files fit none of them and produce no identifier a template can read:
`publication_validator.rb` (whose output is the build log, and an abort) and
`publication_redirect.rb` (whose output is extra pages).

## The naming scheme, in one line

Two words. The first is **`publication_`** (eight files) if the file works on the
`publications` collection, or **`system_`** (three) if it does not; the second says what it
does to that subject. Two prefixes with no third case means there is nothing to adjudicate.
The full rule, its three genuine edge cases, and the two schemes tried and rejected:
`reference/naming.md` — read it before naming a new file, not after.

## The index

Every plugin opens with a **header comment naming what it registers, publishes or attaches,
and who reads it** — `# | image_size — read by home.html, publication.html and both figure-*
includes`. That line is the index, and it matters more here than under a scheme where the
filename spelled out the identifier: `publication_decoder.rb` does not say
`| decode_numeric_entities`, and `publication_neighbors.rb` does not say `prev_pub`. **Keep it
accurate when the file or its consumers change** — it is the only place the coupling is
written down.

| File | Produces | Read by |
|---|---|---|
| `system_image_size.rb` | `\| image_size` | `home.html`, `publication.html`, both `figure-*` includes |
| `publication_urls.rb` | `\| autolink_urls` | `publication.html` |
| `publication_decoder.rb` | `\| decode_numeric_entities` | `publication.html` |
| `publication_order.rb` | `site.data.ordered_publications` + the `OrderedPublications` module | `home.html`; the module by `publication_neighbors.rb`, `publication_date.rb` |
| `publication_neighbors.rb` | `prev_pub` / `next_pub` | `publication-nav.html` |
| `publication_date.rb` | `page.date` | the jekyll-feed gem |
| `publication_figures.rb` | `figures` | `sitemap.xml` |
| `system_commit_date.rb` | `commit_date` (per doc **and** `site.data`) | `sitemap.xml`, `publication.html` |
| `system_readme.rb` | `site.data.readme_content` | `home.html` |
| `publication_redirect.rb` | redirect stub pages | crawlers |
| `publication_validator.rb` | build-log warnings; a fatal error | the deploy |

Per-file detail — what each actually does and the decisions inside it: `reference/catalogue.md`.

## When things run

| Stage | Who |
|---|---|
| `post_read` hook | `publication_order.rb`, `publication_neighbors.rb`, `system_readme.rb` |
| Generator, `priority :high` | `publication_validator.rb`, `publication_figures.rb`, `system_commit_date.rb`, `publication_date.rb` |
| Generator, `priority :low` | `publication_redirect.rb` (last, so every page it might alias exists) |
| `pre_render` hook | `system_image_size.rb`'s cache clear |

Two consequences worth holding on to:

- **Generators run before rendering, so `doc.content` is still the raw Markdown.**
  `publication_figures.rb` depends on this — it scans for `{% include figure-single.html … %}`
  as *source text*, which would be gone after rendering.
- **Hook order among same-stage hooks is not something to rely on.**
  `publication_neighbors.rb` needs the canonical order and could have read
  `site.data.ordered_publications`, but both are `post_read` hooks, so it calls
  `Jekyll::OrderedPublications.order(…)` directly instead. **Copy that pattern**: share a
  module, not a hook's output, whenever one same-stage plugin needs another's work.

## Three rules that hold across all of them

1. **Every constant is namespaced under `Jekyll::`**, in the compact form —
   `class Jekyll::CommitDateGenerator < Jekyll::Generator` — so a plugin adds nothing to
   top-level `Object`. The gotcha: a bare sibling constant does **not** resolve from inside
   compact-form nesting, which is why `publication_date.rb` writes the fully-qualified
   `Jekyll::OrderedPublications`. If a constant mysteriously goes missing, this is why.
2. **Each identifies itself in the build log by its filename** —
   `Jekyll.logger.warn 'publication_figures:', …` — so a warning names the file to open rather
   than a class or an abbreviation.
3. **Class and filter names are deliberately not forced to match the filenames.**
   `| image_size`, `| decode_numeric_entities` and `site.data.ordered_publications` are what
   the templates type, and they read better as they are. The filename agrees with them anyway;
   the point is that it was never a constraint.

## Operations

### Add a plugin
Name it first (`reference/naming.md`). Then: header comment naming what it produces and who
reads it, `Jekyll::`-namespaced constants, filename-prefixed log messages. Pick the stage from
the table above — a `post_read` hook if templates and other plugins need the value, a
generator if it only decorates documents. Add it to the index table above — CLAUDE.md keeps
only the naming rule and a pointer here, so it needs no edit unless the *rule* changes.

### Add a field templates can read
Attach it to `doc.data[…]` in a generator or `post_read` hook. Do not compute it in Liquid —
the whole layer exists to keep sixty-odd pages from each scanning the collection. If two
plugins need the same derivation, put it in a module both call.

### Change the publication sort order
`Jekyll::OrderedPublications.sort_key` in `publication_order.rb`, and only there. It reaches
the gallery, the prev/next nav and the RSS feed; changing it in one consumer would make the
three disagree.

### Debug a missing value
Check the plugin's header comment for the identifier, then confirm the stage: a value written
by a generator is not available to another generator that ran at the same priority. Errors
from `publication_validator.rb` abort the build with the count; everything else warns and
ships.

## Invariants — don't break these

- **`publication_validator.rb` must keep aborting on error.** It runs on every deploy and is
  the only thing standing between bad front matter and a shipped page.
- **`system_commit_date.rb`'s site-wide date must not become `HEAD`.** It is the homepage's
  sitemap `lastmod`, and this repo commits prose about the code beside the code.
- **It needs full git history** — `deploy.yml` checks out with `fetch-depth: 0`. A shallow
  checkout degrades every date to a fallback, silently.
- **One `git log` walk, not one per document.** The per-file dates come from a single
  `--name-only` walk; a subprocess per publication would be 61+ forks per build.
- **`publication_date.rb`'s value is a sort key, not a publication date.** January 1st at
  noon plus a few seconds of offset, arranged so jekyll-feed's newest-first ordering reproduces
  the homepage's alphabetical order within each year. Nothing may read it as a real date.
- **A `Forthcoming` entry is dated `site.time - i`, never in the future** — a future date trips
  Jekyll's future-date filter and drops the page from the build entirely.
- **`prev_pub`/`next_pub` store a plain hash (url + title), not the neighbouring Document.**
  Storing the document would make each page reference the other through page data.
- **`publication_figures.rb` excludes `images/@cards/`** — generated gallery crops, not article
  imagery — and drops a path missing from disk, because a 404 in an image sitemap is a crawl
  error rather than a discovery.
- **`system_image_size.rb` clears its cache on `pre_render`.** Without it a long-running
  `jekyll serve` leaks and serves stale dimensions for a replaced image.
- **`autolink_urls`' regexp must keep swallowing whole tags in group 1.** That is what stops it
  wrapping URLs already inside `href`/`src` attributes. The explicit ` ` exclusion is also
  load-bearing: kramdown inserts a non-breaking space before the footnote return arrow and
  Ruby's `\s` does not match it.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Build aborts, "Front matter validation failed with N error(s)" | `publication_validator.rb`; the errors are logged just above |
| A Liquid filter is "unknown" | the file isn't in `_plugins/`, or the site is being built by GitHub's branch deployment, where no local plugin runs |
| Every `lastmod` is `<year>-01-01` or today | git history unavailable — shallow checkout, or `git` not on `PATH` (logged by `system_commit_date:`) |
| An image is missing from the sitemap | `publication_figures:` warned it isn't on disk, or it lives under `images/@cards/` |
| `width`/`height` empty on a figure | not a WebP, or a WebP variant the parser doesn't cover (it reads VP8, VP8L, VP8X) |
| A constant is `uninitialized` inside a plugin | compact-form nesting — qualify it as `Jekyll::Thing` |
| The feed's order disagrees with the gallery | something re-derived the sort instead of calling `Jekyll::OrderedPublications` |
| An alias 404s | skipped as a duplicate, or for not starting with `/` — `publication_redirect:` names the file |
| The bio is empty | `system_readme:` couldn't find `README.md` |
