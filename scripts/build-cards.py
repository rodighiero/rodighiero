#!/usr/bin/env python3
"""Layer the homepage cluster-card *text* onto _data/network.json.

The heavy network math — embeddings, force layout, and cluster **membership** —
lives in build-network.py, which writes each cluster's structural fields
(id, label, terms, slugs, years, span, size, anchor_slug). This script owns only
the **presentation**: the hand-written card `title` and the short `filter_label`
shown in the search box. Because it needs no model, it runs in a blink, so a card
reword is a one-second `python3 scripts/build-cards.py` instead of a full rebuild.

  python3 scripts/build-cards.py     # cards only — reads & rewrites network.json
  build-network.py                   # runs the full network build, then calls this

Keys are the auto TF-IDF `label` each cluster carries; a cluster without an entry
falls back to a generated template. If a label shifts because membership changed,
update its key here (build-network.py prints the current labels).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_data" / "network.json"

# Editable, hand-written card titles, grounded in each cluster's mutual (strong-edge)
# core. Three short sentences per card, each with a fixed scope:
#   1. Subject  — the thing studied.
#   2. Approach — what the work does to it (method, gesture, lens).
#   3. Stakes   — why it matters (the insight or question it opens).
CLUSTER_TITLES = {
    "Analogous City": "Aldo Rossi collaged the city of memory in 1976. These projects restage it across archives, museums, installations, and data-driven study. A modernist monument returns for the digital age.",
    "Affinity": "Something quiet draws researchers toward one another. These projects visualize the hidden ties that bind them into productive, creative communities. A way of seeing what holds a community together.",
    "Covid": "A pandemic unfolds through the eyes of the scientists who tracked it. These projects collect, translate, and give form to work that would otherwise stay invisible. A global crisis becomes something we can look at.",
    "Peirce Manuscripts": "Charles S. Peirce filled thousands of pages with hand-drawn diagrams. These projects digitize, transcribe, and interpret them with vision-language models. Machines learn to read what only scholars once could.",
    "Représentation": "Researchers cite and gather in shifting constellations. These projects turn conferences into networks of authors linked by their shared vocabulary. A field takes shape before your eyes.",
}

# Short label shown in the search box when a cluster filter is active (data-filter-label),
# overriding the auto TF-IDF label. The `label` itself is left unchanged (it still keys
# CLUSTER_TITLES, sorts alphabetically, and identifies the cluster).
CLUSTER_LABELS = {
    "Affinity": "Mapping Affinities",
    "Covid": "Covid-19 Cartography",
    "Représentation": "Mapping Scientific Communities",
}


def enrich_clusters(clusters: list[dict]) -> list[dict]:
    """Add `title` and `filter_label` to each cluster from its auto `label`."""
    for c in clusters:
        label = c["label"]
        c["filter_label"] = CLUSTER_LABELS.get(label, label)
        c["title"] = CLUSTER_TITLES.get(
            label,
            f"Explore the {label} cluster — {c['size']} works "
            f"drawn together by {', '.join(c.get('terms', []))}",
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
