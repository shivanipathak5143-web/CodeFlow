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