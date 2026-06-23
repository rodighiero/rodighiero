#!/usr/bin/env python3
"""Build the publication similarity network for the home network view.

Reads publications from _publications/, machine-translates non-English
abstracts (cached), embeds title + abstract with all-MiniLM-L6-v2, and
writes _data/network.json with the node list and a pairwise cosine
similarity matrix. The home page consumes it via Liquid as
site.data.network.

Re-run after editing publications:

    KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import yaml
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
PUBS_DIR = ROOT / "_publications"
OUT = ROOT / "_data" / "network.json"
TRANS_CACHE = ROOT / "_data" / "translations-cache.json"
LAYOUT_SCRIPT = ROOT / "scripts" / "layout-network.js"


def precompute_layout(nodes: list[dict], similarity: list[list[float]]) -> dict:
    """Bake the force-directed layout offline via the shared Node script.

    layout-network.js reuses the exact d3-force config the browser used to run
    at render time, so the home page can draw the graph already settled without
    running the simulation client-side. Returns {canvas, positions, links}.
    """
    payload = json.dumps({"nodes": nodes, "similarity": similarity})
    proc = subprocess.run(
        ["node", str(LAYOUT_SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit("layout-network.js failed — is Node installed?")
    return json.loads(proc.stdout)

MODEL_NAME = "all-MiniLM-L6-v2"
# all-MiniLM-L6-v2 defaults to a 256 word-piece window but its architecture
# tops out at 512; raise it so longer abstracts/full texts inform the embedding.
MAX_SEQ_LENGTH = 512
EXCERPT_SEPARATOR = "<!--more-->"
TRANSLATE_CHUNK_CHARS = 1800  # Helsinki-NLP has a 512-token limit — chunk on sentences.


def parse_pub(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].replace(EXCERPT_SEPARATOR, " ").strip()
    # Drop the bibliography: everything from "## References" / "## Bibliography" to end.
    body = re.split(r"^##\s+(?:References|Bibliography)\s*$", body, maxsplit=1, flags=re.M)[0]
    # Kramdown footnote definitions, including indented continuation lines.
    body = re.sub(r"^\[\^[^\]]+\]:.*(?:\n[ \t]+.*)*", "", body, flags=re.M)
    body = re.sub(r"\[\^[^\]]+\]", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"^#+ .*$", "", body, flags=re.M)
    body = re.sub(r"`([^`]+)`", r"\1", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = re.sub(r"\s+", " ", body).strip()
    slug = path.stem
    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "lang": (fm.get("lang") or "en").lower(),
        "url": f"/{slug}",
        "text": f"{fm.get('title', '')}. {body}",
    }


def translate_long(text: str, translator) -> str:
    """Translate text potentially longer than the model's 512-token window."""
    if len(text) <= TRANSLATE_CHUNK_CHARS:
        return translator(text, max_length=512)[0]["translation_text"]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) > TRANSLATE_CHUNK_CHARS and cur:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return " ".join(
        translator(c, max_length=512)[0]["translation_text"] for c in chunks
    )


def translate_pubs(pubs: list[dict]) -> None:
    """Translate non-English publications to English in place, with on-disk caching."""
    cache: dict = {}
    if TRANS_CACHE.exists():
        cache = json.loads(TRANS_CACHE.read_text())

    needing = [p for p in pubs if p["lang"] != "en"]
    if not needing:
        return

    translator = None
    current_model: str | None = None
    for p in needing:
        h = hashlib.sha256(p["text"].encode("utf-8")).hexdigest()[:16]
        entry = cache.get(p["slug"])
        if entry and entry.get("hash") == h and entry.get("lang") == p["lang"]:
            p["text"] = entry["english"]
            print(f"  cached  {p['slug']}", file=sys.stderr)
            continue
        model_name = f"Helsinki-NLP/opus-mt-{p['lang']}-en"
        if translator is None or current_model != model_name:
            print(f"loading translator {model_name}…", file=sys.stderr)
            from transformers import pipeline
            translator = pipeline("translation", model=model_name)
            current_model = model_name
        print(f"  translating {p['slug']} ({p['lang']}→en)…", file=sys.stderr)
        en = translate_long(p["text"], translator)
        cache[p["slug"]] = {
            "hash": h,
            "lang": p["lang"],
            "english": en,
            "source_preview": p["text"][:160] + ("…" if len(p["text"]) > 160 else ""),
        }
        p["text"] = en

    TRANS_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def main() -> int:
    pubs: list[dict] = [r for r in (parse_pub(p) for p in sorted(PUBS_DIR.glob("*.md"))) if r]
    print(f"loaded {len(pubs)} publications", file=sys.stderr)

    non_english = [p for p in pubs if p["lang"] != "en"]
    if non_english:
        print(f"translating {len(non_english)} non-English publications…", file=sys.stderr)
        translate_pubs(pubs)

    print(f"loading model {MODEL_NAME}…", file=sys.stderr)
    model = SentenceTransformer(MODEL_NAME)
    model.max_seq_length = MAX_SEQ_LENGTH

    print("embedding documents…", file=sys.stderr)
    doc_vecs = model.encode(
        [p["text"] for p in pubs], normalize_embeddings=True, show_progress_bar=False
    )

    sim = (doc_vecs @ doc_vecs.T).astype(float)
    np.fill_diagonal(sim, 0)

    nodes = [
        {"i": i, "slug": p["slug"], "title": p["title"], "url": p["url"]}
        for i, p in enumerate(pubs)
    ]
    similarity = [[round(float(s), 4) for s in row] for row in sim]

    print("baking layout (node)…", file=sys.stderr)
    layout = precompute_layout(nodes, similarity)
    for node, (x, y) in zip(nodes, layout["positions"]):
        node["x"], node["y"] = x, y

    data = {
        "nodes": nodes,
        "similarity": similarity,
        "canvas": layout["canvas"],
        "links": layout["links"],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False))
    print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size:,} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
