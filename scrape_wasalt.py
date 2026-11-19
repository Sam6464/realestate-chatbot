import json, os, re, time, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment research project)"}
OUT = "data/raw_wasalt.json"
DROP_LINES = {"Call Now", "Call", "WhatsApp", "Map view", "Click to go to URL", "See more"}
PHONE = re.compile(r"(?:\+?966|0)\s?5[\d\s\-]{8,10}")

def scrape(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    # cut everything from the broker/licence block onwards (contact area + related listings)
    cut = text.find("FAL License No")
    if cut != -1:
        text = text[:cut]

    lines = [l for l in text.split("\n") if l not in DROP_LINES and "people viewed" not in l]
    text = "\n".join(lines)
    text = PHONE.sub("", text)

    kind = "For Sale" if "/property/sale/" in url else "For Rent"
    text = f"Wasalt property listing ({kind}). Prices are in Saudi Riyals (SAR).\n" + text
    return {"title": title, "text": text}

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    records = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
    done = {r["url"] for r in records}
    urls = [u.strip() for u in open("data/wasalt_sample_urls.txt", encoding="utf-8") if u.strip()]
    urls = [u for u in urls if u not in done]
    print("Pages to scrape:", len(urls), "| already done:", len(done))

    for i, url in enumerate(urls, 1):
        try:
            data = scrape(url)
            data.update({"url": url, "source": "Wasalt", "section": "property"})
            records.append(data)
            print(f"[{i}/{len(urls)}] OK   {len(data['text']):5d} chars  {url[-60:]}")
        except Exception as e:
            print(f"[{i}/{len(urls)}] FAIL {url[-60:]} -> {str(e)[:80]}")
        if i % 10 == 0:
            json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        time.sleep(2.5)

    json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Saved", len(records), "records to", OUT)