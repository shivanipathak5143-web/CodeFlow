import csv
import random
import sys
from pathlib import Path
from app import features,roles

csv.field_size_limit(10**9)

def main(dataset, out, n=150):
    bundle = roles.load_model()
    if bundle is None:
        sys.exit("No trained model found. Run ml.train first.")
    with open(dataset, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    random.Random(0).shuffle(rows)
    rows = rows[:n]
    nums = [[float(r[c]) for c in features.NUMERIC] for r in rows]
    classes, P = roles.predict_proba(bundle, [r["text"] for r in rows], nums)
    preds = roles.decide(classes, P)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "path", "local_path", "model_pred", "confidence", "keyword_rule", "true_role"])
        for r, (role, conf) in zip(rows, preds):
            local = f".cache/repos/{r['repo'].replace('/', '__')}/{r['path']}"
            w.writerow([r["repo"], r["path"], local, role, round(conf, 3),
                        roles.weak_label(r["path"]) or "other", ""])
    print(f"Wrote {len(rows)} rows to {out}. Fill the true_role column, then run ml.eval_gold.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 150)