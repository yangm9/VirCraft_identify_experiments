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
# metrics
# =========================
def compute_metrics(y_true, y_pred):

    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))

    recall = TP / (TP + FN + 1e-9)
    precision = TP / (TP + FP + 1e-9)

    denom = np.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    mcc = (TP*TN - FP*FN) / denom if denom != 0 else 0

    return TP, FN, FP, TN, recall*100, precision*100, mcc*100


def eval_rule(df, cols, threshold):
    score = df[cols].sum(axis=1)
    pred = (score >= threshold).astype(int).values
    return compute_metrics(df["label"].values, pred)


# =========================
# feature direction check
# =========================
def feature_direction(df, f):

    thresholds = np.arange(-2, 3.5, 0.5)

    best_pos = -1
    best_neg = -1

    for t in thresholds:

        pos_pred = (df[f] >= t).astype(int)
        neg_pred = (df[f] <= t).astype(int)

        _, _, _, _, _, _, mcc_pos = compute_metrics(df["label"], pos_pred)
        _, _, _, _, _, _, mcc_neg = compute_metrics(df["label"], neg_pred)

        best_pos = max(best_pos, mcc_pos)
        best_neg = max(best_neg, mcc_neg)

    return best_pos, best_neg


# =========================
# beam search
# =========================
def beam_search(df, beam=30):

    combos = []
    for k in range(1, len(FEATURES)+1):
        combos += list(combinations(FEATURES, k))

    thresholds = np.arange(0.5, len(FEATURES)+0.5, 0.5)

    candidates = []

    for c in combos:
        for t in thresholds:

            TP, FN, FP, TN, rec, prec, mcc = eval_rule(df, list(c), t)

            candidates.append([mcc, c, t, TP, FN, FP, TN, rec, prec])

    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[:beam]


# =========================
# explain feature importance
# =========================
def explain(df, best_combo, best_threshold):

    base_cols = list(best_combo)

    _, _, _, _, _, _, base_mcc = eval_rule(df, base_cols, best_threshold)

    importance = {}

    for f in base_cols:

        reduced = [x for x in base_cols if x != f]
        if len(reduced) == 0:
            continue

        _, _, _, _, _, _, mcc = eval_rule(df, reduced, best_threshold)

        drop = base_mcc - mcc

        pos, neg = feature_direction(df, f)

        importance[f] = {
            "impact_drop": drop,
            "best_pos": pos,
            "best_neg": neg,
            "direction": "negative" if neg > pos else "positive"
        }

    return importance


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

        df["label"] = 1 if "positive" in f else 0
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["bin"] = df["contig_length"].apply(assign_bin)
    df = df[df["bin"].notna()]

    results = []

    for b in ["1-2k", "2-5k", "5-10k", "10-20k"]:

        sub = df[df["bin"] == b]
        if len(sub) == 0:
            continue

        best = beam_search(sub)[0]

        mcc, combo, th, TP, FN, FP, TN, rec, prec = best

        importance = explain(sub, combo, th)

        results.append([
            b,
            "+".join(combo),
            th,
            TP, FN, FP, TN,
            rec, prec, mcc,
            str(importance)
        ])

    # =========================
    # dataframe output
    # =========================
    out = pd.DataFrame(results, columns=[
        "Bin",
        "Best_Combo",
        "Threshold",
        "TP", "FN", "FP", "TN",
        "Recall%", "Prec%", "MCC%",
        "Feature_Explain"
    ])

    print("\n==================== FINAL RESULT ====================\n")
    print(out.to_string(index=False))

    out.to_csv("final_rule_system_with_explain.tsv", sep="\t", index=False)

    print("\n✔ saved: final_rule_system_with_explain.tsv")


if __name__ == "__main__":
    main()