import re
from socket import timeout
import subprocess
from pathlib import Path

from . import config

GITHUB_RE=re.compile(r"^https://github\.com/([^/]+)/([^/]+)(?:\.git)?$")

def parse_url(url: str):
    m = GITHUB_RE.match(url.strip())
    if not m:
        raise ValueError("Enter a URL like https://github.com/username/repo")
    return m.group(1), m.group(2)

def head_commit(path:Path)->str:
    out=subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],capture_output=True,text=True)
    return out.stdout.strip()

def clone(url:str):
    owner,name=parse_url(url)
    dest=config.REPOS_DIR/f"{owner}__{name}"
    config.REPOS_DIR.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        subprocess.run(["git","-C",str(dest),"pull","--ff--only"],capture_output=True,text=True,timeout=120)
    else:
        r=subprocess.run(["git","clone","--depth","1",f"https://github.com/{owner}/{name}.git",str(dest)],capture_output=True,text=True,timeout=300)
        if r.returncode!=0:
            raise RuntimeError(f"Failed to clone {url}: {r.stderr}")
    return dest,head_commit(dest)

def lits_code_files(root:Path):
    files=[]
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if any(part in config.IGNORE_DIRS for part in rel.parts):
            continue
        if p.is_file() and p.suffix in config.CODE_EXTS and p.stat().st_size <=config.MAX_FILE_BYTES:
            files.append(rel.as_posix())
            if len(files)>=config.MAX_FILES:
                break
    return files


