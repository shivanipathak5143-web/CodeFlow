import csv
import sys

from sklearn.metrics import accuracy_score, classification_report, f1_score


def main(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["true_role"].strip()]
    if len(rows) < 20:
        sys.exit(f"Only {len(rows)} labelled rows. Label at least ~50 for meaningful numbers.")
    truth = [r["true_role"].strip() for r in rows]
    print(f"{len(rows)} hand-labelled files\n")
    print(f"{'method':22s} {'accuracy':>9s} {'macro-F1':>9s}")
    for name, col in [("keyword rules", "keyword_rule"), ("trained model", "model_pred")]:
        pred = [r[col] for r in rows]
        print(f"{name:22s} {accuracy_score(truth, pred):9.3f} "
              f"{f1_score(truth, pred, average='macro', zero_division=0):9.3f}")
    print("\nPer-class report (trained model):")
    print(classification_report(truth, [r["model_pred"] for r in rows], zero_division=0))


if __name__ == "__main__":
    main(sys.argv[1])