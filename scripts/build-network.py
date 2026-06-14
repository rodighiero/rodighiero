#!/usr/bin/env python3
"""Build the publication similarity network for /network-test/.

Reads publications from _publications/, computes sentence embeddings
for title + abstract via all-MiniLM-L6-v2, extracts KeyBERT keyphrases
per document, and computes pairwise cosine similarity plus per-pair
shared concepts. Writes _data/network.json, which the page consumes
via Liquid as site.data.network.

Re-run after editing publications:

    KMP_DUPLICATE_LIB_OK=TRUE python3 scripts/build-network.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import yaml
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
PUBS_DIR = ROOT / "_publications"
TYPES_FILE = ROOT / "_data" / "publication_types.yml"
OUT = ROOT / "_data" / "network.json"
TRANS_CACHE = ROOT / "_data" / "translations-cache.json"

MODEL_NAME = "all-MiniLM-L6-v2"
TRANSLATOR_MODEL = "Helsinki-NLP/opus-mt-it-en"
NGRAM_RANGE = (1, 2)
TOP_KEYWORDS = 8
TOP_SHARED = 3
MMR_DIVERSITY = 0.5
MIN_SHARED_SIM = 0.10
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
        "year": fm.get("year"),
        "type": fm.get("type"),
        "venue": fm.get("venue"),
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
    for p in needing:
        h = hashlib.sha256(p["text"].encode("utf-8")).hexdigest()[:16]
        entry = cache.get(p["slug"])
        if entry and entry.get("hash") == h and entry.get("lang") == p["lang"]:
            p["text"] = entry["english"]
            print(f"  cached  {p['slug']}", file=sys.stderr)
            continue
        if translator is None:
            print(f"loading translator {TRANSLATOR_MODEL}…", file=sys.stderr)
            from transformers import pipeline
            translator = pipeline(
                "translation", model=f"Helsinki-NLP/opus-mt-{p['lang']}-en"
            )
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
    types = yaml.safe_load(TYPES_FILE.read_text())
    pubs: list[dict] = []
    for p in sorted(PUBS_DIR.glob("*.md")):
        rec = parse_pub(p)
        if rec:
            rec["typeLabel"] = (types.get(rec["type"]) or {}).get("label", rec["type"])
            pubs.append(rec)

    print(f"loaded {len(pubs)} publications", file=sys.stderr)

    non_english = [p for p in pubs if p["lang"] != "en"]
    if non_english:
        print(f"translating {len(non_english)} non-English publications…", file=sys.stderr)
        translate_pubs(pubs)

    print(f"loading model {MODEL_NAME}…", file=sys.stderr)
    model = SentenceTransformer(MODEL_NAME)
    kw = KeyBERT(model=model)

    print("embedding documents…", file=sys.stderr)
    doc_vecs = model.encode(
        [p["text"] for p in pubs], normalize_embeddings=True, show_progress_bar=False
    )

    print("extracting keyphrases…", file=sys.stderr)
    keywords: list[list[str]] = []
    for i, p in enumerate(pubs):
        kws = kw.extract_keywords(
            p["text"],
            keyphrase_ngram_range=NGRAM_RANGE,
            stop_words="english",
            use_mmr=True,
            diversity=MMR_DIVERSITY,
            top_n=TOP_KEYWORDS,
        )
        keywords.append([k for k, _ in kws])
        print(f"  {i + 1:>2}/{len(pubs)} {p['slug']}: {keywords[-1][:3]}", file=sys.stderr)

    # Cache phrase embeddings: every unique keyphrase across the corpus
    all_phrases = sorted({kp for kps in keywords for kp in kps})
    print(f"embedding {len(all_phrases)} unique candidate phrases…", file=sys.stderr)
    phrase_vecs = model.encode(all_phrases, normalize_embeddings=True, show_progress_bar=False)
    phrase_idx = {p: i for i, p in enumerate(all_phrases)}

    sim = (doc_vecs @ doc_vecs.T).astype(float)
    np.fill_diagonal(sim, 0)

    print("computing shared concepts per pair…", file=sys.stderr)
    shared: dict[str, list[str]] = {}
    for i in range(len(pubs)):
        for j in range(i + 1, len(pubs)):
            if sim[i][j] < MIN_SHARED_SIM:
                continue
            candidates = list(dict.fromkeys(keywords[i] + keywords[j]))
            cv = phrase_vecs[[phrase_idx[c] for c in candidates]]
            score = (cv @ doc_vecs[i] + cv @ doc_vecs[j]) / 2
            order = np.argsort(-score)
            shared[f"{i},{j}"] = [candidates[k] for k in order[:TOP_SHARED]]

    nodes = [
        {
            "i": i,
            "slug": p["slug"],
            "title": p["title"],
            "year": p["year"],
            "type": p["type"],
            "typeLabel": p["typeLabel"],
            "venue": p["venue"],
            "url": p["url"],
            "keywords": keywords[i],
        }
        for i, p in enumerate(pubs)
    ]

    data = {
        "model": MODEL_NAME,
        "ngramRange": list(NGRAM_RANGE),
        "topKeywords": TOP_KEYWORDS,
        "nodes": nodes,
        "similarity": [[round(float(s), 4) for s in row] for row in sim],
        "shared": shared,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False))
    print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size:,} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
