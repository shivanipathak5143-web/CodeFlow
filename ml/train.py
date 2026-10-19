import csv
import sys
from collections import Counter
from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import accuracy_score,classification_report,f1_score
from sklearn.model_selection import GroupKFold
from app import features,roles

csv.field_size_limit(10**9)
MIN_PER_CLASS=10
VARIANTS={
    "majority class (dumb baseline)":dict(dummy=True,use_text=False),
    "graph/size numbers only":dict(use_text=False),
    "code tokens only":dict(use_num=False),
    "code token + numbers":{0,}
}

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["label"]]
    counts = Counter(r["label"] for r in rows)
    keep = {c for c, n in counts.items() if n >= MIN_PER_CLASS}
    dropped = sorted(set(counts) - keep)
    if dropped:
        print(f"Dropping rare classes (<{MIN_PER_CLASS} samples): {dropped}")
    rows = [r for r in rows if r["label"] in keep]
    texts = [r["text"] for r in rows]
    nums = [[float(r[c]) for c in features.NUMERIC] for r in rows]
    return texts, nums, np.array([r["label"] for r in rows]), np.array([r["repo"] for r in rows])

def cross_validate(texts, nums, y, groups):
    n_splits = min(5, len(set(groups)))
    if n_splits < 3:
        sys.exit("Need data from at least 3 repos for a repo-level split.")
    results, preds = {}, {}
    for name, kw in VARIANTS.items():
        f1s, accs, true_all, pred_all = [], [], [], []
        for tr, te in GroupKFold(n_splits=n_splits).split(texts, y, groups):
            b = roles.fit([texts[i] for i in tr], [nums[i] for i in tr], y[tr], **kw)
            classes, P = roles.predict_proba(b, [texts[i] for i in te], [nums[i] for i in te])
            pred = classes[P.argmax(axis=1)]
            f1s.append(f1_score(y[te], pred, average="macro", zero_division=0))
            accs.append(accuracy_score(y[te], pred))
            true_all += list(y[te])
            pred_all += list(pred)
        results[name] = (np.mean(f1s), np.std(f1s), np.mean(accs))
        preds[name] = (true_all, pred_all)
    return results, preds, n_splits


