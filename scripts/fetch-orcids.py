"""Fetch publisher-deposited ORCIDs for exact publication-author matches.

Run with `uv run scripts/fetch-orcids.py`. Writes a local snapshot; the site
never calls Crossref at build time or from a reader's browser. Existing verified
entries survive missing deposits and request failures. Conflicts abort the update.
"""
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "people.json"


def normalized(name):
    # Preserve every name token, including middle initials: no fuzzy identity matches.
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFC", name).casefold()))


def orcid_url(value):
    match = re.fullmatch(r"https?://orcid.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])", value)
    if not match:
        return None
    digits = match[1].replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    check = (12 - total % 11) % 11
    if digits[-1] != ("X" if check == 10 else str(check)):
        return None
    return "https://orcid.org/" + match[1]


def main():
    people = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    works = {}
    for path in sorted((ROOT / "_publications").glob("*.md")):
        front = yaml.safe_load(path.read_text().split("---", 2)[1])
        doi = re.fullmatch(r"https?://(?:dx\.)?doi.org/(10\..+)", str(front.get("doi", "")))
        if doi:
            names = works.setdefault(doi[1], set())
            names.update(str(front.get("author", "")).split(" and "))
    failures = []
    for doi, names in works.items():
        source = "https://api.crossref.org/works/" + quote(doi, safe="")
        try:
            request = Request(source, headers={"User-Agent": "RodighieroMetadata/1.0 (https://dariorodighiero.com)"})
            with urlopen(request, timeout=30) as response:
                authors = json.load(response)["message"].get("author", [])
        except Exception as error:
            failures.append(doi)
            print(f"Skipped {doi}: {error}")
            continue
        for name in sorted(names):
            matches = [a for a in authors if normalized(name) == normalized(
                a.get("given", "") + " " + a.get("family", ""))]
            if len(matches) != 1:
                continue
            orcid = orcid_url(matches[0].get("ORCID", ""))
            if not orcid:
                continue
            previous = people.get(name)
            if previous and previous["orcid"] != orcid:
                raise ValueError(f"Conflicting ORCIDs for {name}: {previous['orcid']} / {orcid}")
            entry = people.setdefault(name, {"orcid": orcid, "sources": []})
            if source not in entry["sources"]:
                entry["sources"].append(source)
            entry["sources"].sort()
        time.sleep(0.2)
    OUTPUT.write_text(json.dumps(dict(sorted(people.items())), ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {len(people)} author identities; {len(failures)} unavailable records.")


if __name__ == "__main__":
    main()
