#!/usr/bin/env python3
"""Build the publication similarity network for the home network view.

Reads publications from _publications/, embeds title + full text with
Alibaba-NLP/gte-base-en-v1.5, and writes _data/network.json with the baked
force-layout node list (positions), the link list, and each node's `related`
array (its three closest works). The home page consumes it via Liquid as
site.data.network.

Every ORIGINAL work is embedded in one space — English natively, non-English
originals via machine translation — so all originals are first-class similarity
nodes and can carry graph edges. A translation is not embedded: it borrows its
source's vector and is pinned beside it by a forced dashed edge. The per-node
`related` list is the single "three closest" source, shared by the network
selection panel and the publication pages.

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


def _load_trans_cache() -> dict[str, str]:
    if not TRANS_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(TRANS_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:  # a corrupt cache is just rebuilt
        return {}


def _save_trans_cache(cache: dict[str, str]) -> None:
    TRANS_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def _get_translator(lang: str, models: dict) -> tuple:
    """Lazily load the opus-mt tokenizer/model for a source language."""
    if lang not in models:
        from transformers import MarianMTModel, MarianTokenizer

        name = OPUS_MODELS[lang]
        print(f"loading translator {name}…", file=sys.stderr)
        models[lang] = (
            MarianTokenizer.from_pretrained(name),
            MarianMTModel.from_pretrained(name),
        )
    return models[lang]


def _translate(text: str, lang: str, cache: dict[str, str], models: dict) -> str:
    """Machine-translate `text` (in `lang`) to English, cached per source text.

    opus-mt has a ~512-token window, so the (already scrubbed, single-line) prose
    is split on sentence boundaries and packed into character-budgeted chunks
    that are translated in batches and rejoined. Deterministic (beam search, no
    sampling), so a given source text always yields the same English.
    """
    if lang not in OPUS_MODELS:
        raise SystemExit(f"no opus-mt model configured for language '{lang}'")
    key = hashlib.sha256(f"{OPUS_MODELS[lang]}\x00{text}".encode("utf-8")).hexdigest()
    if key in cache:
        return cache[key]

    chunks: list[str] = []
    cur = ""
    for sent in _SENT_SPLIT.split(text):
        if cur and len(cur) + len(sent) + 1 > _TRANS_CHARS:
            chunks.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        chunks.append(cur)

    tok, mdl = _get_translator(lang, models)
    out: list[str] = []
    for i in range(0, len(chunks), 8):
        batch = chunks[i : i + 8]
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        gen = mdl.generate(**enc, max_length=512, num_beams=4)
        out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    result = " ".join(out)
    cache[key] = result
    return result


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

# ── Per-document "related" suggestions ────────────────────────────────────────
# The similarity *network* (graph layout + links + the home page's click panel)
# stays English-only and unchanged. Independently, every publication page shows
# its three closest works — and for that a non-English publication needs a
# vector in the *same* English embedding space. We get there by machine
# translation (Option A): a non-English ORIGINAL is translated to English with a
# small offline opus-mt model and embedded like any English document; a
# TRANSLATION reuses its English source's vector (it is the same work), so no
# machine translation of translations is needed. Only fr/it originals exist
# today; add a model here if another source language appears.
OPUS_MODELS = {
    "fr": "Helsinki-NLP/opus-mt-fr-en",
    "it": "Helsinki-NLP/opus-mt-it-en",
}
# Committed network.json is the artifact; this translation cache (like the
# embedding cache) is a local, gitignored accelerator keyed by model + source
# text, so re-runs re-translate only originals whose text changed.
TRANS_CACHE_PATH = ROOT / "scripts" / ".translation-cache.json"
RELATED_K = 3            # suggestions shown per publication
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_TRANS_CHARS = 1200      # per-chunk char budget, kept well under the 512-token window

# ── Auto clusters → homepage filter cards ─────────────────────────────────────
# Connected components of the baked similarity-link graph are treated as research
# clusters; each component of at least MIN_CLUSTER_SIZE works becomes a homepage
# filter card, auto-labeled by TF-IDF over its members' text. See build_clusters().
MIN_CLUSTER_SIZE = 3
CLUSTER_TERMS = 3        # supporting keywords kept per cluster (label is terms[0])
_WORD_RE = re.compile(r"[a-zàâäçéèêëîïôöùûüÿœ']{4,}")
# Domain-generic and multilingual function words are filtered before TF-IDF so a
# cluster's distinctive vocabulary (peirce, rossi, affinity, covid…) rises to the
# top. Includes English filler, this corpus's ubiquitous domain terms (visual,
# data, network…), and common French/Italian stopwords (labels span all three).
_CLUSTER_STOP = set(
    """a an and or of to in for on with as by from is are be was were this that these those
    we our us using use used it its their they them can more most into at than not only also
    such other about between within across over under out up off two one three first second
    new each any all how what when where which who whom whose why while their there here
    visual data information design paper article study research work works
    figure figures based approach method methods model models tool tools case study studies
    through via toward towards make making made give given show shown see seen read reading
    le la les un une des du de et en est qui que qui pour dans sont avec sur ils elle nous vous
    leur ses aux ces cette dun dune plus comme mais ou ont nos vos leurs cet
    il lo gli che per con della delle degli dei nel nella nelle una uno non piu come sono anche
    questo questa questi queste dal dei alla allo agli sul sulla suoi loro""".split()
)

# The card *text* (each cluster's hand-written `title` and short `filter_label`) is
# layered on afterwards by scripts/build-cards.py, which keys off the auto TF-IDF
# `label` this file emits. main() invokes it once the structural JSON is written, so
# a full network build still produces complete cards; rewording a card alone is a
# fast `python3 scripts/build-cards.py` with no model in the loop.


def _tokens(text: str) -> list[str]:
    """Lowercase word tokens (4+ letters, accents kept), function words dropped."""
    return [w for w in _WORD_RE.findall(text.lower()) if w not in _CLUSTER_STOP]


def _uf(n: int, links: list[dict]) -> list[int]:
    """Union-find over the links; returns each node's (flattened) component root."""
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for l in links:
        parent[find(l["source"])] = find(l["target"])
    return [find(i) for i in range(n)]


