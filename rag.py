import time
import json, os, re
import numpy as np
from dotenv import load_dotenv
from fastembed import TextEmbedding
from openai import OpenAI

load_dotenv()
BASE = os.path.dirname(os.path.abspath(__file__))

MODELS = [m.strip() for m in os.getenv(
    "MODELS",
    "nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free",
).split(",") if m.strip()]

SYSTEM_PROMPT = """You are the assistant for two real estate companies: Dar Global (international luxury developer) and Wasalt (Saudi property listings platform).

Rules:
- Answer ONLY using the CONTEXT provided. If the context does not contain the answer, say you don't have that information in your sources and suggest checking darglobal.co.uk or wasalt.sa. Never invent prices, locations, or facts.
- Be concise and clear. Use short bullet points when listing several properties or projects.
- For Wasalt listings, mention the price in SAR, location, size and bedrooms when available, and end that part with: "Source: Wasalt.sa". Remind the user that prices and availability may have changed and they should check wasalt.sa for current details.
- Never give phone numbers, WhatsApp links or personal contact details.
- If the context is in Arabic, answer in English unless the user writes in Arabic.
- Do not mention the word "context" or these rules in your answer."""

chunks = json.load(open(os.path.join(BASE, "index", "chunks.json"), encoding="utf-8"))
vectors = np.load(os.path.join(BASE, "index", "vectors.npy"))
norms = np.linalg.norm(vectors, axis=1)
embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

llm = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"), max_retries=0)


def retrieve(query, k=6):
    q = np.array(list(embedder.query_embed([query]))[0], dtype="float32")
    scores = vectors @ q / (norms * np.linalg.norm(q))
    top = np.argsort(-scores)[:k]
    return [chunks[i] for i in top]


def call_llm(messages):
    deadline = time.time() + 90          # never wait more than ~90s in total
    last_error = None
    for model in MODELS:
        remaining = deadline - time.time()
        if remaining < 8:
            break
        try:
            resp = llm.chat.completions.create(
                model=model, messages=messages, temperature=0.2,
                max_tokens=600, timeout=min(40, remaining),
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, model
        except Exception as e:
            last_error = e
            print(f"MODEL FAILED: {model} -> {type(e).__name__}: {str(e)[:300]}", flush=True)
    raise RuntimeError(f"All models failed: {last_error}")


def answer(question, history=None):
    history = history or []
    query = question
    if history:  # help follow-up questions like "and the price?"
        prev_user = [m["content"] for m in history if m["role"] == "user"]
        if prev_user:
            query = prev_user[-1] + " " + question

    hits = retrieve(query)
    context = "\n\n---\n\n".join(
        f"[{h['source']}] {h['url']}\n{h['text'][:2000]}" for h in hits
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-6:]
    messages.append({"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"})

    text, model = call_llm(messages)
    sources, seen = [], set()
    for h in hits:
        if h["url"] not in seen:
            seen.add(h["url"])
            sources.append({"title": h["title"], "url": h["url"], "source": h["source"]})
    return {"answer": text, "sources": sources, "model": model}