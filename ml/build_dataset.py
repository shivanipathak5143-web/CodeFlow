import csv
import random
import sys
from collections import Counter
from pathlib import Path

from app import analysis, features, repo, roles


def main(repos_file, out, max_per_repo=300):
    urls = [ln.strip() for ln in open(repos_file) if ln.strip() and not ln.startswith("#")]
    rng, rows = random.Random(0), []
    for url in urls:
        try:
            root, commit = repo.clone(url)
            a = analysis.build(root, commit)
        except Exception as e:  
            print(f"skip {url}: {e}")
            continue
        paths = sorted(a.infos)
        rng.shuffle(paths)
        name = "/".join(repo.parse_url(url))
        for p in paths[:max_per_repo]:
            rows.append({"repo": name, "path": p, "label": roles.weak_label(p) or "",
                         "text": a.texts[p], **dict(zip(features.NUMERIC, a.nums[p]))})
        print(f"{name}: {min(len(paths), max_per_repo)} files sampled of {len(paths)}")
    if not rows:
        sys.exit("No data collected.")
    cols = ["repo", "path", "label", "text"] + features.NUMERIC
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    counts = Counter(r["label"] or "(unlabelled)" for r in rows)
    print(f"\nWrote {len(rows)} rows to {out}")
    for k, v in counts.most_common():
        print(f"  {k:14s} {v}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300)