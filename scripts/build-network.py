#!/usr/bin/env python3
"""Build the publication similarity network for the home network view.

Reads publications from _publications/, embeds title + full text with
Alibaba-NLP/gte-base-en-v1.5, and writes _data/network.json with the node list and
a pairwise cosine similarity matrix. The home page consumes it via Liquid as
site.data.network.

Only English-language publications are embedded and compared — the
similarity network is English-only. Non-English publications still appear
as nodes (positioned by the same force layout) but are never a similarity
source or candidate, so they have no "closest by embedding" data; a
non-English publication that is a human translation of an English one
(`translation_of` in its front matter) is instead pinned beside its
original by a forced edge.

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
LAYOUT_SCRIPT = ROOT / "scripts" / "layout-network.js"
# Local, gitignored embedding cache: maps a per-document key (model + seq length
# + cleaned text hash) to its 768-dim vector, so re-runs only encode documents
# whose text actually changed. Byte-identical to a full re-embed — same numbers,
# same graph — but turns "I added one article" from a full-corpus encode into a
# single-document one, and a no-content-change re-run skips model loading
# entirely. Delete the file to force a clean rebuild.
CACHE_PATH = ROOT / "scripts" / ".embedding-cache.npz"


def _cache_key(text: str) -> str:
    """Content hash keyed to the model + window, so either change invalidates it."""
    h = hashlib.sha256()
    h.update(f"{MODEL_NAME}\x00{MAX_SEQ_LENGTH}\x00".encode("utf-8"))
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def _load_cache() -> dict[str, np.ndarray]:
    if not CACHE_PATH.exists():
        return {}
    try:
        with np.load(CACHE_PATH) as z:
            return {k: z[k] for k in z.files}
    except Exception:  # a corrupt/incompatible cache is just rebuilt
        return {}


def _save_cache(cache: dict[str, np.ndarray]) -> None:
    np.savez(CACHE_PATH, **cache)


def precompute_layout(
    nodes: list[dict], similarity: list[list[float]], translations: dict[int, int]
) -> dict:
    """Bake the force-directed layout offline via the shared Node script.

    layout-network.js reuses the exact d3-force config the browser used to run
    at render time, so the home page can draw the graph already settled without
    running the simulation client-side. `translations` maps a translation node's
    index to its original's index: those nodes join the simulation as regular
    nodes but their only edge is a forced 1.00 link to the original (no
    similarity edge), so the layout arranges them appended to their source.
    Returns {canvas, positions, links}.
    """
    payload = json.dumps(
        {"nodes": nodes, "similarity": similarity, "translations": translations}
    )
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

MODEL_NAME = "Alibaba-NLP/gte-base-en-v1.5"
# gte-base-en-v1.5 has an 8192 word-piece window, so full-text articles inform
# the embedding instead of being truncated to their first few hundred tokens
# (the previous bge-base-en-v1.5 capped at 512, discarding 90%+ of long papers).
MAX_SEQ_LENGTH = 8192
# Default to CPU for portability. Encoding at MAX_SEQ_LENGTH is the slow step
# (full-text articles run up to several thousand tokens), but the embedding
# cache (see CACHE_PATH) means only changed documents are re-encoded; on Apple
# Silicon, NETWORK_DEVICE=mps (or cuda) speeds up the cold/first encode.
DEVICE = os.environ.get("NETWORK_DEVICE", "cpu")
EXCERPT_SEPARATOR = "<!--more-->"

# ── Body-text scrubbing for the embedder ──────────────────────────────────────
# _clean_body() reduces a Markdown abstract/body to plain prose so only meaningful
# words reach the model. Patterns are compiled once here and applied in the order
# below; ordering matters (e.g. links are unwrapped before parentheses are pulled,
# emphasis after tags). Publication *titles* are cleaned separately, if at all.
_BIB_HEADING   = re.compile(r"^##\s+(?:References|Bibliography|Références|Bibliographie)\s*$", re.M)
_FOOTNOTE_DEF  = re.compile(r"^\[\^[^\]]+\]:.*(?:\n[ \t]+.*)*", re.M)  # def + indented continuations
_FOOTNOTE_REF  = re.compile(r"\[\^[^\]]+\]")                           # inline [^n]
_MD_LINK       = re.compile(r"\[([^\]]+)\]\([^)]+\)")                  # [text](url) → text
_PAREN         = re.compile(r"\([^()]*\)")                             # (aside); looped for nesting
_LIST_MARKER   = re.compile(r"(?<![^\s:;,–—-])[0-9a-zA-Z]{1,3}\)\s*")  # leftover "a) " / "1) "
_HEADING       = re.compile(r"^#+ .*$", re.M)
_INLINE_CODE   = re.compile(r"`([^`]+)`")
_HTML_TAG      = re.compile(r"<[^>]+>")
_LIQUID        = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)            # {% … %} / {{ … }}
_BLOCKQUOTE    = re.compile(r"^(?:[ \t]*>[ \t]?)+", re.M)             # "> " / nested "> > "
_EMPHASIS      = (
    (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),          # **bold**
    (re.compile(r"__([^_]+)__"), r"\1"),              # __bold__
    (re.compile(r"\*([^*]+)\*"), r"\1"),              # *italic*
    (re.compile(r"(?<!\w)_([^_]+)_(?!\w)"), r"\1"),   # _italic_ (word-boundary only)
)
_WHITESPACE    = re.compile(r"\s+")
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,;:!?])")


def _clean_body(body: str) -> str:
    """Strip Markdown/Liquid scaffolding and reference apparatus, leaving prose."""
    body = _BIB_HEADING.split(body, maxsplit=1)[0]  # drop the bibliography onward
    body = _FOOTNOTE_DEF.sub("", body)
    body = _FOOTNOTE_REF.sub("", body)
    body = _MD_LINK.sub(r"\1", body)
    while _PAREN.search(body):                       # citations, figure refs, "(EPFL)", …
        body = _PAREN.sub("", body)
    body = _LIST_MARKER.sub("", body)
    body = _HEADING.sub("", body)
    body = _INLINE_CODE.sub(r"\1", body)
    body = _HTML_TAG.sub("", body)
    body = _LIQUID.sub("", body)
    body = _BLOCKQUOTE.sub("", body)
    for pat, repl in _EMPHASIS:
        body = pat.sub(repl, body)
    body = _WHITESPACE.sub(" ", body).strip()
    body = _SPACE_BEFORE_PUNCT.sub(r"\1", body)      # tidy "tools ." → "tools."
    return body


def parse_pub(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    body = _clean_body(parts[2].replace(EXCERPT_SEPARATOR, " ").strip())
    slug = path.stem
    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "lang": (fm.get("lang") or "en").lower(),
        "translation_of": fm.get("translation_of"),
        "url": f"/{slug}",
        "text": f"{fm.get('title', '')}. {body}",
    }


def main() -> int:
    pubs: list[dict] = [r for r in (parse_pub(p) for p in sorted(PUBS_DIR.glob("*.md"))) if r]
    print(f"loaded {len(pubs)} publications", file=sys.stderr)

    # Validate translation_of references up front: each must point to an
    # existing publication that is not itself a translation.
    by_slug = {p["slug"]: p for p in pubs}
    for p in pubs:
        src = p.get("translation_of")
        if not src:
            continue
        orig = by_slug.get(src)
        if orig is None:
            raise SystemExit(f"{p['slug']}: translation_of '{src}' not found in _publications/")
        if orig.get("translation_of"):
            raise SystemExit(f"{p['slug']}: translation_of '{src}' is itself a translation")

    # The similarity network is English-only: non-English publications are
    # never embedded (no machine translation) and their similarity rows stay
    # zero — they still appear in the graph as nodes (see the translations
    # block below and layout-network.js's isNonEnglish handling) but are
    # never a similarity source or candidate.
    en_idx = [i for i, p in enumerate(pubs) if p["lang"] == "en"]
    en_texts = [pubs[i]["text"] for i in en_idx]
    keys = [_cache_key(t) for t in en_texts]

    # Encode only what the cache is missing; a run with no text changes never
    # loads the model at all.
    cache = _load_cache()
    missing = [(k, t) for k, t in zip(keys, en_texts) if k not in cache]
    print(
        f"embedding {len(en_idx)} English-language documents — "
        f"{len(en_idx) - len(missing)} cached, {len(missing)} to encode…",
        file=sys.stderr,
    )
    if missing:
        print(f"loading model {MODEL_NAME}…", file=sys.stderr)
        model = SentenceTransformer(MODEL_NAME, device=DEVICE, trust_remote_code=True)
        model.max_seq_length = MAX_SEQ_LENGTH
        new_vecs = model.encode(
            [t for _, t in missing], normalize_embeddings=True, show_progress_bar=False
        )
        for (k, _), v in zip(missing, new_vecs):
            cache[k] = np.asarray(v, dtype=np.float32)
        _save_cache({k: cache[k] for k in keys})  # persist, pruning stale entries

    en_vecs = np.vstack([cache[k] for k in keys]) if keys else np.zeros((0, 0))

    sim = np.zeros((len(pubs), len(pubs)))
    idx = np.array(en_idx)
    if len(idx):
        sim[np.ix_(idx, idx)] = en_vecs @ en_vecs.T
    np.fill_diagonal(sim, 0)

    nodes = [
        {"i": i, "slug": p["slug"], "title": p["title"], "url": p["url"], "lang": p["lang"]}
        for i, p in enumerate(pubs)
    ]
    similarity = [[round(float(s), 4) for s in row] for row in sim]

    # ── Translations join the layout, appended to their originals ──
    # A publication with `translation_of` is the same work in another language.
    # It takes part in the force layout as a regular node, but its only edge is a
    # forced 1.00 link to its original (translations are not similarity-link
    # candidates for any node, and — like every non-English publication — were
    # never embedded, so they have no "closest by embedding" data of their own),
    # so the simulation arranges it beside — and collision-separated from — its
    # source.
    slug_idx = {p["slug"]: i for i, p in enumerate(pubs)}
    translations = {
        i: slug_idx[p["translation_of"]]
        for i, p in enumerate(pubs)
        if p.get("translation_of")
    }

    print(
        f"baking layout (node) — {len(nodes)} nodes, {len(translations)} translations…",
        file=sys.stderr,
    )
    layout = precompute_layout(nodes, similarity, translations)
    print(f"layout seed: {layout.get('seed')}", file=sys.stderr)
    for node, (x, y) in zip(nodes, layout["positions"]):
        node["x"], node["y"] = x, y
    for i in translations:
        nodes[i]["tr"] = True

    data = {
        "seed": layout.get("seed"),
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
