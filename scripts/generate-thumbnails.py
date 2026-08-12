#!/usr/bin/env python3
"""Generate the homepage card images.

Reads the `thumb:` front-matter field of every file in _publications/ (the
full-size card + social image, living in the publication's own images/<slug>/
folder — either one of its figures or a purpose-made cover.webp), and writes a
downsized copy (max MAX_WIDTH px wide, never upscaled) to images/@cards/, named
after the publication slug (the .md filename).

images/@cards/ is therefore wholly generated — one file per publication, safe to
delete and rebuild — and is the only image set the homepage loads. The full-size
original stays with its publication and is what og:image points at.

Requires Pillow. Run from the repo root:

    python3 scripts/generate-thumbnails.py
"""

import sys
from pathlib import Path

import yaml
from PIL import Image

MAX_WIDTH = 800
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
    total_in = total_out = 0
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
        dst = DEST / f"{md_path.stem}.webp"
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Always re-encode: sources are saved at high quality, so even
        # already-small images shrink a lot at thumbnail quality.
        with Image.open(src) as im:
            if im.width > MAX_WIDTH:
                im = im.resize(
                    (MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)),
                    Image.LANCZOS,
                )
            im.save(dst, "WEBP", quality=QUALITY, method=6)
        in_kb = src.stat().st_size / 1024
        out_kb = dst.stat().st_size / 1024
        total_in += in_kb
        total_out += out_kb
        print(f"{rel}: {in_kb:.0f} KB -> {out_kb:.0f} KB")
    print(f"\ntotal: {total_in:.0f} KB -> {total_out:.0f} KB")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
