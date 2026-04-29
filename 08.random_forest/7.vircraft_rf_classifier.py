#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np
import joblib

def compute_scores(df):
    # ===== 初始化 =====
    df["vs2_score"] = 0.0
    df["vb_score"] = 0.0
    df["dvf_score"] = 0.0
    df["gn_score"] = 0.0
    df["add_score"] = 0.0
    df["rm_score"] = 0.0

    # ===== 1. geNomad =====
    df.loc[df["gn_v_score"] >= 0.9, "gn_score"] = 3
    df.loc[(df["gn_v_score"] >= 0.8) & (df["gn_v_score"] < 0.9), "gn_score"] = 2
    df.loc[(df["gn_v_score"] >= 0.7) & (df["gn_v_score"] < 0.8), "gn_score"] = 1

    # ===== 2. VIBRANT =====
    df.loc[df["vb_isPhage"] == 1, "vb_score"] = 1

    # ===== 3. VirSorter2 =====
    df.loc[df["vs2_max_score"] >= 0.9, "vs2_score"] = 2
    df.loc[(df["vs2_max_score"] >= 0.8) & (df["vs2_max_score"] < 0.9), "vs2_score"] = 1
    df.loc[(df["vs2_max_score"] >= 0.7) & (df["vs2_max_score"] < 0.8), "vs2_score"] = 0.5

    # ===== 4. DeepVirFinder =====
    cond1 = (df["dvf_v_score"] >= 0.9) & (df["dvf_pvalue"] <= 0.05)
    cond2 = (df["dvf_v_score"] >= 0.7) & (df["dvf_pvalue"] <= 0.05)

    df.loc[cond1, "dvf_score"] = 1
    df.loc[~cond1 & cond2, "dvf_score"] = 0.5

    # ===== 5. Addition =====
    gene_count = df["gene_count"].replace(0, 1)  # 防止除0

    ratio_cond = (
        (df["viral_genes"] / gene_count >= 0.5) |
        (df["vs2_hallmark"] / gene_count >= 0.5) |
        (df["gn_hallmarks"] / gene_count >= 0.5)
    )

    cond_high = (
        (df["viral_genes"] >= 3) |
        (df["vs2_hallmark"] >= 3) |
        (df["gn_hallmarks"] >= 3)
    )

    cond_low = (
        (df["viral_genes"] >= 1) |
        (df["vs2_hallmark"] >= 1) |
        (df["gn_hallmarks"] >= 1)
    )

    df.loc[ratio_cond, "add_score"] = 2
    df.loc[~ratio_cond & cond_high, "add_score"] = 1
    df.loc[~ratio_cond & ~cond_high & cond_low, "add_score"] = 0.5

    # provirus 加分
    df.loc[df["is_provirus"] == 1, "add_score"] += 1

    # ===== 6. Removal =====

    cond_rm1 = (
        (df["viral_genes"] == 0) &
        (df["vs2_hallmark"] == 0) &
        (df["gn_hallmarks"] == 0) &
        (df["host_genes"] >= 1)
    )

    cond_rm2 = (
        3 * df[["viral_genes", "vs2_hallmark", "gn_hallmarks"]].max(axis=1)
        <= df["host_genes"]
    ) & (df["is_provirus"] == 0)

    cond_rm3 = (df["host_genes"] > 50) & (df["is_provirus"] == 0)

    cond_rm4 = (df["contig_length"] > 50000) & (df["viral_genes"] <= 1)

    df.loc[cond_rm1, "rm_score"] -= 2.5
    df.loc[cond_rm2, "rm_score"] -= 2.5
    df.loc[cond_rm3, "rm_score"] -= 4
    df.loc[cond_rm4, "rm_score"] -= 4

    # ===== 计算最终总分 =====
    df["total_score"] = df[["vs2_score", "vb_score", "dvf_score", "gn_score", "add_score", "rm_score"]].sum(axis=1)
    
    return df

