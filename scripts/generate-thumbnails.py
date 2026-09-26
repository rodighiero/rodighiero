#!/usr/bin/env python3
"""Generate the homepage card images.

Reads the `thumb:` front-matter field of every file in _publications/ (the
full-size card + social image, living in the publication's own images/<slug>/
folder — either one of its figures or a purpose-made cover.webp), and writes
downsized copies to images/@cards/, named after the publication slug (the .md
filename), never upscaled:

    <slug>.webp        MAX_WIDTH (800) — the src, the phone copy, what image_size reads
    <slug>-520.webp    a retina desktop or tablet (a card is drawn 251 CSS px wide)
    <slug>-400.webp    a 1x desktop

home.html offers them as one srcset, so the browser takes the smallest that is sharp
on the reader's screen. A rung is written only when the source is wider than it.

images/@cards/ is therefore wholly generated — safe to delete and rebuild — and is
the only image set the homepage loads. The full-size original stays with its
publication and is what og:image points at.

Requires Pillow (in pyproject.toml). Run from the repo root:

    uv run scripts/generate-thumbnails.py
"""

import sys
from pathlib import Path

import yaml
from PIL import Image

MAX_WIDTH = 800
RUNGS = (400, 520)  # the smaller copies; keep in step with _card_rungs in home.html
QUALITY = 70

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "images"
DEST = ROOT / "images" / "@cards"


def front_matter_img(md_path):
    """Return the thumbnail source path from the `thumb:` front-matter field."""
    text = md_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    return fm.get("thumb")


def main():
    failures = 0
    total_in = 0
    total_out = {w: 0 for w in (MAX_WIDTH, *RUNGS)}
    for md_path in sorted((ROOT / "_publications").glob("*.md")):
        rel = front_matter_img(md_path)
        if not rel:
            print(f"warning: no thumb in {md_path.name}", file=sys.stderr)
            continue
        src = SOURCE / rel
        if not src.is_file():
            print(f"error: missing {src}", file=sys.stderr)
            failures += 1
            continue
        DEST.mkdir(parents=True, exist_ok=True)
        # A thumb that got smaller must not leave a stale rung behind.
        for w in RUNGS:
            (DEST / f"{md_path.stem}-{w}.webp").unlink(missing_ok=True)
        in_kb = src.stat().st_size / 1024
        out_kb = []
        # Always re-encode: sources are saved at high quality, so even
        # already-small images shrink a lot at thumbnail quality.
        with Image.open(src) as im:
            for w, suffix in [(MAX_WIDTH, "")] + [(w, f"-{w}") for w in RUNGS]:
                if suffix and im.width <= w:
                    continue
                dst = DEST / f"{md_path.stem}{suffix}.webp"
                out = im
                if im.width > w:
                    out = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                out.save(dst, "WEBP", quality=QUALITY, method=6)
                out_kb.append(f"{dst.stat().st_size / 1024:.0f}")
                total_out[w] += dst.stat().st_size / 1024
        total_in += in_kb
        print(f"{rel}: {in_kb:.0f} KB -> {' / '.join(out_kb)} KB")
    widths = ", ".join(f"{w}px {kb:.0f} KB" for w, kb in total_out.items())
    print(f"\ntotal: {total_in:.0f} KB -> {widths}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
