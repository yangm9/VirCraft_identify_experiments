#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from itertools import combinations

SCORE_DIR = "1.score"


# =========================
# 分段
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
    else:
        return None


# =========================
# 指标
# =========================
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

    return TP, FN, FP, TN, *compute_metrics_from_counts(TP, FN, FP, TN)


# =========================
# 构建规则
# =========================
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

    # =========================
    # 单变量规则
    # =========================
    for name, func in base_rules.items():
        rules[name] = func

    score_cols = list(base_rules.keys())

    # =========================
    # 组合规则（子集）
    # =========================
    for k in range(2, 6):
        for combo in combinations(score_cols, k):

            combo_name = "+".join(combo)

            def make_func(cols):
                # 只输出 score
                return lambda x: x[list(cols)].sum(axis=1)

            rules[combo_name] = make_func(combo)

    # =========================
    # ⭐ FULL FEATURE RULE（你漏掉的关键）
    # =========================
    rules["ALL_vs2_vb_dvf_gn_add_rm"] = lambda x: (
        x[
            [
                "vs2_score",
                "vb_score",
                "dvf_score",
                "gn_score",
                "add_score",
                "rm_score"
            ]
        ].sum(axis=1)
    )

    return rules


# =========================
# 主程序
# =========================
def main():

    dfs = []

    # ===== 读取数据 =====
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

    if not dfs:
        print("❌ 未找到 test 数据")
        return

    df = pd.concat(dfs, ignore_index=True)

    df["Gradient"] = df["contig_length"].apply(assign_bin)
    df = df[df["Gradient"].notna()]

    rules = build_rules()

    results = []

    # =========================
    # 每个长度段独立优化
    # =========================
    for gradient in ["1-2k", "2-5k", "5-10k", "10-20k"]:

        sub = df[df["Gradient"] == gradient]

        pos_df = sub[sub["label"] == 1]
        neg_df = sub[sub["label"] == 0]

        if len(pos_df) == 0:
            continue

        n_neg_needed = len(pos_df) * 19
        neg_sampled = neg_df.sample(n=min(len(neg_df), n_neg_needed), random_state=42)

        sub_balanced = pd.concat([pos_df, neg_sampled], ignore_index=True)

        y_true = sub_balanced["label"].values

        # =========================
        # rule × threshold 搜索
        # =========================
        for rule_name, func in rules.items():

            scores = func(sub_balanced).values

            best_mcc = -1
            best_t = None
            best_pred = None

            max_score = np.max(scores)

            for t in np.arange(0.5, max_score + 0.5, 0.5):

                y_pred = (scores >= t).astype(int)

                TP, FN, FP, TN, recall, precision, mcc = compute_metrics(y_true, y_pred)

                if mcc > best_mcc:
                    best_mcc = mcc
                    best_t = t
                    best_pred = y_pred

            TP, FN, FP, TN, recall, precision, mcc = compute_metrics(y_true, best_pred)

            results.append([
                gradient,
                rule_name,
                best_t,
                TP, FN, FP, TN,
                recall, precision, mcc
            ])

    # =========================
    # dataframe
    # =========================
    result_df = pd.DataFrame(
        results,
        columns=[
            "Gradient", "Tool/Model", "Best_Threshold",
            "TP", "FN", "FP", "TN",
            "Recall%", "Prec%", "MCC%"
        ]
    )

    # =========================
    # 2–20k 汇总
    # =========================
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
            "",
            TP, FN, FP, TN,
            recall, precision, mcc
        ])

    combined_df = pd.DataFrame(combined_results, columns=result_df.columns)

    final_df = pd.concat([result_df, combined_df], ignore_index=True)

    # =========================
    # 排序
    # =========================
    order = ["1-2k", "2-5k", "5-10k", "10-20k", "2-20k"]
    final_df["Gradient"] = pd.Categorical(final_df["Gradient"], categories=order, ordered=True)

    final_df = final_df.sort_values(["Gradient", "MCC%"], ascending=[True, False])

    # =========================
    # 输出格式化
    # =========================
    final_df["Recall%"] = final_df["Recall%"].map(lambda x: f"{x:.2f}")
    final_df["Prec%"] = final_df["Prec%"].map(lambda x: f"{x:.2f}")
    final_df["MCC%"] = final_df["MCC%"].map(lambda x: f"{x:.2f}")

    print("\n==================== OPTIMIZED RESULT (WITH FULL RULE) ====================\n")
    print(final_df.to_string(index=False))

    final_df.to_csv(
        "optimized_rule_search_WITH_FULL_RULE.tsv",
        sep="\t",
        index=False
    )

    print("\n✅ 输出: optimized_rule_search_WITH_FULL_RULE.tsv")


if __name__ == "__main__":
    main()