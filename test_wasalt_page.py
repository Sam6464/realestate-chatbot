import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment research project)"}
url = sys.argv[1]

r = requests.get(url, headers=HEADERS, timeout=30)
html = r.text
print("Status:", r.status_code)
print("HTML length:", len(html))
print("Has __NEXT_DATA__:", "__NEXT_DATA__" in html)
print("Has ld+json:", "application/ld+json" in html)

soup = BeautifulSoup(html, "lxml")
for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
    tag.decompose()
text = soup.get_text(separator="\n", strip=True)
print("Characters of text:", len(text))
print("----- first 1500 characters -----")
print(text[:1500])