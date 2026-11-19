import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment research project)"}
url = sys.argv[1]

r = requests.get(url, headers=HEADERS, timeout=30)
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "lxml")
for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
    tag.decompose()
text = soup.get_text(separator="\n", strip=True)

print("Characters of text:", len(text))
print("----- first 1500 characters -----")
print(text[:1500])