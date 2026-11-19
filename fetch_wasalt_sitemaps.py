import gzip, re, requests
from collections import defaultdict
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment research project)"}
BASE = "https://cdn.wasalt.sa/sitemap/"
FILES = {
    "static": "static_sitemap_en_sa.xml.gz",
    "product": "product_sitemap_en_sa.xml.gz",
    "category": "category_sitemap_en_sa.xml.gz",
}

def fetch(name):
    r = requests.get(BASE + name, headers=HEADERS, timeout=60)
    r.raise_for_status()
    data = r.content
    try:
        data = gzip.decompress(data)
    except OSError:
        pass  # already decompressed
    return data.decode("utf-8", errors="ignore")

for kind, name in FILES.items():
    print("\n==========", kind, "==========")
    try:
        text = fetch(name)
    except Exception as e:
        print("FAILED:", e)
        continue
    urls = re.findall(r"<loc>(.*?)</loc>", text)
    urls = [u.strip() for u in urls]
    with open(f"data/wasalt_{kind}_urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls))
    print("Total URLs:", len(urls))

    groups = defaultdict(list)
    for u in urls:
        parts = [p for p in urlparse(u).path.split("/") if p]
        if parts and parts[0] in ("en", "ar"):
            parts = parts[1:]
        groups[parts[0] if parts else "(home)"].append(u)

    for section, items in sorted(groups.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"{len(items):6d}  /{section}")
        for sample in items[:2]:
            print("          e.g.", sample)