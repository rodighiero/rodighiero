---
name: links
description: Link rot — the weekly lychee crawl, reading its report, and repairing a dead reference with a Wayback fallback. Use when the links.yml workflow goes red, when asked to check the site's external links, when a cited URL no longer resolves, or when deciding whether a 403/429 is real rot or a bot wall.
---

# Link rot

A link can rot without anything in the repo changing, so this is **scheduled maintenance, not
a broken build**. A red `links.yml` run is normal and expected; it is not a deploy blocker
(`deploy.yml` is a separate workflow and does not depend on it).

## The crawl — `.github/workflows/links.yml`

A weekly **lychee** crawl of the built `_site/` (Monday 09:00 UTC), plus `workflow_dispatch`
for a run on demand.

It accepts `200,202,206,302,403,429,999` — **a bare 403 or 429 is a bot wall, not rot** — and
carries a hand-maintained `--exclude` list of hosts that block crawlers outright. `doi.org` is
excluded because publisher landing pages behind a DOI answer inconsistently, so a resolving
DOI still reports as broken.

Adding a host to `--exclude` is the right move when it blocks crawlers *categorically*. It is
the wrong move for a single URL that has genuinely died — that one gets an archive fallback.

## Reading the report

On failure, run **`scripts/link-context.py`** over lychee's flat `lychee/out.md`. It turns the
bare list into a report that says *where* each dead URL lives:

| Where the URL sits | What the report shows |
|---|---|
| a Markdown bullet | the full citation |
| inline prose | the surrounding paragraph |
| front matter | the publication title |

That context is what makes the report actionable — a bare list of URLs does not say which
reference to go fix.

## Triage

1. **403 / 429 / 999 that lychee already accepts** — nothing to do.
2. **A host that blocks crawlers as a policy** — add it to `--exclude` in `links.yml`.
3. **A transient 5xx or timeout** — re-check by hand before touching a file; a publisher
   being down for an afternoon is not rot.
4. **A genuinely dead URL** — archive fallback, below.
5. **A typo in the repo's own URL** — just fix it; there is nothing to preserve.

## The archive fallback

**Dead references get an archive fallback rather than a deletion.** The original URL stays
exactly where it is — it is what the publication cited, and rewriting it would falsify the
citation — and a Wayback link is appended in parentheses:

```
<original URL> ([archived](https://web.archive.org/web/<timestamp>/<original URL>))
```

Rules:

- **Pick a capture contemporaneous with the reference's own access date**, not merely the most
  recent one. A late snapshot of an expired domain can be a parking page, and archive.org will
  happily serve it.
- **Verify the candidate** through `https://archive.org/wayback/available?url=…&timestamp=…`,
  whose `closest` object reports the `status` the crawler actually recorded. Only a **`200`**
  capture is worth linking.
- **The label follows the language of the piece** (`archiviato` in the Italian entries) — it is
  prose inside a bibliography, not UI.
- **A URL with no usable capture is left alone.** A fabricated or wrong-content archive link is
  worse than an honest dead one.

Editing a publication file this way bumps its `commit_date` — expected for a real repair, but
a reason not to sweep every file at once (what the value feeds: the **`plugins`** skill). Body
text changes also shift the embedding: the **`publication`** and **`network`** skills.
