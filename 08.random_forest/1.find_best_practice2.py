#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from itertools import combinations

SCORE_DIR = "1.score"

FEATURES = [
    "vs2_score",
    "vb_score",
    "dvf_score",
    "gn_score",
    "add_score",
    "rm_score",
]


# =========================
# bin
# =========================
def assign_bin(length):
    if 1000 <= length < 2000:
        return "1-2k"
    elif 2000 <= length < 5000:
        return "2-5k"
    elif 5000 <= length < 10000:
        return "5-10k"
    elif 10000 <= length <= 20000:
        return "10-20k"
    return None


# =========================
def compute_mcc(y_true, y_pred):
    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))

    denom = np.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    return (TP*TN - FP*FN) / denom if denom != 0 else 0


# =========================
# evaluate rule
# =========================
def eval_rule(df, cols, threshold):
    score = df[cols].sum(axis=1)
    pred = (score >= threshold).astype(int).values
    return compute_mcc(df["label"].values, pred)


# =========================
# feature direction test
# =========================
def feature_direction_test(df, feature):
    """
    判断 feature 是正向还是反向更有效
    """

    thresholds = np.arange(-2, 3.5, 0.5)

    best_pos = -1
    best_neg = -1

    for t in thresholds:

        # positive direction
        pred_pos = (df[feature] >= t).astype(int).values
        mcc_pos = compute_mcc(df["label"].values, pred_pos)
        best_pos = max(best_pos, mcc_pos)

        # negative direction (flip)
        pred_neg = (df[feature] <= t).astype(int).values
        mcc_neg = compute_mcc(df["label"].values, pred_neg)
        best_neg = max(best_neg, mcc_neg)

    return best_pos, best_neg


# =========================
# beam search
# =========================
def beam_search(df, beam=30):

    combos = []
    for k in range(1, len(FEATURES) + 1):
        combos += list(combinations(FEATURES, k))

    thresholds = np.arange(0.5, len(FEATURES) + 0.5, 0.5)

    candidates = []

    for c in combos:
        for t in thresholds:
            mcc = eval_rule(df, list(c), t)
            candidates.append((mcc, c, t))

    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[:beam]


# =========================
# explanation
# =========================
def explain(df, best_combo):

    report = {}

    base_mcc = eval_rule(df, list(best_combo[1]), best_combo[2])

    report["best_rule"] = {
        "combo": best_combo[1],
        "threshold": best_combo[2],
        "mcc": base_mcc
    }

    feature_importance = {}

    for f in FEATURES:

        if f not in best_combo[1]:
            continue

        reduced = [x for x in best_combo[1] if x != f]

        if len(reduced) == 0:
            continue

        mcc_without = eval_rule(df, reduced, best_combo[2])
        delta = base_mcc - mcc_without

        pos, neg = feature_direction_test(df, f)

        feature_importance[f] = {
            "importance_drop": delta,
            "best_positive": pos,
            "best_negative": neg,
            "direction": "negative" if neg > pos else "positive"
        }

    report["feature_analysis"] = feature_importance

    return report


# =========================
# main
# =========================
def main():

    dfs = []

    for f in os.listdir(SCORE_DIR):
        if "test" not in f:
            continue
        if not f.endswith(".tsv"):
            continue

        df = pd.read_csv(os.path.join(SCORE_DIR, f), sep="\t")

        if "positive" in f:
            df["label"] = 1
        else:
            df["label"] = 0

        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["bin"] = df["contig_length"].apply(assign_bin)
    df = df[df["bin"].notna()]

    results = {}

    for b in ["1-2k", "2-5k", "5-10k", "10-20k"]:

        sub = df[df["bin"] == b]
        if len(sub) == 0:
            continue

        best = beam_search(sub)[0]

        explanation = explain(sub, best)

        results[b] = explanation

    # =========================
    # print report
    # =========================
    for b, r in results.items():

        print("\n====================", b, "====================")

        print("BEST RULE:")
        print("  combo:", r["best_rule"]["combo"])
        print("  threshold:", r["best_rule"]["threshold"])
        print("  MCC:", r["best_rule"]["mcc"])

        print("\nFEATURE ANALYSIS:")

        for f, info in r["feature_analysis"].items():
            print(f"  {f}:")
            print("    importance_drop:", round(info["importance_drop"], 4))
            print("    direction:", info["direction"])
            print("    best_pos:", round(info["best_positive"], 4))
            print("    best_neg:", round(info["best_negative"], 4))


if __name__ == "__main__":
    main()