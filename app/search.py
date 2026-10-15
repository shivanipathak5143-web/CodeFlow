from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from . import features

def get_index(a):
    if a.index is None:
        paths=sorted(a.infos)
        docs=[a.texts[p]+ " "+" ".join(features.code_tokens(p.replace("/"," ").replace("."," "))) for p in paths]
        vec=TfidfVectorizer(sublinear_tf=True, token_pattern=r"\S+")
        a.index=(vec,vec.fit_transform(docs),paths)
    return a.index

def query(a, text, k=8):
    toks = features.code_tokens(text)
    if not toks:
        return []
    vec, X, paths = get_index(a)
    sims = linear_kernel(vec.transform([" ".join(toks)]), X).ravel()
    out = []
    for i in sims.argsort()[::-1][:k]:
        if sims[i] <= 0:
            break
        info = a.infos[paths[i]]
        hits = [f for f in info.functions if set(features.split_identifier(f)) & set(toks)]
        out.append({"path": paths[i], "score": round(float(sims[i]), 3), "functions": hits[:5]})
    return out