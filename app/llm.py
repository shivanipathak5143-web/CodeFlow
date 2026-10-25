import hashlib
import logging
import time

import httpx

from . import config

log = logging.getLogger("uvicorn.error")

SYSTEM = ("You are a senior engineer explaining a codebase to a student. "
          "Be concise and concrete, and only state what the code shows.")
CHUNK = 4000          # characters per request (keeps requests small for free-tier limits)
MAX_CHUNKS = 4


class LLMError(RuntimeError):
    """Raised with a human-readable reason (includes the provider's own error message)."""


def _model():
    if config.LLM_PROVIDER == "anthropic":
        return config.ANTHROPIC_MODEL
    if config.LLM_PROVIDER == "openai":
        return config.OPENAI_MODEL
    return config.OLLAMA_MODEL


def _post(url, headers=None, json=None, timeout=120, retries=3):
    for attempt in range(retries + 1):
        try:
            r = httpx.post(url, headers=headers, json=json, timeout=timeout)
        except httpx.HTTPError as e:
            raise LLMError(f"Could not reach {url}: {e}") from e
        if r.status_code == 429 and attempt < retries:
            try:
                wait = float(r.headers.get("retry-after") or 0)
            except ValueError:
                wait = 0
            wait = min(wait or 15 * (attempt + 1), 60)
            log.warning("LLM rate limit hit, waiting %.0fs (attempt %d)", wait, attempt + 1)
            time.sleep(wait)
            continue
        if r.status_code >= 400:
            msg = f"{r.status_code} from {url.split('/')[2]}: {r.text[:300]}"
            log.warning("LLM error: %s", msg)
            raise LLMError(msg)
        return r


def _call(prompt: str) -> str:
    if config.LLM_PROVIDER == "openai":
        if not config.OPENAI_API_KEY and "localhost" not in config.OPENAI_BASE_URL:
            raise LLMError("OPENAI_API_KEY is empty. Create a .env file with your key "
                           "and restart the server (run: python -m app.check_llm).")
        headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"} if config.OPENAI_API_KEY else {}
        r = _post(f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions", headers=headers,
                  json={"model": config.OPENAI_MODEL, "max_tokens": 1500,
                        "messages": [{"role": "system", "content": SYSTEM},
                                     {"role": "user", "content": prompt}]},
                  timeout=300)
        text = (r.json()["choices"][0]["message"].get("content") or "").strip()
        if not text:
            raise LLMError("The model returned an empty answer (reasoning models can use up the "
                           "token limit while thinking). Try a different OPENAI_MODEL.")
        return text
    if config.LLM_PROVIDER == "anthropic":
        r = _post("https://api.anthropic.com/v1/messages",
                  headers={"x-api-key": config.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                           "content-type": "application/json"},
                  json={"model": config.ANTHROPIC_MODEL, "max_tokens": 700, "system": SYSTEM,
                        "messages": [{"role": "user", "content": prompt}]})
        return r.json()["content"][0]["text"]
    r = _post(f"{config.OLLAMA_URL}/api/chat",
              json={"model": config.OLLAMA_MODEL, "stream": False,
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": prompt}]},
              timeout=300)
    return r.json()["message"]["content"]


def complete(prompt: str) -> str:
    key = hashlib.sha256(f"{config.LLM_PROVIDER}|{_model()}|{prompt}".encode()).hexdigest()
    path = config.SUMMARY_DIR / f"{key}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    out = _call(prompt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(out, encoding="utf-8")
    return out


def summarize_file(path: str, src: str, facts: str) -> str:
    chunks = [src[i:i + CHUNK] for i in range(0, len(src), CHUNK)][:MAX_CHUNKS]
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
        f"README (truncated):\n{readme[:2000]}\n\nSummaries of the most important files:\n{body}\n\n"
        "Explain in one short paragraph what this project does, then list its main components "
        "and how they fit together.")