# The grid

The card width is the constant and the column count follows from it, rather than a set of
hand-picked breakpoints. `--card-w` (270px), `--card-gap` (24px) and `--page-gutter` (32px)
are declared once in `styles-base.css` and read at runtime by the masonry
(`CARD_W`/`GAP_X`/`PAGE_PAD`, via `getComputedStyle`) instead of being copied into it, so
retuning a card is a one-place edit that the header's alignment picks up on its own.

The gallery fits as many `--card-w` columns as the page can hold, **capped at 4**, so a card
is the same size at every width above mobile and the leftover goes to the margins.
`syncPageWidth()` then sizes `document.body` to exactly what the current count spans — at
today's tokens the counts change at **628 / 922 / 1216 px**, each of them `gridWidth(n) + PAGE_PAD`
and so derived, not chosen — so the header, bio, search bar and footer all end
where the last card ends, rather than a 2- or 3-column grid sitting centred in a wider page.

## `--page-gutter` is not decoration

It is the column the fixed `.mode-toggle` lives in, which is why the page's inset is a token
at all. The toggle is fixed to the viewport while the body is centred inside it, so the two
are measured from different origins and collide wherever the centring margin runs out —
under every card below one column, in a band above each of the three thresholds, and down
the whole right edge of a 660px article on a phone, with the content scrolling *beneath* the
icon. Sizing the inset to hold the toggle removes the collision by construction rather than
at the widths that happen to leave a margin.

It settles a second defect for free: `.mode-toggle` and the sticky `.filters` bar both carry
`z-index: 10`, and the bar is later in the DOM, so in those same bands the opaque bar used to
paint the toggle out of existence. A gutter puts the toggle outside the bar's box entirely.

**The 32px is a sum, not a taste.** Per side it must hold:

- the 20px button (16px icon + 2 × 2px padding),
- the 4px its focus ring reaches past that (`outline: 2px` at `outline-offset: 2px`),
- the toggle's own 8px inset from the window, which must itself clear 4px or the ring is cut
  off by the window edge.

28px is the floor, where the ring touches both edges; 32px is the first pair with air on
both. **Retuning the gutter, the inset, the icon or the focus ring means redoing that sum.**

## `clientWidth`, not `innerWidth`

The measurement is `document.documentElement.clientWidth`. `window.innerWidth` counts a
classic scrollbar (Windows, Linux, macOS set to always show them) as page width, and the
grid would then overhang the body by exactly the scrollbar's width — a horizontal scrollbar
on the whole page.

## One column

Below two columns there is no grid left to speak of: one full-width column, which is the
mobile layout. But the vertical gap between stacked tiles stays `CARD_W / 4` — a quarter of
a *card*, not of that full-width column, which would make the gap itself the size of a card.

## Everything else sits on those same columns

The page is one grid, not a grid with a header and a footer beside it.

**Header.** `repeat(auto-fill, minmax(min(var(--card-w), 100%), 1fr))` with `var(--card-gap)`,
each column padded by the `--card-pad` a card pads its own content with. Because the body is
sized to the grid, the header takes exactly as many columns as the gallery below it, so
column 2's left edge lands on card 2's left edge and not merely on the row's outer end, and
the bio paragraphs wrap onto a second row as the count drops instead of the header
collapsing to one full-width column (which used to set 12px text on an 858px measure the
moment the 4th column stopped fitting). The `minmax(min(…), 1fr)` form is what keeps a
viewport narrower than a single card from overflowing; where the body *is* grid-sized, `1fr`
resolves to `--card-w` exactly.

Three columns is the one count where the four blocks don't divide evenly, so
`body[data-cols="3"] .header .bio-col { grid-row: 2 }` sends all three paragraphs to the
second row — side by side across the full measure, with the identity block alone in the first
column above them — rather than leaving two beside the portrait and the third under it.

