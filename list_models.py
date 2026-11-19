import requests

data = requests.get("https://openrouter.ai/api/v1/models", timeout=30).json()["data"]
for m in data:
    if m["id"].endswith(":free"):
        print(m["id"], "| context:", m.get("context_length"))