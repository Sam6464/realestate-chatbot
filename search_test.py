import json, sys
import numpy as np
from fastembed import TextEmbedding

chunks = json.load(open("index/chunks.json", encoding="utf-8"))
vectors = np.load("index/vectors.npy")
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

query = " ".join(sys.argv[1:])
q = np.array(list(model.query_embed([query]))[0], dtype="float32")
scores = vectors @ q / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q))

for i in np.argsort(-scores)[:4]:
    c = chunks[i]
    print(f"\n[{scores[i]:.3f}] {c['source']} - {c['url']}")
    print(c["text"][:300].replace("\n", " "))