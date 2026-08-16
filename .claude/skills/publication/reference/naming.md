# Naming an include

`_includes/` files are named **`<family>-<member>`**: a family noun that groups siblings,
then which one of them this is. The rule is deliberately the same shape as the one for
`_plugins/`, which the **`plugins`** skill documents in its own `reference/naming.md`.

| Family | Members |
|---|---|
| `credit-` | block, full, join, names, short |
| `card-` | action, meta |
| `figure-` | group, single |
| `jsonld-` | people, person |
| `publication-` | cite, nav |
| `site-` | analytics, head, scripts, toggle |
| `styles-` | base, font |
| `network-` | the generated `*.svg` miniatures |

## The three rules

1. **The family word classifies, so it comes first and is always a noun** — never a verb
   phrase. `join-and.html` was the shape this replaced.
2. **A helper that would found a family of one folds into the family it serves.**
   `credit-join.html` joins name lists for both the homepage byline and the Chicago
   reference, so it is a `credit-`, not a `list-`.
3. **Members are named for the voice or role, not the surface or the place.** `credit-full`
   names every contributor in citation order (publication page and `<title>`);
   `credit-short` writes from Dario's point of view with his own name stripped ("with X and
   Y", homepage cards). They were `-text` / `-home`, which named a format and a place while
   the real distinction between them is neither.

The same two-word shape carries into the **behavioural class hooks** the JS selects on,
which stay separate from the classes that style them: `.cite-btn` (the trigger) and
`.cite-data` (the hidden `<pre>` it copies) are one `cite-` family, wearing `.pill-btn` for
their looks. Restyling never breaks a selector, and vice versa.

## Settled — don't re-derive

- **`byline-` → `credit-`.** A byline is strictly the *author* line, and these files also
  render "Ed.", "Translated by", "Preface by" and "Interview by". The word "byline" survives
  in prose and in `publication_validator.rb`'s error message, where it means the author line
  and is exactly right.
- **`credit-text` / `credit-home` → `credit-full` / `credit-short`.** See rule 3.
- **`join-and.html` → `credit-join.html`.** See rules 1 and 2.

## Think twice about `figure-single` / `figure-group`

They are called from nearly every publication. Renaming them rewrites the corpus, and every
rewritten file gets a new `commit_date` — which is what feeds sitemap `lastmod` and JSON-LD
`dateModified`, so the whole collection reports as freshly modified. Count first:

```bash
/usr/bin/grep -ro "include figure-" _publications | /usr/bin/wc -l   # call sites
/usr/bin/grep -rlo "include figure-" _publications | /usr/bin/wc -l  # files affected
```
