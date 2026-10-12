from collections import defaultdict
import networkx as nx
from .flowchart import _clean

def build_call_graph(infos, resolved):
    name_index, CG = defaultdict(list), nx.DiGraph()
    for p, info in infos.items():
        for fn in info.functions:
            name_index[fn].append(p)
            CG.add_node(f"{p}::{fn}")
    for p, info in infos.items():
        visible = {p} | resolved.get(p, set())
        for fn, calls in info.functions.items():
            for c in calls:
                for q in name_index.get(c, []):
                    if q in visible and not (q == p and c == fn):
                        CG.add_edge(f"{p}::{fn}", f"{q}::{c}")
    return CG

def trace(CG, infos, target, start=None):
    """Shortest call path from an entry point (HTTP route, or `start` match) to `target`."""
    if start:
        entries = [n for n in CG if start.lower() in n.lower()]
    else:
        entries = [f"{p}::{fn}" for p, i in infos.items() for fn, _ in i.routes]
        if not entries:
            entries = sorted((n for n in CG if CG.in_degree(n) == 0 and CG.out_degree(n) > 0),
                             key=lambda n: -CG.out_degree(n))[:30]
    targets = {n for n in CG if target.lower() in n.lower()}
    best = None
    for e in entries:
        if e not in CG:
            continue
        paths = nx.single_source_shortest_path(CG, e)
        for t in targets:
            if t in paths and t != e and (best is None or len(paths[t]) < len(best)):
                best = paths[t]
    return best
