import posixpath
import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix,identity
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score,normalized_mutual_info_score,silhouette_score
from sklearn.preprocessing import normalize
from .graph import _safe

def _svd(M,dim):
    k=min(dim,M.shape[0]-1,M.shape[1]-1)
    if k<1:
        return np.zeros((M.shape[0],1))
    return normalize(TruncatedSVD(k,random_state=0).fit_transform(M))

def embed(paths,texts,G,dim=16):
    vec=TfidfVectorizer(sublinear_tf=True, token_pattern=r"\S+", max_features=5000)
    T=vec.fit_transform([texts[p] for p in paths])
    Zc = _svd(T, dim)
    A = csr_matrix(nx.to_scipy_sparse_array(G.to_undirected(), nodelist=paths, format="csr"))
    A.data[:] = 1
    M = normalize(A + identity(len(paths), format="csr"), norm="l1")
    Zg = _svd(M @ M, max(4, dim // 2))
    return np.hstack([Zc, Zg]), vec, T

def _folder(p):
    return p.split("/")[0] if "/" in p else "."

def cluster_modules(a, max_k=10, seed=0):
    paths = sorted(a.infos)
    n = len(paths)
    if n < 6:
        return {"k": 1, "silhouette": None, "nmi": None, "ari": None,
                "clusters": [{"id": 0, "label": "all files", "files": paths, "size": n}],
                "assign": {p: 0 for p in paths}}
    Z, vec, T = embed(paths, a.texts, a.G)
    best = (-2.0, None)
    for k in range(2, min(max_k, n - 1) + 1):
        labels = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(Z)
        if len(set(labels)) < 2:
            continue
        s = silhouette_score(Z, labels)
        if s > best[0]:
            best = (s, labels)
    s, labels = best
    if labels is None:
        labels = np.zeros(n, dtype=int)
        s = None
    terms = np.array(vec.get_feature_names_out())
    clusters = []
    for cid in sorted(set(labels.tolist())):
        idx = [i for i, l in enumerate(labels) if l == cid]
        score = np.asarray(T[idx].mean(axis=0)).ravel()
        words = [t for t in terms[score.argsort()[::-1]] if not t.startswith("imp_")][:3]
        clusters.append({"id": int(cid), "label": ", ".join(words) or f"module {cid}",
                         "files": [paths[i] for i in idx], "size": len(idx)})
    folders = [_folder(p) for p in paths]
    agree = len(set(folders)) > 1
    return {"k": len(clusters), "silhouette": None if s is None else round(float(s), 3),
            "nmi": round(float(normalized_mutual_info_score(folders, labels)), 3) if agree else None,
            "ari": round(float(adjusted_rand_score(folders, labels)), 3) if agree else None,
            "clusters": clusters, "assign": {p: int(l) for p, l in zip(paths, labels)}}

def clusters_mermaid(result, G, ranks, per_cluster=8):
    ids, lines = {}, ["flowchart LR"]
    for c in result["clusters"]:
        lines.append(f'  subgraph c{c["id"]}["{_safe(c["label"])} ({c["size"]} files)"]')
        for f in sorted(c["files"], key=lambda f: -ranks.get(f, 0))[:per_cluster]:
            ids[f] = f"n{len(ids)}"
            lines.append(f'    {ids[f]}["{_safe(posixpath.basename(f))}"]')
        lines.append("  end")
    cross = {}
    for u, v in G.edges:
        cu, cv = result["assign"].get(u), result["assign"].get(v)
        if cu is not None and cv is not None and cu != cv:
            cross[(cu, cv)] = cross.get((cu, cv), 0) + 1
    lines += [f"  c{u} -->|{w}| c{v}" for (u, v), w in sorted(cross.items())]
    lines += [f'  click {i} call showFile("{i}")' for i in ids.values()]
    return "\n".join(lines), {v: k for k, v in ids.items()}