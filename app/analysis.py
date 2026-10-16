from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import networkx as nx
from . import dataflow,features,graph,parser,repo

@dataclass 
class Analysis:
    root: Path
    commit: str
    infos: dict
    resolved: dict
    G: nx.DiGraph
    ranks: dict
    CG: nx.DiGraph
    texts: dict          
    nums: dict           
    index: Optional[Any] = None

def build(root:Path,commit:str)->Analysis:
    infos,texts,has_main={},{},{}
    for rel in repo.list_code_files(root):
        src=(root/rel).read_text(errors='ignore')
        info=parser.parse_file(rel,src)
        infos[rel]=info
        texts[rel]=features.build_text(src,info)
        has_main[rel]=bool(features.MAIN_RE.search(src))
    resolved=parser.resolve_all(infos)
    G=graph.build_import_graph(infos,resolved)
    ranks=nx.pagerank(G) if G.number_of_nodes() else{}
    nums={p:features.numeric(infos[p],G,ranks,has_main[p]) for p in infos}
    return Analysis(root,commit,infos,resolved,G,ranks,dataflow.build_call_graph(infos,resolved),texts,nums)