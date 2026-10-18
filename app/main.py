import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import analysis, dataflow, diff, embed, flowchart, graph, llm, repo, roles, search

app = FastAPI(title="RepoLens")
STATIC = Path(__file__).resolve().parent.parent / "static"
_cache: dict = {}


class RepoReq(BaseModel):
    url: str
    refresh: bool = False


class FileReq(BaseModel):
    url: str
    path: str


class SearchReq(BaseModel):
    url: str
    query: str


class FlowReq(BaseModel):
    url: str
    path: str
    function: str


class TraceReq(BaseModel):
    url: str
    target: str
    start: Optional[str] = None


class DiffReq(BaseModel):
    url: str
    pr_url: Optional[str] = None
    diff: Optional[str] = None


def get(url: str, refresh: bool = False) -> analysis.Analysis:
    if refresh or url not in _cache:
        try:
            root, commit = repo.clone(url)
        except (ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
            raise HTTPException(400, str(e))
        _cache[url] = analysis.build(root, commit)
    return _cache[url]


def file_info(a: analysis.Analysis, path: str):
    if path not in a.infos:          # also blocks path traversal
        raise HTTPException(404, "File not found in analysed set")
    return a.infos[path]


def facts_for(a, path):
    i = a.infos[path]
    return (f"functions={sorted(i.functions)[:30]}; classes={i.classes[:20]}; "
            f"imports_from_repo={sorted(a.resolved[path])}; routes={i.routes}")


@app.post("/api/analyze")
def analyze(req: RepoReq):
    a = get(req.url, req.refresh)
    mer, idmap = graph.to_mermaid(a.G, a.ranks)
    role_info = roles.predict_roles(a)
    ml = (graph.ml_pipeline_mermaid({p: v["role"] for p, v in role_info.items()}, a.ranks)
          if graph.is_ml_repo(a.infos) else "")
    return {
        "commit": a.commit[:8],
        "stats": {"files": len(a.infos), "edges": a.G.number_of_edges(),
                  "functions": a.CG.number_of_nodes(), "ml_repo": bool(ml),
                  "role_source": next(iter(role_info.values()), {}).get("source", "none")},
        "mermaid": mer, "idmap": idmap, "ml_mermaid": ml,
        "onboarding": graph.onboarding_order(a.G, a.ranks),
    }


@app.post("/api/roles")
def file_roles(req: RepoReq):
    a = get(req.url)
    info = roles.predict_roles(a)
    rows = [{"path": p, **v} for p, v in info.items()]
    rows.sort(key=lambda r: (r["role"], -r["confidence"]))
    return {"roles": rows, "source": rows[0]["source"] if rows else "none"}


@app.post("/api/modules")
def modules(req: RepoReq):
    a = get(req.url)
    result = embed.cluster_modules(a)
    mer, idmap = embed.clusters_mermaid(result, a.G, a.ranks)
    return {"k": result["k"], "silhouette": result["silhouette"], "nmi": result["nmi"],
            "ari": result["ari"], "clusters": [{"id": c["id"], "label": c["label"], "size": c["size"]}
                                               for c in result["clusters"]],
            "mermaid": mer, "idmap": idmap}


@app.post("/api/search")
def code_search(req: SearchReq):
    a = get(req.url)
    return {"results": search.query(a, req.query)}


@app.post("/api/file")
def file_details(req: FileReq):
    a = get(req.url)
    info = file_info(a, req.path)
    code = (a.root / req.path).read_text(errors="ignore")
    return {
        "path": req.path, "lang": info.lang, "loc": info.loc,
        "functions": sorted(info.functions), "classes": info.classes, "routes": info.routes,
        "imports": sorted(a.resolved[req.path]),
        "imported_by": sorted(a.G.predecessors(req.path)),
        "code": code[:20000],
    }


@app.post("/api/file_summary")
def file_summary(req: FileReq):
    a = get(req.url)
    file_info(a, req.path)
    code = (a.root / req.path).read_text(errors="ignore")
    try:
        return {"summary": llm.summarize_file(req.path, code, facts_for(a, req.path))}
    except Exception as e:
        raise HTTPException(502, f"LLM unavailable: {e}")


@app.post("/api/summary")
def repo_summary(req: RepoReq):
    a = get(req.url)
    readme = next((p for p in a.root.iterdir() if p.name.lower().startswith("readme")), None)
    text = readme.read_text(errors="ignore") if readme else ""
    try:
        top = [p for p in sorted(a.ranks, key=lambda x: -a.ranks[x])[:8]]
        sums = {p: llm.summarize_file(p, (a.root / p).read_text(errors="ignore"), facts_for(a, p))
                for p in top}
        return {"summary": llm.summarize_repo(text, sums)}
    except Exception as e:
        raise HTTPException(502, f"LLM unavailable: {e}")


@app.post("/api/flowchart")
def func_flowchart(req: FlowReq):
    a = get(req.url)
    file_info(a, req.path)
    src = (a.root / req.path).read_text(errors="ignore")
    try:
        return {"mermaid": flowchart.function_flowchart(src, req.function)}
    except (ValueError, SyntaxError) as e:
        raise HTTPException(400, str(e))


@app.post("/api/trace")
def trace(req: TraceReq):
    a = get(req.url)
    path = dataflow.trace(a.CG, a.infos, req.target, req.start)
    if not path:
        raise HTTPException(404, "No call path found. Try a different target keyword (e.g. 'db', 'save', 'model').")
    return {"path": path, "mermaid": dataflow.path_mermaid(path, a.infos)}


@app.post("/api/diff")
def pr_impact(req: DiffReq):
    a = get(req.url)
    try:
        text = req.diff or diff.diff_text_from_pr(req.pr_url or "")
    except Exception as e:
        raise HTTPException(400, str(e))
    changed, affected = diff.impact(a.G, diff.changed_files(text))
    if not changed:
        raise HTTPException(404, "None of the changed files are in the analysed code graph.")
    highlight = {**{c: "changed" for c in changed}, **{k: "affected" for k in affected}}
    only = list(highlight)[:60]
    mer, idmap = graph.to_mermaid(a.G, a.ranks, highlight=highlight, only=only)
    return {"changed": changed, "affected": affected, "mermaid": mer, "idmap": idmap}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")