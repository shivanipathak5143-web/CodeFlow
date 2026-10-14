import keyword
import math
import re

NUMERIC = ["log_loc", "n_funcs", "n_classes", "n_routes", "has_main",
           "n_imports", "in_deg", "out_deg", "pagerank"]

STOP = set(keyword.kwlist) | {
    "the", "and", "for", "where", "what", "how", "does", "this", "that", "with",
    "from", "are", "not", "you", "can", "self", "cls", "var", "let", "const",
    "function", "return", "export", "default", "undefined", "null"}

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PIECES = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+")
MAIN_RE = re.compile(r"""__name__\s*==\s*['"]__main__['"]""")


def split_identifier(name: str):
    """getUserName / get_user_name -> ['get', 'user', 'name']"""
    return [p.lower() for p in PIECES.findall(name)]

def code_tokens(src:str,limit:int=3000):
    out=[]
    for ident in IDENT.findall(src):
        for w in split_identifier(ident):
            if len(w)>2 and w not in STOP:
                out.append(w)
            if len(out)>=limit:
                break
    return out

def import_tokens(info):
    toks=[]
    for raw in info.imports:
        parts=[p for p in raw.lower().strip(".").split(".") if p]
        if parts:
            toks.append("imp_"+parts[0])
            toks.append("imp_"+"_".join(parts[:2]))
    return toks

def build_text(src:str,info)->str:
    return " ".join(code_tokens(src) + import_tokens(info))

def numeric(info, G, ranks, has_main: bool):
    p = info.path
    return [math.log1p(info.loc), len(info.functions), len(info.classes), len(info.routes),
            int(has_main), len(info.imports), G.in_degree(p), G.out_degree(p), ranks.get(p, 0.0)]

