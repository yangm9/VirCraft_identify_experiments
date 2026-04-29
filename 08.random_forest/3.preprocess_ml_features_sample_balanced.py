#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

def preprocess_matrix():
    datasets = ['train', 'val', 'test']
    
    # 31 key feature
    selected_features = [
        'contig_length', 'proviral_length', 'gene_count', 'viral_genes', 'host_genes', 'checkv_quality', 'completeness', 'contamination', 'kmer_freq',
        'vs2_region', 'vs2_max_score', 'vs2_hallmark', 'vs2_viral', 'vs2_cellular',
        'vb_lifestyle', 'vb_partial', 'vb_isPhage', 
        'dvf_v_score', 'dvf_pvalue',
        'gn_topology', 'gn_hallmarks', 'gn_marker_enrichment', 'gn_v_score', ##remove gn_fdr without value and gn_genes which is same as gene_count
        'is_provirus', 'host_rate', 'vs2_score', 'vb_score', 'dvf_score', 'gn_score', 'add_score', 'rm_score'
        #'score',
        #'tool_score'
    ]
    
    meta_cols = ["label", "origin_gradient"]

    print(f"Starting feature engineering transformation...")

    for ds in datasets:
        input_csv = f"2.build_ml_matrix/{ds}_feature_matrix.csv"
        if not os.path.exists(input_csv):
            continue
            
        print(f"Processing datasets: {input_csv}")
        df = pd.read_csv(input_csv)
        
        print(f"Number of original data rows: {len(df)}")

        # 1. provirus: Yes->1, No->0
        df["provirus"] = df["provirus"].map({"Yes": 1, "No": 0}).fillna(0)

        # 2. checkv_quality: 4,3,2,1,0
        quality_map = {
            "Complete": 4, "High-quality": 3, "Medium-quality": 2, "Low-quality": 1
        }
        df["checkv_quality"] = df["checkv_quality"].map(quality_map).fillna(0)

        # 3. vs2_region: full(1.0), partial(0.5), others(0.0)
        df["vs2_region"] = df["vs2_region"].astype(str)
        conditions = [
            (df["vs2_region"] == "full"),
            (df["vs2_region"].str.contains("partial", case=False, na=False))
        ]
        choices = [1.0, 0.5]
        df["vs2_region"] = np.select(conditions, choices, default=0.0)

        # 4. vb_lifestyle
        lifestyle_map = {"lysogenic": 1, "Undetermined": 0, "lytic": 2}
        df["vb_lifestyle"] = df["vb_lifestyle"].map(lifestyle_map).fillna(0)
        
        df["vb_partial"] = df["vb_partial"].astype(str).str.lower()
        conditions = [
            df["vb_partial"].str.contains("partial|fragment|true|1", na=False)
        ]
        choices = [1]
        df["vb_partial"] = np.select(conditions, choices, default=0)

        # 6. gn_topology
        df["gn_topology"] = (df["gn_topology"] == "Provirus").astype(int)

        # 7. Encoding and imputation
        for col in selected_features:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 8. Keep target features
        final_cols = selected_features + meta_cols
        cleaned_df = df[final_cols]

        # --- 新增：仅针对训练集进行平衡采样 ---
        if ds == 'train':
            print("Performing stratified downsampling for training set...")
            # 以 origin_gradient 分组，找到样本量最少的组（通常是 10-20k）
            min_size = cleaned_df.groupby("origin_gradient").size().min()
            print(f"Min group size detected: {min_size}")
            
            # 按梯度抽样并合并
            cleaned_df = cleaned_df.groupby("origin_gradient").apply(
                lambda x: x.sample(n=min_size, random_state=42)
            ).reset_index(drop=True)
        # ------------------------------------

        # output
        os.makedirs(f"3.preprocess_ml_features", exist_ok=True)
        output_name = f"3.preprocess_ml_features/{ds}_cleaned_matrix.csv"
        cleaned_df.to_csv(output_name, index=False)
        print(f"Preprocessing finished: {output_name} | Dimension: {cleaned_df.shape}")
        print("")

if __name__ == "__main__":
    preprocess_matrix()
    print("Preprocessing finished!")