def run_vircraft_inference(input_tsv, output_tsv):
    # 1. 路径设置
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_lt2k_path = f'{base_dir}/vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib'
    model_gt2k_path = f'{base_dir}/vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib'
    thresholds_path = f'{base_dir}/vircraft_rf_vs2-vb-dvf-gn_thr_20260330.joblib'

    # 检查核心组件
    for p in [model_lt2k_path, model_gt2k_path, thresholds_path]:
        if not os.path.exists(p):
            print(f"Error: could not find {p}")
            sys.exit(1)

    print(f"Loading Dual-Expert Models (LT2K & GT2K)...")
    model_lt2k = joblib.load(model_lt2k_path)
    model_gt2k = joblib.load(model_gt2k_path)
    threshold_map = joblib.load(thresholds_path)
    
    # 2. 读取数据
    try:
        df_raw = pd.read_csv(input_tsv, sep='\t')
    except Exception as e:
        print(f"Failed to read the input file: {e}")
        sys.exit(1)
    
    df_raw = compute_scores(df_raw)
    df = df_raw.copy().fillna(0)
    
    # 3. 指定修正后的特征序列 (30 features, removed tool_score)
    selected_features = [
        'contig_length', 'proviral_length', 'gene_count', 'viral_genes', 
        'host_genes', 'checkv_quality', 'completeness', 'contamination', 'kmer_freq',
        'vs2_region', 'vs2_max_score', 'vs2_hallmark', 'vs2_viral', 'vs2_cellular',
        'vb_lifestyle', 'vb_partial', 'vb_isPhage', 
        'dvf_v_score', 'dvf_pvalue',
        'gn_topology', 'gn_hallmarks', 'gn_marker_enrichment', 'gn_v_score',
        'is_provirus', 'host_rate', 'vs2_score', 'vb_score', 'dvf_score', 'gn_score', 'add_score', 'rm_score'
    ]

    print(f"Aligning {len(selected_features)} features for {len(df)} sequences...")

    # --- 特征预处理逻辑 (与 2026-03-30 训练集保持严格一致) ---
    if "provirus" in df.columns:
        df["provirus"] = df["provirus"].map({"Yes": 1, "No": 0}).fillna(0)

    quality_map = {"Complete": 4, "High-quality": 3, "Medium-quality": 2, "Low-quality": 1}
    df["checkv_quality"] = df["checkv_quality"].map(quality_map).fillna(0)

    df["vs2_region"] = df["vs2_region"].astype(str)
    vs2_conds = [(df["vs2_region"] == "full"), (df["vs2_region"].str.contains("partial", case=False, na=False))]
    df["vs2_region"] = np.select(vs2_conds, [1.0, 0.5], default=0.0)

    lifestyle_map = {"lysogenic": 1, "Undetermined": 0, "lytic": 2}
    df["vb_lifestyle"] = df["vb_lifestyle"].map(lifestyle_map).fillna(0)

    df["vb_partial"] = df["vb_partial"].astype(str).str.lower()
    partial_conds = [df["vb_partial"].str.contains("partial|fragment|true|1", na=False)]
    df["vb_partial"] = np.select(partial_conds, [1], default=0)

    df["gn_topology"] = (df["gn_topology"] == "Provirus").astype(int)

    # 强制数值化并补零
    for col in selected_features:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. 执行双专家预测
    print(f"Inference in progress...")
    df_raw['vircraft_score'] = 0.0
    
    # 路由：短序列 (< 2000 bp)
    idx_lt2k = df[df['contig_length'] < 2000].index
    if not idx_lt2k.empty:
        df_raw.loc[idx_lt2k, 'vircraft_score'] = model_lt2k.predict_proba(df.loc[idx_lt2k, selected_features])[:, 1]
    
    # 路由：标准/长序列 (>= 2000 bp)
    idx_gt2k = df[df['contig_length'] >= 2000].index
    if not idx_gt2k.empty:
        df_raw.loc[idx_gt2k, 'vircraft_score'] = model_gt2k.predict_proba(df.loc[idx_gt2k, selected_features])[:, 1]

    # 5. 基于梯度阈值的最终判定
    def get_prediction(row):
        length = row['contig_length']
        if length < 2000: grad = '1-2k'
        elif length < 5000: grad = '2-5k'
        elif length < 10000: grad = '5-10k'
        else: grad = '10-20k'
        
        t = threshold_map.get(grad, 0.5) # 获取 2026-03-30 训练得出的最优 T
        return 1 if row['vircraft_score'] >= t else 0

    df_raw['is_virus'] = df_raw.apply(get_prediction, axis=1)

    # 6. 结果输出
    df_raw.to_csv(output_tsv, sep='\t', index=False)
    print(f"Success! Output saved to: {output_tsv}")
    print(f"Summary: {df_raw['is_virus'].sum()} potential viruses identified among {len(df_raw)} sequences.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python 6.vircraft_rf_classifier.py <input.tsv> <output.tsv>")
        sys.exit(1)
    else:
        run_vircraft_inference(sys.argv[1], sys.argv[2])
