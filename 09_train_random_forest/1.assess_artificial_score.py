#!/usr/bin/env python3
#used name 1.assess_artificial_score_63_conbination_2-20k.py

import os
import pandas as pd
import numpy as np
from itertools import combinations
import rules_contribution

SCORE_DIR = "1.score"

def assign_bin(length):
    if 1000 <= length < 2000:
        return "1-2k"
    elif 2000 <= length < 5000:
        return "2-5k"
    elif 5000 <= length < 10000:
        return "5-10k"
    elif 10000 <= length <= 20000:
        return "10-20k"
    else:
        return None

# ===== Confusion matrix evaluation metrics =====
def compute_metrics_from_counts(TP, FN, FP, TN):
    recall = TP / (TP + FN) * 100 if (TP + FN) > 0 else 0
    precision = TP / (TP + FP) * 100 if (TP + FP) > 0 else 0

    denom = np.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    mcc = (TP*TN - FP*FN) / denom if denom != 0 else 0

    if abs(mcc) > 1:
        mcc = np.sign(mcc)

    return recall, precision, mcc * 100


def compute_metrics(y_true, y_pred):
    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))

    recall, precision, mcc = compute_metrics_from_counts(TP, FN, FP, TN)

    return TP, FN, FP, TN, recall, precision, mcc


# ===== Make ruls =====
def build_rules():

    base_rules = {
        "vs2_score": lambda x: x["vs2_score"] >= 1,
        "vb_score": lambda x: x["vb_score"] >= 1,
        "dvf_score": lambda x: x["dvf_score"] >= 1,
        "gn_score": lambda x: x["gn_score"] >= 1,
        "add_score": lambda x: x["add_score"] >= 1,
        "rm_score": lambda x: x["rm_score"] >= -1,
    }

    rules = {}

    # ===== single rule =====
    for name, func in base_rules.items():
        rules[name] = func

    score_cols = list(base_rules.keys())

    # ===== mixed rule =====
    for k in range(2, 6):
        for combo in combinations(score_cols, k):

            combo_name = "+".join(combo)

            def make_func(cols):
                #return lambda x: (x[list(cols)].sum(axis=1) >= len(cols)).astype(int)
                return lambda x: (x[list(cols)].sum(axis=1) >= 0.6 * len(cols)).astype(int)
            rules[combo_name] = make_func(combo)

    rules["total_score"] = lambda x: x["total_score"] >= 3

    return rules


def main():

    dfs = []

    # ===== Read TEST data =====
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

    if len(dfs) == 0:
        print("Can not find test data")
        return

    df = pd.concat(dfs, ignore_index=True)

    df["Gradient"] = df["contig_length"].apply(assign_bin)
    df = df[df["Gradient"].notna()]

    # ===== Make rules =====
    rules = build_rules()

    results = []

    # Independently sample each length segment (1:19)
    for gradient in ["1-2k", "2-5k", "5-10k", "10-20k"]:

        sub = df[df["Gradient"] == gradient]

        pos_df = sub[sub["label"] == 1]
        neg_df = sub[sub["label"] == 0]

        n_pos = len(pos_df)

        if n_pos == 0:
            continue

        n_neg_needed = n_pos * 19

        if len(neg_df) >= n_neg_needed:
            neg_sampled = neg_df.sample(
                n=n_neg_needed,
                replace=False,
                random_state=42
            )
        else:
            neg_sampled = neg_df

        sub_balanced = pd.concat([pos_df, neg_sampled], ignore_index=True)

        y_true = sub_balanced["label"].values

        for rule_name, func in rules.items():

            y_pred = func(sub_balanced).astype(int).values

            TP, FN, FP, TN, recall, precision, mcc = compute_metrics(y_true, y_pred)

            results.append([
                gradient,
                rule_name,
                TP, FN, FP, TN,
                recall, precision, mcc
            ])

    # ===== Convert dataframe =====
    result_df = pd.DataFrame(
        results,
        columns=[
            "Gradient", "Tool/Model",
            "TP", "FN", "FP", "TN",
            "Recall%", "Prec%", "MCC%"
        ]
    )

    # =========================================================
    #  2–20k
    # =========================================================
    combined = result_df[
        result_df["Gradient"].isin(["2-5k", "5-10k", "10-20k"])
    ]

    combined_results = []

    for name, sub in combined.groupby("Tool/Model"):

        TP = sub["TP"].sum()
        FN = sub["FN"].sum()
        FP = sub["FP"].sum()
        TN = sub["TN"].sum()

        recall, precision, mcc = compute_metrics_from_counts(TP, FN, FP, TN)

        combined_results.append([
            "2-20k",
            name,
            TP, FN, FP, TN,
            recall, precision, mcc
        ])

    combined_df = pd.DataFrame(
        combined_results,
        columns=result_df.columns
    )

    final_df = pd.concat([result_df, combined_df], ignore_index=True)

    order = ["1-2k", "2-5k", "5-10k", "10-20k", "2-20k"]
    final_df["Gradient"] = pd.Categorical(final_df["Gradient"], categories=order, ordered=True)

    final_df = final_df.sort_values(["Gradient", "MCC%"], ascending=[True, False])

    final_df["Recall%"] = final_df["Recall%"].map(lambda x: f"{x:.2f}")
    final_df["Prec%"] = final_df["Prec%"].map(lambda x: f"{x:.2f}")
    final_df["MCC%"] = final_df["MCC%"].map(lambda x: f"{x:.2f}")

    print("\n============================= Benchmark (With 2–20k Combined) =============================\n")
    print(final_df.to_string(index=False))

    rules_contribution.calc_contribution(final_df)
    final_df.to_csv("artificial_score_combinations_with_2_20k.tsv", sep="\t", index=False)

    print("\nOutput: artificial_score_combinations_with_2_20k.tsv")


if __name__ == "__main__":
    main()
