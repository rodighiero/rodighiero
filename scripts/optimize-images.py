#!/usr/bin/env python3
"""Re-encode source WebP images at the maximum compression effort (method 6).

WebP's `-m` flag (0-6) is the encoder's *effort* level, not its quality: at a
fixed fidelity, a higher method searches harder for a more compact packing of
the *same* pixels. Many of the site's images were originally saved with the
fast default (method 4) or with a less efficient encoder, leaving free bytes on
the table.

For every WebP under images/ (excluding @thumbnails/, which has its own
generator, and @icons/), this re-encodes at:

    method 6  (max effort)  +  -sharp_yuv  +  a strict visually-lossless target

Fidelity is pinned with cwebp's `-psnr` target (PSNR_TARGET dB against the
current pixels), so quality is preserved regardless of the original's quality
setting — the method, not the quality, does the shrinking. The result replaces
the original ONLY when it is smaller by a meaningful margin (MIN_SAVING_PCT /
MIN_SAVING_BYTES); a re-encode that would grow the file, or barely change it,
leaves the original untouched. So no image is ever made worse or bigger, and the
pass is idempotent (a second run finds nothing left to gain).

Requires libwebp's `cwebp` on PATH (brew install webp). Run from the repo root:

    python3 scripts/optimize-images.py            # apply in place
    python3 scripts/optimize-images.py --dry-run  # report only, change nothing

Note: a handful of @cards images also seed homepage thumbnails; if any card is
re-encoded, rerun scripts/generate-thumbnails.py afterwards (the visual delta is
nil at this fidelity, but it keeps provenance clean).
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

METHOD = 6            # max compression effort (0=fast … 6=slowest); quality-neutral
PSNR_TARGET = 50      # dB vs current pixels — strict visually-lossless (>~45 is imperceptible)
MIN_SAVING_PCT = 5.0  # only replace when at least this much smaller …
MIN_SAVING_BYTES = 2048  # … and at least this many bytes, to skip trivial churn

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
EXCLUDE_DIRS = {"@thumbnails", "@icons"}


def sources():
    """All optimizable WebPs under images/, excluding the generated/derived dirs."""
    for path in sorted(IMAGES.rglob("*.webp")):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(IMAGES).parts):
            continue
        yield path


def reencode(src, dst):
    """Re-encode src to dst at method 6 / visually-lossless. Returns True on success."""
    result = subprocess.run(
        ["cwebp", "-quiet", "-m", str(METHOD), "-psnr", str(PSNR_TARGET),
         "-sharp_yuv", "-metadata", "none", str(src), "-o", str(dst)],
        capture_output=True,
    )
    return result.returncode == 0 and dst.is_file() and dst.stat().st_size > 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report savings without modifying any file")
    args = parser.parse_args()

    total_before = total_after = 0
    changed = failures = 0
    print(f"{'file':52} {'orig':>8} {'new':>8} {'result':>12}")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.webp"
        for src in sources():
            orig = src.stat().st_size
            if not reencode(src, out):
                print(f"{str(src.relative_to(IMAGES)):52} {'':>8} {'':>8} {'ENCODE-FAIL':>12}")
                failures += 1
                continue
            new = out.stat().st_size
            saving = orig - new
            worth = saving >= MIN_SAVING_BYTES and saving >= orig * MIN_SAVING_PCT / 100
            total_before += orig
            total_after += orig - saving if worth else orig
            if worth:
                if not args.dry_run:
                    out.replace(src)
                    out = Path(tmp) / "out.webp"  # replace() moved the temp file
                changed += 1
                label = f"-{saving * 100 // orig}%"
            else:
                label = "keep"
            print(f"{str(src.relative_to(IMAGES)):52} {orig/1024:7.0f}K {new/1024:7.0f}K {label:>12}")

    saved = total_before - total_after
    print(f"\n{'DRY RUN — ' if args.dry_run else ''}"
          f"{changed} file(s) {'would be' if args.dry_run else ''} re-encoded, "
          f"{failures} failure(s)")
    print(f"total: {total_before/1024/1024:.1f} MB -> {total_after/1024/1024:.1f} MB "
          f"(saved {saved/1024/1024:.1f} MB, {saved*100//total_before if total_before else 0}%)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
