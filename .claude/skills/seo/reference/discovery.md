# Discovery — sitemap, robots, aliases, feed, 404

How URLs are found, consolidated, and retired. Everything here is about *which* URLs exist and
which one is canonical; what each page then says about itself is `head.md`.

## `sitemap.xml`

Hand-written Liquid, not a gem. One `<url>` for the homepage, then one per
`site.publications`. Each carries exactly three things: `loc`, `lastmod`, and its images.

**Dropped on purpose:** `changefreq` and `priority` — Google stopped reading them in 2023.
Don't add them back.

**The image extension** (`sitemap-image/1.1`) declares only `image:loc`. `image:title`,
`caption`, `license` and `geo_location` were discontinued in August 2022 and are ignored.

The homepage declares the portrait. Each publication declares its **`figures`** — the images
that actually appear inside the body, collected by `publication_figures.rb` off the raw
content by scanning the `figure-single` / `figure-group` includes. Not the `thumb`.

`images/@cards/` copies are excluded — gallery and social crops, not article content — and so
is any path missing from disk. Excluding a card image does **not** deindex it: it stays on the
page as a lead figure and as `og:image`. How the two call conventions are normalised and why
each filter exists: the **`plugins`** skill (`reference/catalogue.md`, `publication_figures.rb`).

## `lastmod`

| URL | Source |
|---|---|
| a publication | `page.commit_date` — that file's last commit |
| the homepage | `site.data.commit_date` — **not `HEAD`** |

The homepage is the one URL with no file of its own. Its date is the last commit touching a
path that *reaches `_site`*, so a commit to `CLAUDE.md`, a skill or a build script does not
tell crawlers the homepage changed. `system_commit_date.rb` derives the exclusion list from
Jekyll's own `exclude:` rather than keeping a parallel copy, with two adjustments Jekyll
cannot supply:

- `UNPUBLISHED` — tracked dot-paths Jekyll drops implicitly (`.claude`, `.github`,
  `.gitignore`), which are not in `exclude:` but never reach the build.
- `PUBLISHED_ANYWAY` — `README.md`, excluded from the build but *is* the homepage bio, so a
  change to it really is a change to the page.

Both lists are small and exist because the two sets genuinely differ. Adding a new top-level
directory of tooling means adding it to `exclude:` (which handles both concerns at once).

The whole thing needs full git history — `deploy.yml` checks out with `fetch-depth: 0`. A
shallow checkout silently degrades every date to the fallback.

## `robots.txt`

Four lines: `Allow: /` for everyone, plus the sitemap URL. Nothing is disallowed, and the
`@cards/` note above is the reason to keep it that way.

## URL aliases

`redirect_from` on any page or document (`publication_redirect.rb` scans
`site.pages + site.documents`, so a top-level page would work too — today every alias happens
to sit on a publication). The stub is:

```html
<link rel="canonical" href="<absolute URL of the real page>">
<meta http-equiv="refresh" content="0; url=<target>">
<script>location.replace("<target>");</script>
```

**It deliberately carries no `noindex`** — the refresh is what keeps an alias out of the
index, and the canonical is what hands the real page the alias's link credit. The full
argument: the **`plugins`** skill (`reference/catalogue.md`, `publication_redirect.rb`).

Path rules: an alias with no extension is written `<alias>.html` (served extensionless by both
GitHub Pages and `jekyll serve`); one ending in `/` becomes `<alias>/index.html`. A duplicate
alias, or one not starting with `/`, is skipped with a build warning naming the file. Stubs
set `sitemap: false`, and `sitemap.xml` loops `site.publications` only, so they never appear.

## The feed

`jekyll-feed` on the `publications` collection, at `/feed.xml`, `excerpt_only` so each entry
carries its abstract rather than the full body. The gem *always* emits a posts feed too, so it
is parked at `/feed/posts.xml` (empty) and deleted by `deploy.yml`.

Ordering is the reason `publication_date.rb` exists: most entries declare only a `year`, so it
synthesises `page.date` as January 1st at noon plus a few seconds of offset, arranged so the
feed's newest-first ordering reproduces the homepage's alphabetical order within each year.
The value is a **sort key**, not a publication date, and nothing else should read it as one.

## `404.html`

Standalone — its own inline CSS and the only page still loading `fonts/nunito.css`. It is
`noindex` and carries **no `rel=canonical`**, for two independent reasons:

1. Pointing one at the homepage would ask crawlers to consolidate every missing URL into it.
2. `count.js` derives its analytics path from `link[rel=canonical]` when that points at this
   host, so every 404 would be logged as `/` — inflating the homepage and hiding which dead
   links people actually follow. Instead the page sets
   `window.goatcounter = {path: … '404: ' + location.pathname}` **before** the async
   `count.js` runs (which keeps an existing `window.goatcounter` object).
