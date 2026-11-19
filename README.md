# Real Estate Chatbot: Dar Global & Wasalt

 Live demo: https://realestate-chatbot-rhu7.onrender.com/

A RAG (retrieval-augmented generation) chatbot that answers questions about Dar Global projects and Wasalt property listings.

## How it works
1. **Scraping:** public pages from darglobal.co.uk (Playwright, because the site is JavaScript-rendered) and a sample of public listings from wasalt.sa (requests + BeautifulSoup). Scrapers run at a low request rate and follow robots.txt and Wasalt's llms.txt. Contact details are not collected.
2. **Indexing:** pages are cleaned and chunked, then embedded with `BAAI/bge-small-en-v1.5` (fastembed) into a NumPy vector index.
3. **Answering:** the question is embedded, the top matching chunks are retrieved, and a free OpenRouter model answers using only that context. Models fall back to alternatives if one is rate-limited.
4. **Serving:** FastAPI backend + a single-page chat UI, packaged with Docker.

## Run locally
```
pip install -r requirements.txt
# create .env with: OPENROUTER_API_KEY=your_key
uvicorn main:app --port 7860
```

## Run with Docker
```
docker build -t realestate-bot .
docker run --rm -p 7860:7860 --env-file .env realestate-bot
```

## Notes
- Data comes from public pages and may be out of date; prices and availability may have changed.
- Wasalt content is attributed as "Source: Wasalt.sa". This is a non-commercial technical assessment.
- The free hosting instance sleeps when idle, so the first load can take up to a minute.