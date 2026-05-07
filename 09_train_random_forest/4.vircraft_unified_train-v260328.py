#!/usr/bin/env python3

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, PredefinedSplit
from sklearn.metrics import matthews_corrcoef, make_scorer

mcc_scorer = make_scorer(matthews_corrcoef)

def find_best_t(y_true, y_probs):
    thresholds = np.linspace(0.1, 0.9, 81)
    best_mcc, best_t = -1, 0.5
    for t in thresholds:
        mcc = matthews_corrcoef(y_true, (y_probs >= t).astype(int))
        if mcc > best_mcc:
            best_mcc, best_t = mcc, t
    return best_t

def optimize_with_val(train_df, val_df, features, tag, is_short=True):
    print(f'\n' + f' Optimizing {tag} (Training + Validation) '.center(60, '='))
    
    # --- Core change: Merge data and create predefined splits ---
    #  GridSearchCV trains on the train set and evaluates on the validation set to select the best parameters
    X = pd.concat([train_df[features], val_df[features]])
    y = pd.concat([train_df['label'], val_df['label']])
    
    # test_fold array: -1 indicates traning dataset，0 refers to validation dataset
    test_fold = np.concatenate([
        np.full(len(train_df), -1),
        np.full(len(val_df), 0)
    ])
    ps = PredefinedSplit(test_fold)

    if is_short:
        param_grid = {
            'max_depth': [10, 15, 20],
            'min_samples_leaf': [5, 10, 20],
            'max_features': [0.2, 0.3, 0.4],
            'min_samples_split': [10, 20]
        }
    else:
        param_grid = {
            'max_depth': [20, 25, 30],
            'min_samples_leaf': [2, 5, 10],
            'max_features': [0.3, 0.4, 0.5],
            'min_samples_split': [10, 20]
        }

    rf = RandomForestClassifier(n_estimators=300, class_weight='balanced', n_jobs=-1, random_state=42)
    
    # 这里的 cv=ps 确保了参数选择是基于验证集表现的
    grid_search = GridSearchCV(rf, param_grid, scoring=mcc_scorer, cv=ps, verbose=1)
    grid_search.fit(X, y)
    
    print(f'Best parameters based on Validation Set: {grid_search.best_params_}')
    print(f'Best Val MCC: {grid_search.best_score_:.4f}')
    
    return grid_search.best_estimator_

def run_experiment():
    # 1. Load data
    train_df = pd.read_csv('3.preprocess_ml_features/train_cleaned_matrix.csv')
    val_df = pd.read_csv('3.preprocess_ml_features/val_cleaned_matrix.csv')
    features = [c for c in train_df.columns if c not in ['label', 'origin_gradient']]
    
    # 2. stratify
    t_short = train_df[train_df['origin_gradient'] == '1-2k']
    v_short = val_df[val_df['origin_gradient'] == '1-2k']
    
    t_std = train_df[train_df['origin_gradient'] != '1-2k']
    v_std = val_df[val_df['origin_gradient'] != '1-2k']
    
    # 3. Use the validation set to tune parameters
    model_short = optimize_with_val(t_short, v_short, features, 'Short: 1-2k', is_short=True)
    model_std = optimize_with_val(t_std, v_std, features, 'Standard: >2k', is_short=False)
    
    # 4. Re-confirm the optimal threshold for each gradient (fine-tuned on the validation set)
    print('\nRefining thresholds on validation set...')
    best_t_map = {}
    gradients = ['1-2k', '2-5k', '5-10k', '10-20k']
    
    for grad in gradients:
        v_sub = val_df[val_df['origin_gradient'] == grad]
        if len(v_sub) == 0: continue
        
        m_active = model_short if grad == '1-2k' else model_std
        v_probs = m_active.predict_proba(v_sub[features])[:, 1]
        
        best_t_map[grad] = find_best_t(v_sub['label'], v_probs)
        print(f'  - [{grad}] Final Threshold: {best_t_map[grad]:.2f}')

    # 5. Save
    joblib.dump(model_short, 'vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib')
    joblib.dump(model_std, 'vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib')
    joblib.dump(best_t_map, 'vircraft_rf_vs2-vb-dvf-gn_thr_20260330.joblib')
    
    print(f'\nOptimization Finished with Validation Data Integration!')

if __name__ == '__main__':
    run_experiment()
