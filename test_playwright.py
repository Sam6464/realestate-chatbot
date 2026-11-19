import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)
    title = page.title()
    text = page.inner_text("body")
    browser.close()

print("Title:", title)
print("Characters of text:", len(text))
print("----- first 2000 characters -----")
print(text[:2000])