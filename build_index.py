import json, os, re
from collections import Counter
import numpy as np
from fastembed import TextEmbedding

CHUNK_WORDS, OVERLAP = 220, 40

def load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []

def drop_boilerplate(records):
    """Remove short lines that appear on more than 25% of pages (menus, footers, etc.)."""
    counts = Counter()
    for r in records:
        counts.update(set(l.strip() for l in r["text"].split("\n")))
    limit = max(5, 0.25 * len(records))
    for r in records:
        keep = [l.strip() for l in r["text"].split("\n")
                if l.strip() and not (counts[l.strip()] > limit and len(l.strip()) < 200)]
        r["text"] = "\n".join(keep)
    return records

def chunk_words(text, size=CHUNK_WORDS, overlap=OVERLAP):
    words = text.split()
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        if i + size >= len(words):
            break
        i += size - overlap
    return out

chunks, seen = [], set()

# ---- Dar Global: chunk by words ----
dar = drop_boilerplate(load("data/raw_darglobal.json"))
for r in dar:
    if r["url"].rstrip("/").count("/") <= 3 and r["section"] in ("press", "insights", "blog"):
        continue  # skip the big list pages
    text = re.sub(r"\s+\n", "\n", r["text"]).strip()
    if len(text) < 200 or text[:300] in seen:
        continue
    seen.add(text[:300])
    for c in chunk_words(text):
        chunks.append({
            "text": f"{r['title']} (Dar Global, {r['section']})\n{c}",
            "source": "Dar Global", "url": r["url"], "title": r["title"],
        })

# ---- Wasalt: one chunk per listing ----
for r in load("data/raw_wasalt.json"):
    text = r["text"].strip()
    if len(text) < 200:
        continue
    text = " ".join(text.split()[:350])
    text = re.sub(r"\s*\n\s*", " | ", r["text"].strip())[:2500]
    chunks.append({
        "text": f"{r['title']} (Wasalt)\n{text}",
        "source": "Wasalt", "url": r["url"], "title": r["title"],
    })

print("Total chunks:", len(chunks))
print("  Dar Global:", sum(c["source"] == "Dar Global" for c in chunks))
print("  Wasalt:    ", sum(c["source"] == "Wasalt" for c in chunks))

print("Embedding (first run downloads the model, ~130 MB)...")
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
vectors = np.array(list(model.embed([c["text"] for c in chunks])), dtype="float32")

os.makedirs("index", exist_ok=True)
json.dump(chunks, open("index/chunks.json", "w", encoding="utf-8"), ensure_ascii=False)
np.save("index/vectors.npy", vectors)
print("Saved index/chunks.json and index/vectors.npy | vectors:", vectors.shape)