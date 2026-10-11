import ast

MAX_NODES = 80


def _clean(text: str, n: int = 48) -> str:
    text = " ".join(text.split())
    if len(text) > n:
        text = text[: n - 1] + "…"
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")

class _Flow:
    def __init__(self):
        self.lines, self.edges, self.count, self.end = ["flowchart TD"], [], 0, None

    def node(self, parts, shape="box"):
        self.count += 1
        nid = f"f{self.count}"
        label = "<br/>".join(_clean(p) for p in parts)
        fmt = {"diamond": '{{"{}"}}', "stadium": '(["{}"])', "box": '["{}"]'}[shape]
        self.lines.append(f"  {nid}{fmt.format(label)}")
        return nid

    def link(self, prevs, nid):
        for p, lab in prevs:
            self.edges.append(f"  {p} -->|{lab}| {nid}" if lab else f"  {p} --> {nid}")

    def block(self, stmts, prevs):
        simple = []

        def flush(prevs):
            if not simple:
                return prevs
            parts = [ast.unparse(x) for x in simple[:4]] + (["..."] if len(simple) > 4 else [])
            simple.clear()
            nid = self.node(parts)
            self.link(prevs, nid)
            return [(nid, "")]

        for s in stmts:
            if self.count > MAX_NODES:
                return flush(prevs)
            if isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant):
                continue  # docstring / bare constant
            if isinstance(s, ast.If):
                prevs = flush(prevs)
                cond = self.node([f"if {ast.unparse(s.test)}"], "diamond")
                self.link(prevs, cond)
                yes = self.block(s.body, [(cond, "yes")])
                no = self.block(s.orelse, [(cond, "no")]) if s.orelse else [(cond, "no")]
                prevs = yes + no
            elif isinstance(s, (ast.For, ast.AsyncFor, ast.While)):
                prevs = flush(prevs)
                text = (f"for {ast.unparse(s.target)} in {ast.unparse(s.iter)}"
                        if not isinstance(s, ast.While) else f"while {ast.unparse(s.test)}")
                head = self.node([text], "diamond")
                self.link(prevs, head)
                self.link(self.block(s.body, [(head, "each")]), head)
                prevs = [(head, "done")]
            elif isinstance(s, (ast.Return, ast.Raise)):
                prevs = flush(prevs)
                nid = self.node([ast.unparse(s)])
                self.link(prevs, nid)
                self.link([(nid, "")], self.end)
                prevs = []
            elif isinstance(s, ast.Try):
                prevs = flush(prevs)
                t = self.node(["try"])
                self.link(prevs, t)
                body = self.block(s.body, [(t, "")])
                if s.orelse:
                    body = self.block(s.orelse, body)
                exits = list(body)
                for h in s.handlers:
                    hn = self.node([f"except {ast.unparse(h.type) if h.type else ''}"])
                    self.link([(t, "error")], hn)
                    exits += self.block(h.body, [(hn, "")])
                prevs = self.block(s.finalbody, exits) if s.finalbody else exits
            elif isinstance(s, (ast.With, ast.AsyncWith)):
                prevs = flush(prevs)
                w = self.node(["with " + ", ".join(ast.unparse(i) for i in s.items)])
                self.link(prevs, w)
                prevs = self.block(s.body, [(w, "")])
            else:
                simple.append(s)
        return flush(prevs)


def function_flowchart(src: str, func_name: str) -> str:
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func_name), None)
    if fn is None:
        raise ValueError(f"Function '{func_name}' not found (flowcharts support Python only)")
    f = _Flow()
    start = f.node([f"def {fn.name}({', '.join(a.arg for a in fn.args.args)})"], "stadium")
    f.end = f.node(["end"], "stadium")
    f.link(f.block(fn.body, [(start, "")]), f.end)
    return "\n".join(f.lines + f.edges)