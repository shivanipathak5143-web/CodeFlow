import os
import posixpath
import re
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROLES = ["entry", "api", "model", "data", "training", "evaluation", "config", "util", "test"]
THRESHOLD = 0.45          # below this confidence a file is shown as "other"
MODEL_PATH = Path(os.getenv("ROLE_MODEL", "models/role_clf.joblib"))

_RULES = [
    ("training", ("train", "fit", "optim", "loss", "schedul")),
    ("evaluation", ("eval", "metric", "score", "benchmark", "validat")),
    ("config", ("config", "setting", "constant", "conf", "env")),
    ("api", ("api", "route", "view", "controller", "endpoint", "handler", "server", "serve",
             "predict", "infer")),
    ("data", ("data", "dataset", "loader", "preprocess", "feature", "etl", "transform")),
    ("model", ("model", "network", "layer", "arch", "backbone", "net")),
    ("util", ("util", "helper", "common", "misc", "tool")),
]
ENTRY_NAMES = {"main", "__main__", "run", "cli", "manage", "app", "wsgi", "asgi", "index"}


def weak_label(path: str):
    tokens = [t for t in re.split(r"[^a-z0-9]+", path.lower()) if t]
    if any(t.startswith("test") or t in ("spec", "conftest") for t in tokens):
        return "test"
    if posixpath.basename(path).rsplit(".", 1)[0].lower() in ENTRY_NAMES:
        return "entry"
    for role, keys in _RULES:
        if any(t.startswith(k) for t in tokens for k in keys):
            return role
    return None



def _matrix(b, texts, nums, fit):
    parts = []
    if b["use_text"]:
        parts.append(b["vec"].fit_transform(texts) if fit else b["vec"].transform(texts))
    if b["use_num"]:
        arr = np.asarray(nums, dtype=float)
        parts.append(csr_matrix(b["scaler"].fit_transform(arr) if fit else b["scaler"].transform(arr)))
    return hstack(parts).tocsr()


def fit(texts, nums, y, use_text=True, use_num=True, dummy=False):
    b = {"use_text": use_text, "use_num": use_num,
         "vec": TfidfVectorizer(sublinear_tf=True, min_df=2, max_features=6000, token_pattern=r"\S+"),
         "scaler": StandardScaler()}
    X = _matrix(b, texts, nums, fit=True)
    clf = (DummyClassifier(strategy="most_frequent") if dummy
           else LogisticRegression(max_iter=2000, class_weight="balanced", C=3.0))
    b["clf"] = clf.fit(X, y)
    return b


def predict_proba(b, texts, nums):
    return b["clf"].classes_, b["clf"].predict_proba(_matrix(b, texts, nums, fit=False))


def decide(classes, P, threshold=THRESHOLD):
    out = []
    for row in P:
        i = int(row.argmax())
        out.append((str(classes[i]) if row[i] >= threshold else "other", float(row[i])))
    return out


def top_terms(b, k=8):
    if not b["use_text"] or not hasattr(b["clf"], "coef_"):
        return {}
    names = np.array(b["vec"].get_feature_names_out())
    coef = b["clf"].coef_[:, :len(names)]      # drop the numeric-feature columns
    return {str(c): [str(names[j]) for j in coef[i].argsort()[::-1][:k]]
            for i, c in enumerate(b["clf"].classes_)}


@lru_cache(maxsize=2)
def _load(path, mtime):
    return joblib.load(path)


def load_model():
    return _load(str(MODEL_PATH), MODEL_PATH.stat().st_mtime) if MODEL_PATH.exists() else None


def predict_roles(a):
    paths = sorted(a.infos)
    bundle = load_model()
    out = {}
    if bundle:
        classes, P = predict_proba(bundle, [a.texts[p] for p in paths], [a.nums[p] for p in paths])
        for p, (role, conf) in zip(paths, decide(classes, P)):
            out[p] = {"role": role, "confidence": round(conf, 3), "source": "model",
                      "rule": weak_label(p) or "other"}
    else:
        for p in paths:
            rule = weak_label(p) or "other"
            out[p] = {"role": rule, "confidence": 1.0 if rule != "other" else 0.0,
                      "source": "keywords", "rule": rule}
    return out