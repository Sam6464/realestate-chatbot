import json, os, sys, time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

OUT = "data/raw_darglobal.json"
SKIP = ["thank-you", "success", "pay-online", "privacy-policy", "terms-conditions",
        "terms-of-uses", "careers", "internship", "landing-page", "landingpage",
        "new-home-page", "bookyourunit", "broker-contest-terms", "become-a-broker",
        "become-an-agent", "get-in-touch"]
CAPS = {"blog": 30, "press": 30}          # raise later if you have time
LATE = {"insights", "press", "blog"}      # scraped last

def section(url):
    return urlparse(url).path.strip("/").split("/")[0] or "home"

def build_url_list():
    urls = [u.strip() for u in open("data/darglobal_urls.txt", encoding="utf-8") if u.strip()]
    urls = [u for u in urls if not any(s in u.lower() for s in SKIP)]
    counts, keep = {}, []
    for u in urls:
        s = section(u)
        counts[s] = counts.get(s, 0) + 1
        if s in CAPS and counts[s] > CAPS[s]:
            continue
        keep.append(u)
    return sorted(keep, key=lambda u: section(u) in LATE)   # important pages first

def scrape(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)
    for _ in range(4):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(400)
    title = page.title()
    desc = page.evaluate(
        "() => { const m = document.querySelector('meta[name=description]'); return m ? m.content : ''; }")
    page.evaluate(
        "() => document.querySelectorAll('header, nav, footer, script, style, noscript').forEach(e => e.remove())")
    text = page.inner_text("body")
    return {"title": title, "description": desc, "text": text}

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    records = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
    done = {r["url"] for r in records}
    urls = [u for u in build_url_list() if u not in done]
    if limit:
        urls = urls[:limit]
    print("Pages to scrape:", len(urls), "| already done:", len(done))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(user_agent="Mozilla/5.0 (assessment research project)")
        context.route("**/*", lambda route: route.abort()
                      if route.request.resource_type in ("image", "media", "font")
                      else route.continue_())
        page = context.new_page()

        for i, url in enumerate(urls, 1):
            for attempt in (1, 2):
                try:
                    data = scrape(page, url)
                    data.update({"url": url, "source": "Dar Global", "section": section(url)})
                    records.append(data)
                    print(f"[{i}/{len(urls)}] OK   {len(data['text']):6d} chars  {url}")
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"[{i}/{len(urls)}] FAIL {url} -> {str(e)[:80]}")
            if i % 10 == 0:
                json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            time.sleep(1)

        browser.close()

    json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Saved", len(records), "records to", OUT)