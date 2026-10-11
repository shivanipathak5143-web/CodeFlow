import ast

MAX_NODES = 80


def _clean(text: str, n: int = 48) -> str:
    text = " ".join(text.split())
    if len(text) > n:
        text = text[: n - 1] + "…"
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")
