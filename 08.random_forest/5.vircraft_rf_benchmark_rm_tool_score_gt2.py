#!/usr/bin/env python3
import pandas as pd
import numpy as np
import joblib
import sys
from sklearn.metrics import matthews_corrcoef, confusion_matrix

def get_metrics_at_threshold(y_true, y_probs, threshold):
    """保持指标计算逻辑与 4.vircraft_...py 完全一致"""
    y_pred = (y_probs >= threshold).astype(int)
    if len(np.unique(y_true)) < 2: 
        return [0, 0, 0, 0, 0, 0, 0]
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    mcc = matthews_corrcoef(y_true, y_pred)
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    pre = tp / (tp + fp) if (tp + fp) > 0 else 0
    return [tp, fn, fp, tn, rec*100, pre*100, mcc*100]

def run_benchmark():
    print("Loading 0330 Expert Models and test data...")
    try:
        # 加载 0330 双专家模型
        m_short = joblib.load("vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib")
        m_std = joblib.load("vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib")
        t_map = joblib.load("vircraft_rf_vs2-vb-dvf-gn_thr_20260330.joblib")
        
        # 应用手动修正的 10-20k 鲁棒阈值
        t_map['10-20k'] = 0.70
        
        test_full = pd.read_csv('test_cleaned_matrix.csv')
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # --- 核心逻辑修正：直接加和原始分数 ---
    # 确保列名对应原始的连续型 Score (0.0 - 1.0)
    score_cols = ['vs2_score', 'vb_isPhage', 'dvf_score', 'gn_score']
    
    if all(col in test_full.columns for col in score_cols):
        # 实时计算原始分数总和 (Raw Score Summation)
        test_full['tool_score'] = test_full[score_cols].sum(axis=1)
        
        # 执行剔除：仅保留四个工具分数加起来都不到 2 的硬骨头
        initial_count = len(test_full)
        test_raw = test_full[test_full['tool_score'] < 2].copy()
        removed_count = initial_count - len(test_raw)
        
        print(f"\n[Filtering Report]")
        print(f" - Initial Samples: {initial_count}")
        print(f" - Ignored (tool_score >= 2.0): {removed_count}")
        print(f" - Remaining 'Hard' Samples: {len(test_raw)}")
    else:
        missing = [c for c in score_cols if c not in test_full.columns]
        print(f"Error: Missing score columns {missing}.")
        sys.exit(1)

    features = [c for c in test_raw.columns if c not in ['label', 'origin_gradient', 'tool_score']]
    gradients = ['1-2k', '2-5k', '5-10k', '10-20k']
    ratios = [1, 9, 19]
    
    for r in ratios:
        print(f"\n" + f" 0330 Expert Evaluation (Hard-Zone: tool_score sum < 2): Ratio 1:{r} ".center(115, "="))
        
        pos = test_raw[test_raw['label'] == 1]
        neg = test_raw[test_raw['label'] == 0]
        
        if len(pos) == 0:
            print(f"Warning: No positive samples found in Hard-Zone for ratio 1:{r}")
            continue
            
        # 采样保持不平衡分布
        curr_test = pd.concat([pos, neg.sample(n=min(int(len(pos)*r), len(neg)), random_state=42)])
        
        res_rows = []
        for grad in gradients:
            g_df = curr_test[curr_test['origin_gradient'] == grad]
            y_true = g_df['label']
            if len(y_true) == 0: continue
            
            # --- VirCraft 0330 路由预测 ---
            model_active = m_short if grad == '1-2k' else m_std
            c_probs = model_active.predict_proba(g_df[features])[:, 1]
            fixed_t = t_map.get(grad, 0.5)
            res_rows.append([grad, f"VirCraft_v0330(T={fixed_t:.2f})"] + get_metrics_at_threshold(y_true, c_probs, fixed_t))
            
            # --- 外部工具对比 (看看它们在自己都不自信的区间表现如何) ---
            external_tools = [
                ("geNomad", "gn_score", 0.7),
                ("DeepVirFinder", "dvf_score", 0.9),
                ("VirSorter2", "vs2_score", 0.5),
                ("VIBRANT", "vb_isPhage", 0.5)
            ]
            for name, col, t_def in external_tools:
                if col in g_df.columns:
                    res_rows.append([grad, f"{name}({t_def})"] + get_metrics_at_threshold(y_true, g_df[col], t_def))
            
        cols = ["Gradient", "Tool", "TP", "FN", "FP", "TN", "Recall%", "Prec%", "MCC%"]
        df_out = pd.DataFrame(res_rows, columns=cols)
        
        # 排序输出：看谁在绝境中表现最好
        print(df_out.sort_values(by=["Gradient", "MCC%"], ascending=[True, False]).to_string(index=False, float_format=lambda x: "{:.2f}".format(x) if isinstance(x, float) else x))
        print("-" * 120)

if __name__ == "__main__":
    run_benchmark()
