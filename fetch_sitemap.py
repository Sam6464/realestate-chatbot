import sys
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment research project)"}

def get_urls(sitemap_url):
    r = requests.get(sitemap_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "xml")
    return [loc.get_text(strip=True) for loc in soup.find_all("loc")]

if __name__ == "__main__":
    sitemap_url = sys.argv[1]
    out_file = sys.argv[2]
    urls = get_urls(sitemap_url)
    urls = [u for u in urls if "?" not in u and "utm_" not in u]

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

    print("Total URLs:", len(urls))
    sections = Counter(
        urlparse(u).path.strip("/").split("/")[0] or "(home)" for u in urls
    )
    for name, count in sections.most_common():
        print(f"{count:4d}  /{name}")