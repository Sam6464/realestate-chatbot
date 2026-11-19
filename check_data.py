import json
from collections import Counter

recs = json.load(open("data/raw_darglobal.json", encoding="utf-8"))
print(Counter(r["section"] for r in recs).most_common(12))
print()
for r in recs:
    if r["section"] in ("projects", "aida-360", "rayana", "amaya", "the-astera", "marea", "w-residences"):
        print(f"{len(r['text']):6d} chars  {r['url']}")