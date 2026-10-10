import ast
import posixpath
import re
from dataclasses import dataclass,field

HTTP_METHODS={"get","post","put","delete","patch","head","options"}
JS_EXTS={'.js','.jsx','.ts','.tsx'}

JS_IMPORT=re.compile(
    r"""(?:import\s+(?:[^'"]*?\s+from\s+)?|require\(\s*|import\(\s*)['"]([^'"]+)['"]""")
JS_FUNC = re.compile(
    r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>)")
JS_ROUTE = re.compile(r"""\b(?:app|router)\.(get|post|put|delete|patch)\(\s*['"]([^'"]+)['"]""")

@dataclass
class FileInfo:
    path:str
    lang:str
    loc:int=0
    doc:str=""
    imports:set=field(default_factory=set)
    functions:dict=field(default_factory=set)
    classes:list=field(default_factory=set)
    routes:list=field(default_factory=dict)

def parse_file(path:str,src:str)->FileInfo:
    return _parse_python(path,src) if path.endswith(".py") else _parse_js(path,src)

def _route_from_decorator(dec):
    if isinstance(dec,ast.Call) and isinstance(dec.func,ast.Attribute):
        if dec.func.attr in HTTP_METHODS and dec.args and isinstance(dec.args[0], ast.Constant):
            return f"{dec.func.attr.upper()} {dec.args[0].value}"
    return None

def _parse_python(path,src):
    info=FileInfo(path,"python",loc=src.count("\n")+1)
    try:
        tree=ast.parse(src)
    except (SyntaxError,ValueError):
        return info
    info.doc=(ast.get_docstring(tree) or "")[:300]
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

