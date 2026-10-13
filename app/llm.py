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
