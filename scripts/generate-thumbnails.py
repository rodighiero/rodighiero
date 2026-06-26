#!/usr/bin/env python3
"""Generate homepage card thumbnails.

Reads the `img:` front-matter field of every file in _publications/
(or the optional `thumb:` override, when the homepage card should use a
different image than the full-size/social `img:` — e.g. a figure from the
article body), takes that full-size WebP from images/, and writes a
thumbnail (max MAX_WIDTH px wide, never upscaled) to images/@thumbnails/,
named after the publication slug (the .md filename). Requires Pillow.
Run from the repo root:

    python3 scripts/generate-thumbnails.py
"""

import re
import sys
from pathlib import Path

from PIL import Image

MAX_WIDTH = 800
QUALITY = 70

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "images"
DEST = ROOT / "images" / "@thumbnails"

IMG_RE = re.compile(r'^img:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
THUMB_RE = re.compile(r'^thumb:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)


def front_matter_img(md_path):
    """Return the thumbnail source path: `thumb:` if set, else `img:`."""
    text = md_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    match = THUMB_RE.search(parts[1]) or IMG_RE.search(parts[1])
    return match.group(1) if match else None


def main():
    failures = 0
    total_in = total_out = 0
    for md_path in sorted((ROOT / "_publications").glob("*.md")):
        rel = front_matter_img(md_path)
        if not rel:
            print(f"warning: no img in {md_path.name}", file=sys.stderr)
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
