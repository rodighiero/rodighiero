#!/usr/bin/env python3
"""Compare the built site before and after a change — the check a refactor passes.

The site has no test suite, so a change that should not alter what readers get is
verified by building twice and diffing _site: once from a git ref (a temporary
worktree), once from the working tree. Comments and whitespace are stripped before
comparing, so condensing a comment or re-indenting a block reads as no change; what
remains is every real difference in markup, CSS, JS, JSON-LD, the feed and the sitemap.

  uv run scripts/diff-build.py                 # HEAD vs the working tree
  uv run scripts/diff-build.py HEAD~3          # an older ref vs the working tree
  uv run scripts/diff-build.py --ignore-dates  # mask commit dates too (base ref is older)
  uv run scripts/diff-build.py --keep          # leave both builds in place to inspect

Each build's own clock (`site.time`, read from its feed's first <updated>) is always
masked. Commit dates are not unless asked: against HEAD they cannot differ, and
against an older ref they are real output — the sitemap and dateModified do change.

Stripping is a heuristic tuned to this site, not a parser: `/* */` and `<!-- -->`
comments go, and a `//` comment only when it starts a line or follows whitespace, `;`,
`{` or `)` — which keeps the `//` in every URL. Exits 1 when anything differs.
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = {".html", ".xml", ".json", ".txt", ".css", ".js", ".webmanifest"}
ISO = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)"


def build(source: Path, dest: Path) -> None:
    # Run from the repo, so both builds use its Gemfile; -s picks the tree to build.
    subprocess.run(["bundle", "exec", "jekyll", "build", "-q", "-s", str(source), "-d", str(dest)],
                   cwd=ROOT, check=True)


def site_time(site: Path) -> str | None:
    feed = site / "feed.xml"
    m = feed.exists() and re.search(r"<updated>(" + ISO + ")</updated>", feed.read_text())
    return m.group(1) if m else None


def normalize(text: str, clock: str | None, ignore_dates: bool) -> list[str]:
    if clock:
        text = text.replace(clock, "SITE_TIME")
    if ignore_dates:
        text = re.sub(ISO, "DATE", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"<!--(?!more-->).*?-->", "", text, flags=re.S)
    text = re.sub(r"(?m)(^|[\s;{)])//(?!/)[^\n]*", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" ?([{};,()<>=]) ?", r"\1", text)
    # One statement, rule or tag per line, so the diff points at the change.
    return re.sub(r"([;}>])", r"\1\n", text.strip()).splitlines()


def compare(base: Path, head: Path, ignore_dates: bool, context: int) -> int:
    clocks = site_time(base), site_time(head)
    files = sorted({p.relative_to(s) for s in (base, head) for p in s.rglob("*")
                    if p.is_file() and p.suffix in TEXT})
    changed = 0
    for rel in files:
        a, b = base / rel, head / rel
        if not a.exists() or not b.exists():
            print(f"{'added' if b.exists() else 'removed'}: {rel}")
            changed += 1
            continue
        x, y = a.read_text(errors="replace"), b.read_text(errors="replace")
        if x == y:
            continue
        nx = normalize(x, clocks[0], ignore_dates)
        ny = normalize(y, clocks[1], ignore_dates)
        if nx == ny:
            continue
        changed += 1
        print(f"\n=== {rel}  ({len(x):,} → {len(y):,} bytes)")
        sys.stdout.writelines(line + "\n" for line in difflib.unified_diff(
            nx, ny, "before", "after", n=context, lineterm=""))
    print(f"\n{changed} file(s) differ" if changed else "No difference beyond comments and whitespace.")
    return 1 if changed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ref", nargs="?", default="HEAD", help="git ref to compare against (default HEAD)")
    ap.add_argument("--ignore-dates", action="store_true", help="mask every ISO datetime")
    ap.add_argument("--keep", action="store_true", help="keep the temporary builds")
    ap.add_argument("-U", "--context", type=int, default=1, help="diff context lines (default 1)")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="diff-build-"))
    tree = tmp / "tree"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(tree), args.ref], cwd=ROOT, check=True)
    try:
        print(f"Building {args.ref}…", file=sys.stderr)
        build(tree, tmp / "before")
        print("Building the working tree…", file=sys.stderr)
        build(ROOT, tmp / "after")
        return compare(tmp / "before", tmp / "after", args.ignore_dates, args.context)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False)
        if args.keep:
            print(f"Builds kept in {tmp}/before and {tmp}/after", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
