"""Import graph, PageRank, reading order, Mermaid output, ML pipeline view."""
import posixpath

import networkx as nx

ML_LIBS = {"torch", "tensorflow", "keras", "sklearn", "transformers", "jax", "xgboost", "lightgbm"}


def _safe(text: str) -> str:
    return text.replace('"', "'").replace("<", "#lt;").replace(">", "#gt;")


def build_import_graph(infos, resolved):
    G = nx.DiGraph()
    G.add_nodes_from(infos)
    for src, deps in resolved.items():
        for dst in deps:
            G.add_edge(src, dst)   # src imports dst
    return G


def to_mermaid(G, ranks, max_nodes=40, highlight=None, only=None):
    """Return (mermaid_text, id_to_path). Large repos: only the top-ranked files are drawn."""
    nodes = list(only) if only else sorted(G.nodes, key=lambda n: -ranks.get(n, 0))[:max_nodes]
    ids = {n: f"n{i}" for i, n in enumerate(nodes)}
    groups = {}
    for n in nodes:
        groups.setdefault(n.split("/")[0] if "/" in n else ".", []).append(n)
    lines = ["flowchart LR"]
    for gi, (g, members) in enumerate(sorted(groups.items())):
        lines.append(f'  subgraph g{gi}["{_safe(g)}"]')
        lines += [f'    {ids[n]}["{_safe(posixpath.basename(n))}"]' for n in members]
        lines.append("  end")
    lines += [f"  {ids[a]} --> {ids[b]}" for a, b in G.edges if a in ids and b in ids]
    lines += [f'  click {ids[n]} call showFile("{ids[n]}")' for n in nodes]
    if highlight:
        lines.append("  classDef changed fill:#ffb3b3,stroke:#d33,color:#000")
        lines.append("  classDef affected fill:#ffe0a3,stroke:#e69500,color:#000")
        for cls in ("changed", "affected"):
            members = [ids[n] for n in nodes if highlight.get(n) == cls]
            if members:
                lines.append(f"  class {','.join(members)} {cls}")
    return "\n".join(lines), {v: k for k, v in ids.items()}


def onboarding_order(G, ranks, n=5):
    """'Read these files in this order': entry point first, then what it depends on."""
    if not G.nodes:
        return []
    hint = ("main", "app", "run", "cli", "server", "index")
    entries = sorted(
        (x for x in G if G.in_degree(x) == 0 and G.out_degree(x) > 0),
        key=lambda x: (not any(h in posixpath.basename(x).lower() for h in hint), -G.out_degree(x)))
    order, reasons = [], {}
    if entries:
        start = entries[0]
        order.append(start)
        reasons[start] = f"Entry point: nothing imports it, it imports {G.out_degree(start)} files"
        queue = [start]
        while queue and len(order) < n:
            cur = queue.pop(0)
            for nxt in sorted(G.successors(cur), key=lambda x: -ranks.get(x, 0)):
                if nxt not in order and len(order) < n:
                    order.append(nxt)
                    reasons[nxt] = f"Imported by {G.in_degree(nxt)} files, used by {posixpath.basename(cur)}"
                    queue.append(nxt)
    for x in sorted(G, key=lambda x: -ranks.get(x, 0)):
        if len(order) >= n:
            break
        if x not in order:
            order.append(x)
            reasons[x] = f"Core module: imported by {G.in_degree(x)} files"
    return [{"path": p, "reason": reasons[p]} for p in order]


# ---------- ML repos ----------

STAGE_ORDER = ["data", "model", "training", "evaluation", "api"]
STAGE_TITLES = {"data": "Data", "model": "Model", "training": "Training",
                "evaluation": "Evaluation", "api": "Serving / API"}


def is_ml_repo(infos) -> bool:
    return any(i.split(".")[0] in ML_LIBS for info in infos.values() for i in info.imports)


def ml_pipeline_mermaid(roles, ranks, per_stage=6):
    """roles: path -> role string (from the trained classifier, or keyword fallback)."""
    stages = {s: [] for s in STAGE_ORDER}
    for path, role in roles.items():
        if role in stages:
            stages[role].append(path)
    lines, present = ["flowchart LR"], []
    for s in STAGE_ORDER:
        files = sorted(stages[s], key=lambda f: -ranks.get(f, 0))[:per_stage]
        if not files:
            continue
        present.append(s)
        lines.append(f'  subgraph stage_{s}["{STAGE_TITLES[s]}"]')
        lines += [f'    {s[:3]}{i}["{_safe(f)}"]' for i, f in enumerate(files)]
        lines.append("  end")
    lines += [f"  stage_{a} --> stage_{b}" for a, b in zip(present, present[1:])]
    return "\n".join(lines) if present else ""