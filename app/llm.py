import hashlib
import httpx
from . import config

SYSTEM = ("You are a senior engineer explaining a codebase to a student. "
          "Be concise and concrete, and only state what the code shows.")
CHUNK = 6000

def _model():
    if config.LLM_PROVIDER == "anthropic":
        return config.ANTHROPIC_MODEL
    if config.LLM_PROVIDER == "openai":
        return config.OPENAI_MODEL
    return config.OLLAMA_MODEL

def _call(prompt:str)->str:
    if config.LLM_PROVIDER=='openai':
        headers={"AUTHORIZATION": f"Bearer {config.OPENAI_API_KEY}"} if config.OPENAI_API_KEY else {}
        r = httpx.post(
            f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json={"model": config.OPENAI_MODEL, "max_tokens": 700,
                  "messages": [{"role": "system", "content": SYSTEM},
                               {"role": "user", "content": prompt}]},
            timeout=300)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    if config.LLM_PROVIDER == "anthropic":
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": config.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": config.ANTHROPIC_MODEL, "max_tokens": 700, "system": SYSTEM,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=120)
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    r = httpx.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={"model": config.OLLAMA_MODEL, "stream": False,
              "messages": [{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": prompt}]},
        timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"]

def complete(prompt: str) -> str:
    key = hashlib.sha256(f"{config.LLM_PROVIDER}|{_model()}|{prompt}".encode()).hexdigest()
    path = config.SUMMARY_DIR / f"{key}.txt"
    if path.exists():
        return path.read_text()
    out = _call(prompt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(out)
    return out

def summarize_file(path: str, src: str, facts: str) -> str:
    """Map-reduce for big files: summarise chunks, then combine."""
    chunks = [src[i:i + CHUNK] for i in range(0, len(src), CHUNK)][:6]
    ask = "In 3-5 sentences: what does this file do and what is its role in the project?"
    if len(chunks) <= 1:
        return complete(f"File: {path}\nStatic-analysis facts: {facts}\n\nCode:\n{src}\n\n{ask}")
    parts = [complete(f"File: {path} (part {i + 1}/{len(chunks)})\n\n{c}\n\nSummarise this part in 2-3 sentences.")
             for i, c in enumerate(chunks)]
    joined = "\n".join(f"- {p}" for p in parts)
    return complete(f"File: {path}\nFacts: {facts}\nPart summaries:\n{joined}\n\n{ask}")


def summarize_repo(readme: str, file_summaries: dict) -> str:
    body = "\n\n".join(f"{p}: {s}" for p, s in file_summaries.items())
    return complete(
        f"README (truncated):\n{readme[:3000]}\n\nSummaries of the most important files:\n{body}\n\n"
        "Explain in one short paragraph what this project does, then list its main components "
        "and how they fit together.")