import os
from pathlib import Path


def _load_dotenv(path=".env"):
    """Tiny .env loader (no extra package). Real environment variables win over the file."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

CACHE_DIR = Path(os.getenv("CACHE_DIR", ".cache"))
REPOS_DIR = CACHE_DIR / "repos"
SUMMARY_DIR = CACHE_DIR / "summaries"

# Which AI backend to use: "openai" (Groq, Gemini, LM Studio...), "ollama" or "anthropic"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# --- Groq (default) ---------------------------------------------------------
# Put your key in a .env file (see below), NEVER in this file.
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")

# --- Ollama (local) ---------------------------------------------------------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

# --- Anthropic --------------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# --- Analysis limits --------------------------------------------------------
MAX_FILE_BYTES = 200_000
MAX_FILES = 3000
CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}
IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist",
    "build", ".next", ".idea", ".vscode", "site-packages", "vendor", "migrations",
}