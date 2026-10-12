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
