#!/usr/bin/env python3
import joblib
import numpy as np
import sys
import os

# Define the list of models to check
model_files = {
    'Short Expert (1-2k)': 'vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib',
    'Standard Expert (>2k)': 'vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib'
}

def analyze_model(name, file_path):
    print(f'\n' + '='*80)
    print(f' ANALYZING MODEL: {name} '.center(80, '#'))
    print('='*80)

    if not os.path.exists(file_path):
        print(f'Error: File {file_path} not found.')
        return

    model = joblib.load(file_path)

    # 1. Model basic parameters
    print(f'\n[1] Model Basics')
    print(f'  - Model Type: {type(model)}')
    print(f'  - Number of Trees: {model.n_estimators}')
    print(f'  - Max Depth: {model.max_depth}')
    print(f'  - Min Samples Leaf: {model.min_samples_leaf}')
    
    # 2. Tree depth statistics
    depths = [tree.tree_.max_depth for tree in model.estimators_]
    print(f'  - Avg Tree Depth: {np.mean(depths):.1f} (Min: {np.min(depths)}, Max: {np.max(depths)})')

    # 3. Feature importance analysis
    if hasattr(model, 'feature_importances_'):
        print(f'\n[2] Feature Importances (Top 15)')
        print(f"  {'Rank':<6} {'Importance':<12} {'Feature Name'}")
        print('  ' + '-'*60)
        
        importances = model.feature_importances_
        feature_names = getattr(model, 'feature_names_in_', [f'Feature_{i}' for i in range(len(importances))])
        
        # Sort in descending order
        sorted_indices = np.argsort(importances)[::-1]
        
        for rank, idx in enumerate(sorted_indices[:15], 1): # Only show the top 15 for easy comparison
            print(f'  {rank:<6} {importances[idx]:<12.6f} {feature_names[idx]}')

        # statistics
        print(f'\n[3] Statistics')
        print(f'  - Feature count: {len(importances)}')
        print(f'  - Mean importance: {np.mean(importances):.6f}')
        print(f'  - Zero importance features: {np.sum(importances == 0)}')

    # 4. memory
    print(f'\n[4] Memory Usage: {sys.getsizeof(model) / 1024 / 1024:.2f} MB')

def run_analysis():
    # Check the threshold table
    thr_path = 'vircraft_rf_expert_thr_20260330.joblib'
    if os.path.exists(thr_path):
        thr_map = joblib.load(thr_path)
        print('\n' + ' OPTIMAL THRESHOLDS '.center(80, '='))
        for grad, t in thr_map.items():
            print(f'  - {grad:<10}: {t:.2f}')

    # Analyze the two expert models
    for name, path in model_files.items():
        analyze_model(name, path)

if __name__ == '__main__':
    run_analysis()
