# Images

## The rule

**Every source image belongs to its publication**, in `images/<publication-slug>/`: the
numbered `fig_00N.webp` figures, plus an optional `cover.webp` for the card/social image when
it is not one of those figures — either because a purpose-made image is wanted, or because the
entry has no article figures at all (a book cover, a map, a magazine spread).

## `images/@cards/` — wholly generated

One flat max-800px copy per publication, named `<slug>.webp` after the .md filename, written
by `scripts/generate-thumbnails.py` from whatever that publication's `thumb` points at (always
re-encoded at card quality, committed to the repo — rerun it after adding or changing a card
image).

`@cards/` is safe to delete and rebuild, is the **only** image set the homepage loads, and is
**never a source**: `og:image` keeps pointing at the full-size original in the publication's
own folder, so a social preview never inherits the gallery downsize. It is also excluded from
the image sitemap — crops, not article content, and excluding one does not deindex it. Why:
the **`seo`** skill (`reference/discovery.md`).

## Compression — method 6

All source WebPs are stored at libwebp's **method 6** (max compression effort). Run
`python3 scripts/optimize-images.py` after adding new images: it re-encodes every WebP under
`images/` — except `@cards/`, which its own generator already writes at method 6, and
`@icons/` — at method 6 to a strict visually-lossless PSNR target, keeping the result only
when it is meaningfully smaller. So no image is ever degraded or enlarged, and the pass is
idempotent. `--dry-run` previews the savings.

`method` is cwebp's effort dial `-m` (0–6) and does **not** change quality — a higher method
means a smaller file at the same fidelity. Most gains come from figures originally saved with
the fast default.

## `thumb` — the one image field

A path under `images/`, always inside the publication's own folder: a body figure like
`<slug>/fig_002.webp` when the card should show a figure from the article, or
`<slug>/cover.webp` when it should not.

It is the source for the generated homepage card **and** the OG/Twitter/JSON-LD social image
(`_social_img = thumb`), so the shared preview always matches the card.

There is **no on-page hero**: every publication's on-page imagery comes from body figures
(`{% include figure-single.html %}`). Entries whose "content" is really a single image — a
book cover, a map, a magazine spread — open the body with a **caption-less lead figure**
pointing at that image (the same `<slug>/cover.webp` the `thumb` uses). A `cover.webp` is
*not* automatically displayed, though: three entries carry one purely as a social preview and
show nothing on the page, which is why they declare no images in the sitemap.

Because a `thumb` can have any aspect ratio, the homepage card reserves space from the
**thumbnail's own** intrinsic size, read at build time via the `image_size` filter.

## The author portrait

It sits directly in `images/`, not in a publication folder. The homepage header wears it as a
`.card-media` — the same slot a publication's thumbnail sits in — so it is as wide as its
column, and it carries **four widths in one `srcset`**:

- `Dario-Rodighiero-640.webp` serves every count from two columns up (a fixed 251px slot);
- the `-768` / `-1024` copies plus the full-size `Dario-Rodighiero.webp` cover the one-column
  case, where the column is the page's whole width.

The rungs in the middle exist because that case is a phone: at ~347 CSS px (a 430px viewport)
the image is asked for at 694 device pixels on a 2× screen, and a 390px one asks 920 on a 3×,
both past the 640 copy — so with only 640 and 1200 to choose from, the larger phones fetched
the 1200 (50KB) for the one image carrying `fetchpriority="high"`.

All four are one family (`cwebp -m 6 -sharp_yuv -q 81`, the quality the 640 copy was already
at). The ladder only pays if `sizes` states the real column rather than `100vw`: an
overstatement is safe with two candidates (it can only bias the choice upward) but with four
it costs a rung.

**The full size alone** is what OG cards, JSON-LD and the sitemap point at — the downsized
copies are display derivatives, never declared, on the same principle that keeps `@cards/` out
of the sitemap.

## `images/@icons/`

The site icon set: `favicon.ico` (legacy tab icon, ~5 KB), the vector `icon.svg` (modern
browsers), `apple-touch-icon.png` (180px, iOS/Android home screen), and `icon-192.png` /
`icon-512.png` referenced by the root `site.webmanifest`. All are derived from one orthographic
graticule-sphere source on a white background. Both layouts declare them in `<head>` (SVG
preferred, `.ico` as fallback) plus `<link rel="manifest">`.

## The `@` prefix

It sorts those folders first in listings. An underscore would not work — Jekyll excludes
underscore-prefixed paths from the build.

## Which path each surface uses

| Surface | Path |
|---|---|
| Homepage cards | `/images/@cards/{{ slug }}.webp` |
| OG/Twitter + JSON-LD | `/images/{{ thumb }}` (with `og:image:width`/`height` via `image_size`) |
| Sitemap, per publication | the body `figures` from `publication_figures.rb` |
| Sitemap, homepage | the full-size portrait |
