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

