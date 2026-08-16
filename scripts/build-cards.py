#!/usr/bin/env python3
"""Layer the homepage cluster-card *text* onto _data/network.json.

The heavy network math — embeddings, force layout, and cluster **membership** —
lives in build-network.py, which writes each cluster's structural fields
(id, label, terms, slugs, years, span, size, anchor_slug). This script owns only
the **presentation**: the hand-written card `title` and `description`, plus the
short `filter_label` shown in the search box. Because it needs no model, it runs in
a blink, so a card reword is a one-second `python3 scripts/build-cards.py` instead
of a full rebuild.

  python3 scripts/build-cards.py     # cards only — reads & rewrites network.json
  build-network.py                   # runs the full network build, then calls this

Keys are the auto TF-IDF `label` each cluster carries; a cluster without an entry
falls back to that label and a generated description. If a label shifts because
membership changed, update its key here (build-network.py prints the current labels).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_data" / "network.json"

# Editable, hand-written card text, grounded in each cluster's mutual (strong-edge)
# core. A card reads like a publication card — a short title over a quieter
# description — so each entry is written to that shape:
#   title       — the subject, as a name: what the cluster is about.
#   description — two short sentences: what the work does to it (method, gesture,
#                 lens), then why it matters (the insight or question it opens).
#   filter      — optional; the chip shown in the search box when the filter is
#                 active. Defaults to the title, which is normally the right name.
CLUSTER_CARDS = {
    "Analogous City": {
        "title": "Analogous City",
        "description": "Aldo Rossi’s 1976 collage of the city of memory, restaged across archives, museums, and installations. A modernist monument returns for the digital age.",
    },
    "Affinity": {
        "title": "Mapping Affinities",
        "description": "Visualizing the quiet ties that draw researchers toward one another. A way of seeing what holds a community together.",
    },
    "Covid": {
        "title": "Covid-19 Cartography",
        "description": "Collecting and giving form to the work of the scientists who tracked the pandemic. A global crisis becomes something we can look at.",
    },
    "Peirce Manuscripts": {
        "title": "Peirce Manuscripts",
        "description": "Digitizing and interpreting thousands of hand-drawn diagrams with vision-language models. Machines learn to read what only scholars once could.",
    },
    "Représentation": {
        "title": "Mapping Science",
        "description": "Turning conferences into networks of authors linked by a shared vocabulary. A field takes shape before your eyes.",
    },
    "Thesaurus": {
        "title": "Controlled Vocabularies",
        "description": "Thesauri for organizing scientific and library collections, from a European Commission retrieval system to the semantic web. The groundwork before visualization.",
    },
}


def enrich_clusters(clusters: list[dict]) -> list[dict]:
    """Add `title`, `description` and `filter_label` to each cluster from its auto `label`."""
    unkeyed = []
    for c in clusters:
        label = c["label"]
        card = CLUSTER_CARDS.get(label, {})
        # Without an entry, fall back to the auto label and a template drawn from
        # the cluster's own TF-IDF terms — never a blank card.
        if not card:
            unkeyed.append(label)
        c["title"] = card.get("title", label)
        c["description"] = card.get(
            "description",
            f"{c['size']} works drawn together by {', '.join(c.get('terms', []))}.",
        )
        c["filter_label"] = card.get("filter", c["title"])
    # The fallback is a safety net, not an outcome: a label shifts whenever cluster
    # membership changes, and the auto text ships to the homepage looking deliberate.
    # Say so loudly rather than letting a reworded card silently disappear.
    if unkeyed:
        print(
            "WARNING: no CLUSTER_CARDS entry for "
            + ", ".join(repr(l) for l in unkeyed)
            + f" — {'these clusters' if len(unkeyed) > 1 else 'this cluster'} shipped auto text. "
            "Add the key(s) to build-cards.py and re-run.",
            file=sys.stderr,
        )
    return clusters


def main() -> int:
    if not OUT.exists():
        print(f"{OUT.relative_to(ROOT)} not found — run build-network.py first", file=sys.stderr)
        return 1
    data = json.loads(OUT.read_text(encoding="utf-8"))
    enrich_clusters(data.get("clusters", []))
    OUT.write_text(json.dumps(data, ensure_ascii=False))
    print(
        "wrote cards: "
        + ", ".join(f"{c['filter_label']}" for c in data.get("clusters", [])),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
