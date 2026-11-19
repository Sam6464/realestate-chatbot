from rag import answer

history = []
print("Real estate chatbot (type 'quit' to exit)")
while True:
    q = input("\nYou: ").strip()
    if not q:
        continue
    if q.lower() in ("quit", "exit"):
        break
    result = answer(q, history)
    print("\nBot:", result["answer"])
    print("\n[model:", result["model"], "]")
    for s in result["sources"][:4]:
        print("  -", s["url"])
    history += [{"role": "user", "content": q}, {"role": "assistant", "content": result["answer"]}]