**Footer and network view** follow the count instead of hardcoding four. `syncPageWidth`
publishes it as `--cols` (the number to compute with) and `data-cols` (the hook for rules
that can't, since a grid line counted from the end needs a line to exist), and both use
`repeat(var(--cols), 1fr)` with `var(--card-gap)` — which reproduces a card's width exactly.

The footer's quote takes the **last two columns** at four, three and two, in one declaration:
`grid-column: -3 / -1`. Counting both endpoints from the end makes `-3` resolve to `cols - 1`
and the span follow the count by itself. At two columns that is the whole row, which is the
intent — half a two-column page is too narrow a measure for a quotation that long.

One column is the exception, and the only case needing `data-cols`: there is no
second-to-last line to reach back to, so `-3` would land before the grid's first line and the
browser would manufacture an implicit column to hold the item, widening the footer past the
page.

**Network stage.** The sidebar is one column and the stage the rest, so the panel is exactly
a card wide and the stage starts on a card edge. Within that span the stage is a **square two
columns wide** (`2 × --card-w + --card-gap`, the same at every count, since the card width is
the constant — and the square `scripts/layout-network.js` bakes its coordinates into, as
`CANVAS_W`/`CANVAS_H`), `justify-self: center` — it fills the two remaining columns exactly at
three and sits centred inside three at four. Its height comes from `aspect-ratio: 1` rather
than a slice of the viewport: the view is as tall as the graph, instead of a `80vh − 9rem` box
a wide canvas could only fill in the middle, leaving ~165px of dead space above and below.

The CSS carries `body { --cols: 4 }` for the moment before the masonry first runs (which is
before the first paint) and for a reader with no JS.

## The 921px boundary

Where the grid drops from 3 columns to 2, and where the view toggle, the filter count and the
action/cluster tiles are hidden (event cards stay) and the network view is forced back to
gallery.

The JS asks for it as a **`matchMedia` query** rather than measuring `innerWidth`, so it runs
the identical test the CSS does: a media query is matched against the viewport *without* its
scrollbar while `innerWidth` includes one, and in the band between those two answers the
toggle would be hidden with the network view still live — a reader with it persisted, in a
view with no visible way out.

The number is written **once**, as the Liquid `{% assign _mobile_max = 921 %}` at the top of
`home.html` (it is `gridWidth(3) + PAGE_PAD - 1`, so it moves whenever `--page-gutter` does),
and interpolated into all three places that ask for it — the pre-paint script in `<head>`,
the `@media` rule, the `matchMedia` call. Three literals that must agree, from one source.

## Two things to keep in mind when touching `setView`

`syncPageWidth()` is called from `layoutMasonry()`, which the network branch must **not** run
— so that branch syncs the width itself before the graph is fitted into the stage. A page
opening straight into `?view=network` would otherwise keep the stylesheet's 4-column cap.

It does **not** have to tell the graph about it. The network watches its stage with a
**`ResizeObserver`** rather than listening for window resizes, and the stage is as wide as the
page, so every way its box can change reaches it on one path: the page being resized to a new
column count, the view switch that takes the stage from `display: none` to its real size, a
window resize that happened while the gallery was on screen — with no call site having to
remember to ask. The callback ignores a 0×0 delivery (what a hidden stage measures) and
re-fits — a scale and a translate, no simulation — on any other. Observer callbacks run after
layout and before paint, so the read costs no forced reflow.

## The bio collapse and the grid

The whole masthead — portrait, name, links and bio — collapses behind the `.bio-toggle`
button above it, persisted in `localStorage` under `bioVisible` and restored before the first
paint by the `<head>` script, as one attribute (`data-bio-visible`) on `<html>` that every
rule reads. `.bio-shell` is the collapsing wrapper, which is why `.header` carries no bottom
padding: the spacing is the shell's margin, so it can go to zero with the height.

**At rest the collapse holds no measurement**: open, the shell's height is `auto`; closed, it
is 0. That is the whole point, and it is what the first attempt got wrong — it kept the open
height pinned to a pixel number maintained by a `ResizeObserver`, which could not survive this
page, because the header's height *is* a function of the column count (four blocks in one row
at four columns, two rows at three, stacked at one), so every remeasure raced a layout that
had already changed shape and a stale number clipped the bio under its own `overflow`. `auto`
cannot go stale, so a resize at any time in either state needs no handling at all.

A pixel number does appear, but only **during** the travel: `height: auto` is not an
interpolable value in most engines, so `setBioVisible` pins the height the panel currently
occupies, flips the state, and hands the height back to the stylesheet on `transitionend` —
and on `transitioncancel` too, or an interrupted double-click would leave a pin behind, which
is the stale number all over again. (`interpolate-size: allow-keywords` would remove even
that and was tried first, but it is too new to rely on: where it is missing the height simply
jumps, which is the one thing the rule exists to prevent.) `prefers-reduced-motion` skips the
pin entirely and lets the state flip instantly.

The JS owns only the state: it flips the attribute, updates `aria-expanded`/label/title,
persists, and sets `.inert` on the shell — a panel clipped to zero height still holds real
links, which would otherwise stay in the tab order. It also calls `scheduleLayout()` on toggle
and on the height's `transitionend`, not because the masonry depends on the header (tiles sit
inside `#publications`, which merely moves) but because losing ~400px of page can take a
scrollbar with it, and a scrollbar is width, which is the column count.

Bio prose itself lives in `README.md`, split into three paragraphs with `<!-- split -->`
comments; `_plugins/system_readme.rb` exposes it as `site.data.readme_content`, so `README.md`
doubles as the GitHub repo readme.
