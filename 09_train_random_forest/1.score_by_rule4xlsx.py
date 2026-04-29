#!/usr/bin/env python3
import os
import pandas as pd

DATA_DIR = "0.data"
OUT_DIR = "1.score"

os.makedirs(OUT_DIR, exist_ok=True)

def compute_scores(df, methods='vs2-vb-dvf-gn'):

    method_score_map = {
        "vs2": "vs2_score",
        "vb": "vb_score",
        "dvf": "dvf_score",
        "gn": "gn_score"
    }

    for method in methods.split('-'):
        col = method_score_map.get(method)
        if col and col not in df.columns:
            df[col] = 0.0

    df["add_score"] = 0.0
    df["rm_score"] = 0.0

    # 🔥 1. geNomad（增强）
    if "gn" in methods and "gn_v_score" in df.columns:
        df.loc[df["gn_v_score"] >= 0.9, "gn_score"] = 3.5
        df.loc[(df["gn_v_score"] >= 0.8) & (df["gn_v_score"] < 0.9), "gn_score"] = 2.5
        df.loc[(df["gn_v_score"] >= 0.7) & (df["gn_v_score"] < 0.8), "gn_score"] = 1.5

    # 2. VIBRANT（保持）
    if "vb" in methods and "vb_isPhage" in df.columns:
        df.loc[df["vb_isPhage"] == 1, "vb_score"] = 1.5

    # 🔥 3. VirSorter2（增强）
    if "vs2" in methods and "vs2_max_score" in df.columns:
        df.loc[df["vs2_max_score"] >= 0.9, "vs2_score"] = 2.5
        df.loc[(df["vs2_max_score"] >= 0.8) & (df["vs2_max_score"] < 0.9), "vs2_score"] = 2.0
        df.loc[(df["vs2_max_score"] >= 0.7) & (df["vs2_max_score"] < 0.8), "vs2_score"] = 1.0

    # 🔥 4. DeepVirFinder（降权）
    if "dvf" in methods and "dvf_v_score" in df.columns and "dvf_pvalue" in df.columns:
        cond1 = (df["dvf_v_score"] >= 0.9) & (df["dvf_pvalue"] <= 0.05)
        cond2 = (df["dvf_v_score"] >= 0.7) & (df["dvf_pvalue"] <= 0.05)

        df.loc[cond1, "dvf_score"] = 1
        df.loc[~cond1 & cond2, "dvf_score"] = 0.5

    # 🔥 5. Addition（降权 + 更严格）
    gene_count = df["gene_count"].replace(0, 1)

    ratio_cond = (
        (df.get("viral_genes", 0) / gene_count >= 0.6) |
        (df.get("vs2_hallmark", 0) / gene_count >= 0.6) |
        (df.get("gn_hallmarks", 0) / gene_count >= 0.6)
    )

    cond_high = (
        (df.get("viral_genes", 0) >= 4) |
        (df.get("vs2_hallmark", 0) >= 4) |
        (df.get("gn_hallmarks", 0) >= 4)
    )

    cond_low = (
        (df.get("viral_genes", 0) >= 2) |
        (df.get("vs2_hallmark", 0) >= 2) |
        (df.get("gn_hallmarks", 0) >= 2)
    )

    df.loc[ratio_cond, "add_score"] += 1
    df.loc[cond_high, "add_score"] += 1
    df.loc[~cond_high & cond_low, "add_score"] += 0.5

    if "is_provirus" in df.columns:
        df.loc[df["is_provirus"] == 1, "add_score"] += 0.5

    # Removal（显著增强，特别针对长序列）
    viral_max = df.reindex(columns=["viral_genes", "vs2_hallmark", "gn_hallmarks"]).fillna(0).max(axis=1)
    host_count = df.get("host_genes", pd.Series(0, index=df.index))

    cond_rm1 = (
        (viral_max == 0) &
        (host_count >= 1)
    )
    
    cond_rm2 = (
        (3 * viral_max <= host_count) |
        ((viral_max < host_count) & (host_count > 5))
    ) & (df.get("is_provirus", 0) == 0)
    
    cond_rm3 = (
        (host_count > 50) &
        (df.get("is_provirus", 0) == 0)
    )
    
    cond_rm4 = (
        (df.get("contig_length", 0) > 50000) &
        (viral_max <= 1)
    )

    # 长序列额外惩罚

    df.loc[cond_rm1, "rm_score"] -= 1.5
    df.loc[cond_rm2, "rm_score"] -= 1.5
    df.loc[cond_rm3, "rm_score"] -= 3
    df.loc[cond_rm4, "rm_score"] -= 3

    # 关键增强：长序列额外 penalty
    long_seq = df.get("contig_length", 0) >= 10000
    ratio = host_count / (viral_max + 1)
    df.loc[long_seq & (host_count > viral_max) & (ratio > 1.5), 'rm_score'] -= 1

    # 7. total_score（长度感知阈值）
    score_cols = [
        method_score_map[m]
        for m in methods.split('-')
        if m in method_score_map and method_score_map[m] in df.columns
    ]

    score_cols += ["add_score", "rm_score"]

    df["total_score"] = df[score_cols].sum(axis=1)

    return df

def main():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".tsv")]

    for f in files:
        input_path = os.path.join(DATA_DIR, f)
        print(f"🚀 处理: {f}")

        df = pd.read_csv(input_path, sep="\t")

        df = compute_scores(df)

        # ===== 输出文件名 =====
        base_name = f.replace(".tsv", "")
        out_name = f"{base_name}.score.tsv"
        out_path = os.path.join(OUT_DIR, out_name)

        df.to_csv(out_path, sep="\t", index=False)

        print(f"  ✅ 输出: {out_name}")

    print("\n✨ 全部完成！")


if __name__ == "__main__":
    main()
