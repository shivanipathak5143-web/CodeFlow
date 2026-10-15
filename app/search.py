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

