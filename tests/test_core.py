import networkx as nx

from app import dataflow, diff, flowchart, graph, parser

SRC = '''
def f(x):
    """doc"""
    if x > 1:
        return 1
    for i in range(3):
        print(i)
    try:
        risky()
    except ValueError:
        return -1
    return 0
'''


def test_flowchart_has_decision_loop_and_try():
    m = flowchart.function_flowchart(SRC, "f")
    assert m.startswith("flowchart TD")
    assert "if x #gt; 1" in m
    assert "for i in range(3)" in m
    assert "except ValueError" in m
    assert "|yes|" in m and "|each|" in m


def test_flowchart_unknown_function():
    try:
        flowchart.function_flowchart(SRC, "nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def make_infos():
    return {
        "pkg/a.py": parser.parse_file("pkg/a.py", "from .b import g\nimport pkg.c\n"),
        "pkg/b.py": parser.parse_file("pkg/b.py", "from .c import h\ndef g():\n    h()\n"),
        "pkg/c.py": parser.parse_file("pkg/c.py", "def h():\n    pass\n"),
    }


def test_import_resolution_relative_and_absolute():
    res = parser.resolve_all(make_infos())
    assert res["pkg/a.py"] == {"pkg/b.py", "pkg/c.py"}
    assert res["pkg/b.py"] == {"pkg/c.py"}


def test_pagerank_ranks_most_imported_file_first():
    infos = make_infos()
    G = graph.build_import_graph(infos, parser.resolve_all(infos))
    ranks = nx.pagerank(G)
    assert max(ranks, key=ranks.get) == "pkg/c.py"
    order = graph.onboarding_order(G, ranks, n=3)
    assert order[0]["path"] == "pkg/a.py"      # entry point first


def test_mermaid_contains_click_and_idmap():
    infos = make_infos()
    G = graph.build_import_graph(infos, parser.resolve_all(infos))
    mer, idmap = graph.to_mermaid(G, nx.pagerank(G))
    assert "click" in mer and set(idmap.values()) == set(infos)


def test_pr_impact_walks_reverse_dependencies():
    infos = make_infos()
    G = graph.build_import_graph(infos, parser.resolve_all(infos))
    changed, affected = diff.impact(G, ["pkg/c.py"])
    assert changed == ["pkg/c.py"] and affected == {"pkg/b.py": 1, "pkg/a.py": 1}


def test_changed_files_parses_diff():
    text = "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n"
    assert diff.changed_files(text) == ["x.py"]


def test_trace_route_to_database():
    infos = {
        "api.py": parser.parse_file("api.py", "from svc import get_user\n@app.get('/u')\ndef route():\n    return get_user()\n"),
        "svc.py": parser.parse_file("svc.py", "from db import query\ndef get_user():\n    return query()\n"),
        "db.py": parser.parse_file("db.py", "def query():\n    pass\n"),
    }
    res = parser.resolve_all(infos)
    CG = dataflow.build_call_graph(infos, res)
    path = dataflow.trace(CG, infos, "db")
    assert path == ["api.py::route", "svc.py::get_user", "db.py::query"]
    assert "GET /u" in dataflow.path_mermaid(path, infos)