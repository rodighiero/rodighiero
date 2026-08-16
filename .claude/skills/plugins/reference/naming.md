# Naming a plugin

Two words, separated by an underscore. Same shape as the `<family>-<member>` rule the includes
follow, but the first word is drawn from a closed set of **two**.

## The rule

| Prefix | Count | Means |
|---|---|---|
| `publication_` | 8 | the file reads, orders, validates or decorates the `publications` collection |
| `system_` | 3 | everything else — build infrastructure whose output no reader sees as prose |

The second word is then free to say what the file does to that subject: `publication_order`,
`publication_figures`, `publication_decoder`.

**Two prefixes with no third case is the point.** A plugin either works on the collection or it
does not, so there is nothing to adjudicate at naming time. Read the prefix as a claim about
scope: a `publication_` file can be reasoned about knowing only the collection.

## The three edge cases

Worth knowing, because each looks like a violation and isn't.

**`publication_redirect.rb` is broader than its prefix claims.** It scans `site.pages +
site.documents`, so a `redirect_from` on any top-level page would be honoured too. Today every
alias happens to sit on a publication, which is why the prefix has not become a problem.

**`system_readme.rb` is the weak fit.** It exposes `README.md` as `site.data.readme_content`,
and its output *is* visible masthead prose — the one thing the `system_` gloss says it isn't.
Read the prefix here as "sourced from a repo file rather than from the collection". The other
two earn it cleanly: every one of `system_image_size.rb`'s four call sites emits a machine-read
attribute, and everything `system_commit_date.rb` feeds is machine-facing, including where it
also writes a tag on a page.

**Two `publication_` names carry a caveat the filename cannot.** `publication_date.rb` sets
`page.date`, but the value is a **feed sort key**, not a publication date. And
`publication_order.rb` is named for the *rule* rather than for any consumer, because it has
three — the gallery, the prev/next nav and the RSS feed — and naming it for one would have
lied about the other two.

## Two schemes tried and rejected

Don't re-derive these.

**Name each plugin after its consuming template.** Resolved for only 4 of 10 — several plugins
have two or four consuming templates, and three have none at all (`publication_validator`,
`publication_redirect`, and `publication_date`, whose consumer is a gem).

**A four-prefix surface rule — `home_` / `publication_` / `both_` / `system_`.** Needed a
tie-break rule for files that straddled two categories, and the `both_`/`system_` pair turned
out to be exactly the ambiguous part. Collapsing to one dominant prefix with two named
exceptions removes the adjudication without losing the grouping.

## What the filename does *not* have to match

Class names and Liquid filter names are deliberately not forced to agree with the file.
`| image_size`, `| decode_numeric_entities` and `site.data.ordered_publications` are what the
templates type and read better as they are. The filenames happen to agree with them now, which
is the point — it was never the constraint.

This is also why the header comment matters: `publication_decoder.rb` does not say
`| decode_numeric_entities`, so the first line of the file is where that coupling is written
down.

## Checklist for a new file

1. Does it work on the `publications` collection? → `publication_`, else `system_`.
2. Second word: what it does — a noun for what it produces (`figures`, `neighbors`, `order`)
   or an agent noun for what it is (`validator`, `decoder`).
3. Header comment: what it registers, publishes or attaches, and who reads it.
4. `Jekyll::`-namespaced constants, compact form.
5. Log with the filename as the prefix: `Jekyll.logger.warn 'publication_thing:', …`.
6. Add it to the index table in `../SKILL.md`. CLAUDE.md carries only the rule and a pointer,
   so it changes only if the rule does.
