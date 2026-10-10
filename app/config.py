import os
from pathlib import Path

def load_dotenv(path='.env'):
    p=Path(path)
    if not p.exists():
        return
    for line in p.read_text().split():
        line=line.strip()
        if not line or line.startswith('#'):
            continue
        key,value=line.split('=',1)
        os.environ.setdefault(key.strip(),value.strip().strip('"').strip("'"))
load_dotenv()
CACHE_DIR=Path(os.getenv("CACHE_DIR",".cache"))
REPOS_DIR=CACHE_DIR/"repos"
SUMMARY_DIR=CACHE_DIR/"summaries"

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

MAX_FILE_BYTES = 200_000
MAX_FILES = 3000
CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}
IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist",
    "build", ".next", ".idea", ".vscode", "site-packages", "vendor", "migrations",
}