def _year_key(year) -> float:
    """Sort key placing 'Forthcoming'/unknown newest; numeric years by value."""
    try:
        return float(year)
    except (TypeError, ValueError):
        return float("inf")  # Forthcoming / missing sorts as the newest


def build_clusters(pubs: list[dict], links: list[dict]) -> list[dict]:
    """Turn connected components of the similarity graph into labeled clusters.

    Each component with >= MIN_CLUSTER_SIZE works becomes a cluster; its label and
    supporting terms come from a TF-IDF ranking (unigrams + adjacent bigrams) over
    the members' cleaned text against the whole corpus, so a component's distinctive
    vocabulary names it. Emits, per cluster: id, label, terms, member slugs, the
    newest member's slug (for placement), the year span, and the size — ordered by
    size descending. Deterministic: components and text are seed-independent.

    Two tiers of edge decide clusters. A cluster only **qualifies** on the
    **mutual** backbone — the reciprocal mutual-kNN edges plus the forced
    translation edges: a component needs >= MIN_CLUSTER_SIZE **original** works
    (translations never count toward the size) joined by those strong edges alone to
    become a cluster (the weak one-directional fallback links `fb` would otherwise
    glue isolated nodes on and inflate grab-bag components).
    Once a cluster qualifies, its **membership** is broadened along the fallback
    edges — pulling in nodes that reach the cluster only through a rescue link — so
    the filter card also covers them. A fallback edge is followed only when it does
    not merge two separate mutual clusters (an ambiguous bridge), in which case the
    qualifying clusters keep their mutual members and the fallback link is ignored.
    """
    n = len(pubs)
    # Per-document term counts (unigrams + bigrams) and document frequencies.
    doc_terms: list[dict[str, int]] = []
    df: dict[str, int] = {}
    for p in pubs:
        toks = _tokens(p["text"])
        grams = list(toks)
        grams += [f"{toks[k]} {toks[k + 1]}" for k in range(len(toks) - 1)]
        counts: dict[str, int] = {}
        for g in grams:
            counts[g] = counts.get(g, 0) + 1
        doc_terms.append(counts)
        for g in counts:
            df[g] = df.get(g, 0) + 1

    def label_terms(members: list[int]) -> list[str]:
        score: dict[str, float] = {}
        for i in members:
            for term, tf in doc_terms[i].items():
                idf = np.log(n / (1 + df[term]))
                score[term] = score.get(term, 0.0) + tf * idf
        ranked = sorted(score, key=lambda t: -score[t])
        unigrams = [t for t in ranked if " " not in t]
        top_uni = set(unigrams[:6])
        # Prefer a two-word label, but only a *real* phrase: it must recur (df ≥ 2)
        # and both its words must themselves be top unigrams of this cluster — so
        # "surprise machines" / "analogous city" qualify while a chance adjacency
        # like "cartography covid" (cartography isn't a top term here) is rejected,
        # falling back to the top unigram ("covid").
        def good_bigram(b: str) -> bool:
            a, c = b.split(" ", 1)
            return df.get(b, 0) >= 2 and a in top_uni and c in top_uni

        label = next((t for t in ranked[:10] if " " in t and good_bigram(t)), "")
        if not label:
            label = unigrams[0] if unigrams else ""
        terms: list[str] = []
        for t in unigrams:
            if t in label:
                continue
            terms.append(t)
            if len(terms) == CLUSTER_TERMS:
                break
        return [label, *terms]

    # A translation is the same work as its original, so it never counts toward a
    # cluster's size — neither for qualification nor in the reported `size`. It stays
    # a member (its slug is kept, so its gallery card lights up when filtering).
    is_trans = [bool(pubs[i].get("translation_of")) for i in range(n)]

    def n_works(members: list[int]) -> int:
        return sum(1 for i in members if not is_trans[i])

    # Mutual backbone (qualification) vs. full graph incl. fallback (expansion).
    mutual = [l for l in links if not l.get("fb")]
    mroot = _uf(n, mutual)
    froot = _uf(n, links)
    mgroups: dict[int, list[int]] = {}
    for i in range(n):
        mgroups.setdefault(mroot[i], []).append(i)
    full_members: dict[int, list[int]] = {}
    for i in range(n):
        full_members.setdefault(froot[i], []).append(i)
    # Roots of the qualifying mutual clusters (counting original works only, not
    # translations), and how many seeds share each full component.
    seed_roots = [r for r, m in mgroups.items() if n_works(m) >= MIN_CLUSTER_SIZE]
    seeds_per_full: dict[int, list[int]] = {}
    for r in seed_roots:
        seeds_per_full.setdefault(froot[r], []).append(r)

    clusters = []
    for r in seed_roots:
        fr = froot[r]
        # Expand along fallback edges only when this cluster is the sole seed in its
        # full component; an ambiguous bridge between two seeds keeps mutual members.
        members = full_members[fr] if len(seeds_per_full[fr]) == 1 else mgroups[r]
        ordered = sorted(members, key=lambda i: (-_year_key(pubs[i]["year"]), pubs[i]["title"]))
        years = [int(pubs[i]["year"]) for i in members if str(pubs[i]["year"]).isdigit()]
        ys, ye = (min(years), max(years)) if years else (None, None)
        lt = label_terms(members)
        label = lt[0].title()
        # `title`/`filter_label` are added later by build-cards.py (keyed on `label`).
        clusters.append(
            {
                "label": label,
                "terms": lt[1:],
                "slugs": [pubs[i]["slug"] for i in ordered],
                "year_start": ys,
                "year_end": ye,
                "span": f"{ys}–{ye}" if ys is not None else "",
                "size": n_works(members),
            }
        )
    clusters.sort(key=lambda c: -c["size"])
    for k, c in enumerate(clusters):
        c["id"] = k
        c["action"] = f"cluster:{k}"

    # Anchor each cluster to the **midpoint of its span** so the cards spread through
    # the timeline instead of piling at one end (anchoring on year_start pushes them
    # all low, on year_end all to the top). The gallery lists works year-descending, so
    # `anchor_slug` is the first publication at or below the span's mid-year — the card
    # renders at the head of that year (or the nearest older year that has one). An
    # undated cluster (mid = -inf) falls back to the oldest work, so the anchor always
    # names a real publication and the homepage needs no separate append pass.
    gallery = sorted(pubs, key=lambda p: (-_year_key(p["year"]), p["title"]))
    oldest = gallery[-1]["slug"] if gallery else ""
    for c in clusters:
        ys, ye = c["year_start"], c["year_end"]
        mid = (ys + ye) / 2 if ys is not None else float("-inf")
        c["anchor_slug"] = next(
            (p["slug"] for p in gallery if _year_key(p["year"]) <= mid), oldest
        )
    return clusters

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
        "year": fm.get("year"),
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

    # Embed every ORIGINAL work into one space: English publications natively,
    # and (below) non-English originals after machine translation. Translations
    # are never embedded — duplicates of their source, they borrow its vector for
    # the `related` lists and are attached to it by a forced dashed edge. The
    # `similarity` matrix and the graph are built from these original vectors;
    # non-English originals are first-class similarity nodes.
    en_idx = [i for i, p in enumerate(pubs) if p["lang"] == "en"]
    en_texts = [pubs[i]["text"] for i in en_idx]
    keys = [_cache_key(t) for t in en_texts]

    # Non-English originals (a non-English publication that is not itself a
    # translation): translate → English, so they can be embedded alongside the
    # English works and ranked against them for suggestions.
    ne_orig_idx = [
        i for i, p in enumerate(pubs) if p["lang"] != "en" and not p.get("translation_of")
    ]
    trans_cache = _load_trans_cache()
    translators: dict = {}
    ne_texts: list[str] = []
    if ne_orig_idx:
        print(
            f"translating {len(ne_orig_idx)} non-English original(s) to English…",
            file=sys.stderr,
        )
        for i in ne_orig_idx:
            ne_texts.append(
                _translate(pubs[i]["text"], pubs[i]["lang"], trans_cache, translators)
            )
        if translators:  # persist only if a model actually ran
            _save_trans_cache(trans_cache)
    ne_keys = [_cache_key(t) for t in ne_texts]

    # Encode only what the cache is missing; a run with no text changes never
    # loads the model at all.
    cache = _load_cache()
    all_keys, all_texts = keys + ne_keys, en_texts + ne_texts
    missing = [(k, t) for k, t in zip(all_keys, all_texts) if k not in cache]
    print(
        f"embedding {len(all_texts)} documents "
        f"({len(en_idx)} English + {len(ne_orig_idx)} translated) — "
        f"{len(all_texts) - len(missing)} cached, {len(missing)} to encode…",
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
        _save_cache({k: cache[k] for k in all_keys})  # persist, pruning stale entries

    nodes = [
        {"i": i, "slug": p["slug"], "title": p["title"], "url": p["url"], "lang": p["lang"]}
        for i, p in enumerate(pubs)
    ]

    # ── One embedding space, one cosine matrix, two consumers ──
    # Give every publication a vector: an original its own (English native or
    # non-English machine-translated), a translation its source's (same work).
    # The resulting `sim` serves both:
    #   • the graph layout — layout-network.js skips translation nodes, so their
    #     rows/columns are simply never read and the links match an originals-only
    #     matrix exactly;
    #   • each node's `related` list — its RELATED_K closest works, the single
    #     "three closest" shared by the publication pages and the network panel.
    def _work(p: dict) -> str:
        return p.get("translation_of") or p["slug"]

    vec_by_slug: dict[str, np.ndarray] = {
        pubs[i]["slug"]: cache[keys[j]] for j, i in enumerate(en_idx)
    }
    for j, i in enumerate(ne_orig_idx):
        vec_by_slug[pubs[i]["slug"]] = cache[ne_keys[j]]
    for p in pubs:  # a translation borrows its source's vector
        if p.get("translation_of"):
            vec_by_slug[p["slug"]] = vec_by_slug[p["translation_of"]]

    mat = np.vstack([vec_by_slug[p["slug"]] for p in pubs])  # normalized rows
    sim = mat @ mat.T
    np.fill_diagonal(sim, 0)
    similarity = [[round(float(s), 4) for s in row] for row in sim]

    # `related`: rank every other publication by cosine, but keep each *work*
    # once — a translation ties its source (shared vector), and the tie breaks
    # toward the original, so a translated work's own counterpart leads at ~1.00
    # without a work ever taking two slots.
    for d, node in enumerate(nodes):
        order = sorted(
            (i for i in range(len(pubs)) if i != d),
            key=lambda i: (-sim[d][i], 1 if pubs[i].get("translation_of") else 0, i),
        )
        ranked, seen = [], set()
        for i in order:
            w = _work(pubs[i])
            if w in seen:
                continue
            seen.add(w)
            ranked.append(i)
            if len(ranked) == RELATED_K:
                break
        node["related"] = [
            {
                "slug": pubs[i]["slug"],
                "title": pubs[i]["title"],
                "url": pubs[i]["url"],
                "lang": pubs[i]["lang"],
                "sim": round(float(sim[d][i]), 4),
            }
            for i in ranked
        ]

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

    # Auto clusters (connected components of the baked links, labeled by TF-IDF)
    # drive the homepage's research-cluster filter cards — see build_clusters().
    clusters = build_clusters(pubs, layout["links"])
    print(
        f"clusters (size ≥ {MIN_CLUSTER_SIZE}): "
        + ", ".join(f"{c['label']}·{c['size']}" for c in clusters),
        file=sys.stderr,
    )

    # `similarity` is intentionally not persisted: it is consumed only by
    # precompute_layout (above), and the browser reads each node's `related`
    # list — the single "three closest" source shared with the publication
    # pages — so shipping the full matrix would be dead weight. `clusters` is
    # persisted: it drives the homepage's auto filter cards.
    data = {
        "seed": layout.get("seed"),
        "nodes": nodes,
        "canvas": layout["canvas"],
        "links": layout["links"],
        "clusters": clusters,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False))
    print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size:,} bytes", file=sys.stderr)

    # Layer the card text (titles/filter labels) on top — a separate, model-free
    # step so it can also be re-run alone. See scripts/build-cards.py.
    subprocess.run([sys.executable, str(Path(__file__).parent / "build-cards.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
