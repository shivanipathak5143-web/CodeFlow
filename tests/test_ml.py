import networkx as nx
import numpy as np
from types import SimpleNamespace

from app import embed, features, graph, parser, roles, search


def test_weak_labels():
    assert roles.weak_label("tests/test_x.py") == "test"
    assert roles.weak_label("src/train.py") == "training"
    assert roles.weak_label("src/models/resnet.py") == "model"
    assert roles.weak_label("app/main.py") == "entry"
    assert roles.weak_label("src/zzz.py") is None


def test_tokens_split_identifiers_and_drop_keywords():
    toks = features.code_tokens("def getUserName(self):\n    return load_data_loader()")
    assert {"get", "user", "name", "load", "data", "loader"} <= set(toks)
    assert "self" not in toks and "def" not in toks


def test_classifier_learns_separable_roles():
    rng = np.random.default_rng(0)
    vocab = {"training": "optimizer loss epoch backward step",
             "data": "dataset dataloader batch transform csv",
             "config": "settings default value environ path"}
    texts, nums, y = [], [], []
    for role, words in vocab.items():
        w = words.split()
        for _ in range(40):
            texts.append(" ".join(rng.choice(w, 12)) + " imp_x")
            nums.append([3.0, 4, 1, 0, 0, 5, 1, 2, 0.01])
            y.append(role)
    b = roles.fit(texts, nums, np.array(y))
    classes, P = roles.predict_proba(b, ["optimizer loss epoch backward", "dataset batch csv"],
                                     [nums[0], nums[0]])
    assert [r for r, _ in roles.decide(classes, P, threshold=0.3)] == ["training", "data"]


def make_fake_analysis():
    """Two clearly separate groups of files (different vocabulary, internal imports)."""
    infos, texts, edges = {}, {}, []
    for grp, words in (("net", "tensor layer weights forward"), ("web", "request route response http")):
        for i in range(5):
            p = f"{grp}/m{i}.py"
            infos[p] = parser.parse_file(p, "def f():\n    pass\n")
            texts[p] = " ".join([words] * 3) + f" extra{i}"
        edges += [(f"{grp}/m{i}.py", f"{grp}/m{(i + 1) % 5}.py") for i in range(5)]
    G = nx.DiGraph()
    G.add_nodes_from(infos)
    G.add_edges_from(edges)
    return SimpleNamespace(infos=infos, texts=texts, G=G, ranks=nx.pagerank(G), index=None)


def test_module_clustering_recovers_groups():
    a = make_fake_analysis()
    res = embed.cluster_modules(a)
    assert res["k"] >= 2
    assert res["nmi"] is not None and res["nmi"] > 0.8
    mer, idmap = embed.clusters_mermaid(res, a.G, a.ranks)
    assert mer.startswith("flowchart LR") and idmap


def test_search_finds_relevant_file():
    a = make_fake_analysis()
    hits = search.query(a, "http request route")
    assert hits and hits[0]["path"].startswith("web/")
    assert search.query(a, "the is a") == []


def test_ml_pipeline_view_uses_roles():
    m = graph.ml_pipeline_mermaid({"a.py": "data", "b.py": "model", "c.py": "util"}, {})
    assert "stage_data --> stage_model" in m and "c.py" not in m