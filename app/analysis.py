from dataclasse import dataclass
from pathlib import Path
from typing import Any,Optional

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

