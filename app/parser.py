"""Static parsing: imports, functions, calls and HTTP routes. No LLM involved."""
import ast
import posixpath
import re
from dataclasses import dataclass, field

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "route"}
JS_EXTS = (".js", ".jsx", ".ts", ".tsx")

JS_IMPORT = re.compile(
    r"""(?:import\s+(?:[^'"]*?\s+from\s+)?|require\(\s*|import\(\s*)['"]([^'"]+)['"]""")
JS_FUNC = re.compile(
    r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>)")
JS_ROUTE = re.compile(r"""\b(?:app|router)\.(get|post|put|delete|patch)\(\s*['"]([^'"]+)['"]""")


@dataclass
class FileInfo:
    path: str
    lang: str
    loc: int = 0
    doc: str = ""
    imports: set = field(default_factory=set)
    functions: dict = field(default_factory=dict)   # name -> set of called names
    classes: list = field(default_factory=list)
    routes: list = field(default_factory=list)      # (function name, "GET /path")


def parse_file(path: str, src: str) -> FileInfo:
    return _parse_python(path, src) if path.endswith(".py") else _parse_js(path, src)


def _route_from_decorator(dec):
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
        if dec.func.attr in HTTP_METHODS and dec.args and isinstance(dec.args[0], ast.Constant):
            return f"{dec.func.attr.upper()} {dec.args[0].value}"
    return None


def _parse_python(path, src):
    info = FileInfo(path, "python", loc=src.count("\n") + 1)
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return info
    info.doc = (ast.get_docstring(tree) or "")[:300]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            info.imports.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            if node.module:
                info.imports.add(prefix)
            sep = "" if (not prefix or prefix.endswith(".")) else "."
            info.imports.update(prefix + sep + a.name for a in node.names)
        elif isinstance(node, ast.ClassDef):
            info.classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            calls = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    if isinstance(sub.func, ast.Name):
                        calls.add(sub.func.id)
                    elif isinstance(sub.func, ast.Attribute):
                        calls.add(sub.func.attr)
            info.functions.setdefault(node.name, set()).update(calls)
            for dec in node.decorator_list:
                route = _route_from_decorator(dec)
                if route:
                    info.routes.append((node.name, route))
    return info


def _parse_js(path, src):
    info = FileInfo(path, "javascript", loc=src.count("\n") + 1)
    info.imports.update(JS_IMPORT.findall(src))
    for m in JS_FUNC.finditer(src):
        info.functions.setdefault(m.group(1) or m.group(2), set())
    for method, route in JS_ROUTE.findall(src):
        info.routes.append(("handler", f"{method.upper()} {route}"))
    return info


# ---------- import resolution ----------

def _module_parts(path):
    parts = path[:-3].split("/")
    return parts[:-1] if parts[-1] == "__init__" else parts


def _resolve_py(path, raw, paths, by_module):
    if raw.startswith("."):
        level = len(raw) - len(raw.lstrip("."))
        base = posixpath.dirname(path)
        for _ in range(level - 1):
            base = posixpath.dirname(base)
        rest = raw.lstrip(".").replace(".", "/")
        stem = posixpath.normpath(posixpath.join(base, rest)) if rest else base
        for cand in (stem + ".py", stem + "/__init__.py"):
            if cand in paths:
                return cand
        return None
    return by_module.get(raw)


def _resolve_js(path, raw, paths):
    if not raw.startswith("."):
        return None  # external package
    stem = posixpath.normpath(posixpath.join(posixpath.dirname(path), raw))
    cands = [stem] + [stem + e for e in JS_EXTS] + [stem + "/index" + e for e in JS_EXTS]
    return next((c for c in cands if c in paths), None)


def resolve_all(infos: dict) -> dict:
    """Map every file to the set of repo files it imports."""
    paths = set(infos)
    by_module = {}
    for p in sorted(infos, key=lambda x: x.count("/")):
        if p.endswith(".py"):
            parts = _module_parts(p)
            for i in range(len(parts)):
                by_module.setdefault(".".join(parts[i:]), p)
    out = {}
    for p, info in infos.items():
        deps = set()
        for raw in info.imports:
            t = (_resolve_py(p, raw, paths, by_module) if info.lang == "python"
                 else _resolve_js(p, raw, paths))
            if t and t != p:
                deps.add(t)
        out[p] = deps
    return out