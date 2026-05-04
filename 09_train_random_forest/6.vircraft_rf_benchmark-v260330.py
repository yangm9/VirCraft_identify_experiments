#!/usr/bin/env python3
import pandas as pd
import numpy as np
import joblib
import sys
from sklearn.metrics import matthews_corrcoef, confusion_matrix

def get_metrics(y_true, y_probs, threshold):
    # Standard metrics calculation function
    y_pred = (y_probs >= threshold).astype(int)
    if len(np.unique(y_true)) < 2: return [0]*7
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    mcc = matthews_corrcoef(y_true, y_pred)
    rec = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    pre = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    return [tp, fn, fp, tn, rec, pre, mcc * 100]

def run_benchmark():
    print('Loading Models and Baselines...')
    try:
        # 1. Load 0328 old version (Unified)
        #m_0328 = joblib.load('vircraft_rf_vs2-vb-dvf-gn_20260328_mdl.joblib')
        #t_0328 = joblib.load('vircraft_rf_vs2-vb-dvf-gn_20260328_thr.joblib')
        
        # 2. Load 0330 new version (Experts)
        m_short = joblib.load('vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib')
        m_std = joblib.load('vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib')
        t_0330 = joblib.load('vircraft_rf_vs2-vb-dvf-gn_thr_20260330.joblib')
        
        test_raw = pd.read_csv('test_cleaned_matrix.csv')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

    features = [c for c in test_raw.columns if c not in ['label', 'origin_gradient']]
    gradients = ['1-2k', '2-5k', '5-10k', '10-20k']
    
    # Set ratio 1:19
    r = 19
    print(f'\n' + f' Comprehensive Benchmark: v0328 vs v0330 vs Baselines (Ratio 1:{r}) '.center(125, '='))
    
    pos = test_raw[test_raw['label'] == 1]
    neg = test_raw[test_raw['label'] == 0]
    curr_test = pd.concat([pos, neg.sample(n=min(int(len(pos)*r), len(neg)), random_state=42)])
    
    res_rows = []
    for grad in gradients:
        g_df = curr_test[curr_test['origin_gradient'] == grad]
        y_true = g_df['label']
        if len(y_true) == 0: continue

        # --- A. VirCraft v0330 SEG (Latest segment expert routing logic) ---
        m_active = m_short if grad == '1-2k' else m_std
        p_seg = m_active.predict_proba(g_df[features])[:, 1]
        t_seg = t_0330.get(grad, 0.5)
        res_rows.append([grad, f'VirCraft_v0330_SEG(T={t_seg:.2f})'] + get_metrics(y_true, p_seg, t_seg))

        # --- B. VirCraft v0328 ---
        #p_0328 = m_0328.predict_proba(g_df[features])[:, 1]
        #t_old = t_0328.get(grad, 0.5)
        #res_rows.append([grad, f'VirCraft_v0328(T={t_old:.2f})'] + get_metrics(y_true, p_0328, t_old))

        # --- C. External Tools (Baseline) ---
        external_tools = [
            ('geNomad', 'gn_score', 0.7),
            ('DeepVirFinder', 'dvf_score', 0.9),
            ('VirSorter2', 'vs2_score', 0.5),
            ('VIBRANT', 'vb_isPhage', 0.5)
        ]
        for name, col, t_def in external_tools:
            if col in g_df.columns:
                res_rows.append([grad, f'{name}({t_def})'] + get_metrics(y_true, g_df[col], t_def))

    # Output table
    cols = ['Gradient', 'Tool/Model', 'TP', 'FN', 'FP', 'TN', 'Recall%', 'Prec%', 'MCC%']
    df_out = pd.DataFrame(res_rows, columns=cols)
    
    # Sorting logic: first by gradient, then by MCC descending
    print(df_out.sort_values(by=['Gradient', 'MCC%'], ascending=[True, False]).to_string(index=False, float_format=lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x))
    print('-' * 125)

if __name__ == '__main__':
    run_benchmark()
