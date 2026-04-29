#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from itertools import combinations

SCORE_DIR = "1.score"

# =========================
# bin 划分
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
# metric
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


# =========================
# base features（不可改）
# =========================
BASE_FEATURES = [
    "vs2_score",
    "vb_score",
    "dvf_score",
    "gn_score",
    "add_score",
    "rm_score",
]


# =========================
# beam search rule search
# =========================
def evaluate_rule(df, cols, threshold):
    score = df[cols].sum(axis=1)
    y_pred = (score >= threshold).astype(int).values
    y_true = df["label"].values
    return compute_metrics(y_true, y_pred)


def beam_search(df, beam_width=20):
    """
    搜索：
    - feature subset
    - threshold (0.5 step)
    """

    features = BASE_FEATURES

    # 所有候选组合（含你漏掉的全量组合）
    all_combos = []
    for k in range(1, len(features) + 1):
        all_combos += list(combinations(features, k))

    thresholds = np.arange(0.5, len(features) + 0.5, 0.5)

    beam = []

    # init
    for combo in all_combos:
        for th in thresholds:
            TP, FN, FP, TN, rec, prec, mcc = evaluate_rule(df, list(combo), th)
            beam.append((mcc, combo, th, TP, FN, FP, TN, rec, prec))

    beam.sort(reverse=True, key=lambda x: x[0])
    beam = beam[:beam_width]

    # greedy refinement (beam search style)
    for _ in range(2):  # 轻量迭代
        new_beam = []

        for _, combo, th, *_ in beam:

            # 微调 threshold
            for delta in [-0.5, 0, 0.5]:
                new_th = max(0.5, th + delta)

                TP, FN, FP, TN, rec, prec, mcc = evaluate_rule(df, list(combo), new_th)
                new_beam.append((mcc, combo, new_th, TP, FN, FP, TN, rec, prec))

        new_beam.sort(reverse=True, key=lambda x: x[0])
        beam = new_beam[:beam_width]

    return beam[0]


# =========================
# main
# =========================
def main():

    dfs = []

    for f in os.listdir(SCORE_DIR):
        if not f.endswith(".tsv"):
            continue
        if "test" not in f:
            continue

        df = pd.read_csv(os.path.join(SCORE_DIR, f), sep="\t")

        if "positive" in f:
            df["label"] = 1
        elif "negative" in f:
            df["label"] = 0
        else:
            continue

        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["bin"] = df["contig_length"].apply(assign_bin)
    df = df[df["bin"].notna()]

    results = []

    for b in ["1-2k", "2-5k", "5-10k", "10-20k"]:

        sub = df[df["bin"] == b]
        if len(sub) == 0:
            continue

        best_mcc, best_combo, best_th, TP, FN, FP, TN, rec, prec = beam_search(sub)

        results.append([
            b,
            "+".join(best_combo),
            best_th,
            TP, FN, FP, TN,
            rec, prec, best_mcc
        ])

    out = pd.DataFrame(results, columns=[
        "Bin", "Best_Combo", "Threshold",
        "TP", "FN", "FP", "TN",
        "Recall%", "Prec%", "MCC%"
    ])

    print("\n================ BEST PER BIN (Beam Search) ================\n")
    print(out.to_string(index=False))

    out.to_csv("beam_search_best_rules.tsv", sep="\t", index=False)

    print("\n✔ saved: beam_search_best_rules.tsv")


if __name__ == "__main__":
    main()