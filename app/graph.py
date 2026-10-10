import posixpath
import networkx as nx

ML_LIBS = {"torch", "tensorflow", "keras", "sklearn", "transformers", "jax", "xgboost", "lightgbm"}

def _safe(text:str)->str:
    return text.replace('"',"'").replace("<","#lt;").replace(">", "#gt;")

def build_import_graph(infos,resolved):
    G=nx.DiGraph()
    G.add_nodes_from(infos)
    for src,deps in resolved.items():
        for dst in deps:
            G.add_edge(src, dst)
    return G

def to_mermaid(G,ranks,max_nodes=40,highlight=None,only=None):
    nodes=list(only) if only else sorted(G.nodes, key=lambda n: -ranks.get(n,0))[:max_nodes]
    ids={n:f"n{i}" for i, n in enumerate(nodes)}
    groups={}
    for n in nodes:
        groups.setdefault(n.split("/")[0] if "/" in n else ".",[]).append(n)
    lines=["flowchart LR"]
    for gi, (g,members) in enumerate(sorted(groups.items())):
        lines.append(f' subgraph g{gi}["{_safe(g)}"]')
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

