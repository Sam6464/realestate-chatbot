import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rag import answer

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Real Estate Chatbot")


class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    q = req.question.strip()
    if not q:
        return {"answer": "Please type a question.", "sources": [], "model": ""}
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in req.history
        if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)
    ][-6:]
    try:
        return answer(q[:1000], history)
    except Exception:
        return {
            "answer": "Sorry, the AI models are busy right now. Please try again in a moment.",
            "sources": [],
            "model": "",
        }


app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "static", "index.html"))