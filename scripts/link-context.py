#!/usr/bin/env python3
"""Annotate lychee link-check failures with source context.

Reads lychee's markdown report (default lychee/out.md), extracts each
broken URL, then searches the Jekyll source tree to find where the URL
is referenced and what surrounds it: full citation if the URL is in a
markdown bullet, surrounding paragraph if it's in inline prose, or the
publication title if it sits in YAML front matter. Writes a richer
markdown summary to stdout (suitable for $GITHUB_STEP_SUMMARY).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPORT = Path(sys.argv[1] if len(sys.argv) > 1 else "lychee/out.md")
SEARCH_ROOTS = [
    "_publications",
    "_layouts",
    "_includes",
    "_data",
    "README.md",
    "_config.yml",
]

URL_LINE_RE = re.compile(
    r"\*\s*\[([^\]]+)\]\s*<(https?://[^>]+)>\s*\|\s*(.+)"
)
BULLET_RE = re.compile(r"^[-*+]\s+")


def collect_broken_urls(report_path: Path) -> dict[str, dict]:
    if not report_path.exists():
        return {}
    seen: dict[str, dict] = {}
    for line in report_path.read_text().splitlines():
        m = URL_LINE_RE.search(line.lstrip())
        if not m:
            continue
        status, url, reason = m.groups()
        if url not in seen:
            seen[url] = {"status": status, "reason": reason.strip()}
    return seen


def source_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        p = Path(root)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for ext in ("*.md", "*.html", "*.yml", "*.yaml"):
                files.extend(p.rglob(ext))
    return files


def front_matter_bounds(lines: list[str]) -> tuple[int, int] | None:
    if not lines or lines[0].strip() != "---":
        return None
    for j in range(1, len(lines)):
        if lines[j].strip() == "---":
            return (0, j)
    return None


def front_matter_title(lines: list[str]) -> str | None:
    fm = front_matter_bounds(lines)
    if not fm:
        return None
    for line in lines[1:fm[1]]:
        m = re.match(r'\s*title\s*:\s*"?([^"\n]+?)"?\s*$', line)
        if m:
            return m.group(1).strip()
    return None


def extract_context(lines: list[str], i: int) -> tuple[str, str]:
    fm = front_matter_bounds(lines)
    if fm and fm[0] < i < fm[1]:
        field = lines[i].split(":", 1)[0].strip()
        title = front_matter_title(lines) or "(untitled)"
        return ("front matter", f"`{field}` field of *{title}*")

    start = i
    while start > 0 and not BULLET_RE.match(lines[start].lstrip()):
        if not lines[start].strip():
            break
        start -= 1
    if BULLET_RE.match(lines[start].lstrip()):
        end = i
        while end + 1 < len(lines):
            nxt = lines[end + 1]
            if not nxt.strip() or BULLET_RE.match(nxt.lstrip()):
                break
            end += 1
        text = " ".join(l.strip() for l in lines[start:end + 1])
        return ("citation", BULLET_RE.sub("", text, count=1))

    start = i
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = i
    while end + 1 < len(lines) and lines[end + 1].strip():
        end += 1
    return ("inline", " ".join(l.strip() for l in lines[start:end + 1]))


def find_occurrences(urls: list[str]) -> dict[str, list[tuple[str, int, str, str]]]:
    out: dict[str, list[tuple[str, int, str, str]]] = {url: [] for url in urls}
    for f in source_files():
        try:
            lines = f.read_text().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines):
            for url in urls:
                if url in line:
                    kind, ctx = extract_context(lines, i)
                    out[url].append((str(f), i + 1, kind, ctx))
    return out


def main() -> int:
    urls = collect_broken_urls(REPORT)
    if not urls:
        return 0
    occurrences = find_occurrences(list(urls.keys()))

    print(f"**Broken links ({len(urls)})**\n")
    for n, (url, info) in enumerate(urls.items(), 1):
        hits = occurrences.get(url, [])
        if not hits:
            print(f"{n}. **[{info['status']}]** _(not found in source)_  ")
            print(f"   `{url}`")
            if not info["status"].isdigit():
                print(f"   _{info['reason']}_")
            print()
            continue
        primary = hits[0]
        file, line_no, kind, ctx = primary
        print(f"{n}. **[{info['status']}]** `{file}:{line_no}` ({kind})  ")
        print(f"   `{url}`  ")
        if not info["status"].isdigit():
            print(f"   _{info['reason']}_  ")
        print(f"   > {ctx}")
        if len(hits) > 1:
            others = ", ".join(f"`{f}:{ln}`" for f, ln, _, _ in hits[1:])
            print(f"   _also in:_ {others}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
