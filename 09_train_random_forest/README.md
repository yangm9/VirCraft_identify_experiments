# VirCraft Random Forest Training & Evaluation Suite

This directory contains the complete machine learning pipeline for training, evaluating, and benchmarking the VirCraft hybrid phage identification system. The workflow transitions from expert-defined scoring rules to a data-driven Random Forest classifier, with specialized "Expert" models for different contig length groups.

## Overview

The pipeline consists of eight main stages:

0. **Data Collection** (`0.collect_vc_result_features.py`) – Extracts feature tables from VirCraft results.
1. **Rule-based Scoring** (`1.score_by_rule4xlsx.py`) – Converts raw tool outputs into heuristic scores.
2. **Expert Rule Benchmark** (`1.assess_artificial_score.py`) – Evaluates baseline rule-based combinations.
3. **Feature Matrix Construction** (`2.build_ml_matrix.py`) – Aggregates per-contig tool scores.
4. **Preprocessing & Balancing** (`3.preprocess_ml_features_sample_balanced.py`) – Cleans features and balances the training set.
5. **Model Training** (`4.vircraft_unified_train-v260328.py`) – Trains length-specific Random Forest experts.
6. **Model Inspection** (`5.vircraft_rf_model_info.py`) – Analyzes trained models (feature importance, tree depth, etc.).
7. **Benchmarking** (`6.vircraft_rf_benchmark-v260330.py` & `5.vircraft_rf_benchmark_rm_tool_score_gt2.py`) – Compares VirCraft against external tools, including hard-sample evaluation.

## File Descriptions

| File | Purpose |
|------|---------|
| `0.collect_vc_result_features.py` | Extracts `candidate_viral_ctgs.qual.tsv` files from VirCraft output directories (`08_run_vircraft/{train,val,test}/*_identify/work_files/`) and copies them to `0.data/` with standardized naming: `{label}_{dataset}_{gradient}_viral_ctgs.qual.tsv`. |
| `1.score_by_rule4xlsx.py` | Converts raw tool outputs into heuristic scores. Applies weighted scoring rules for geNomad, VIBRANT, VirSorter2, and DeepVirFinder, plus `add_score` (viral gene enrichment) and `rm_score` (host contamination penalties). Outputs `*.score.tsv` files to `1.score/`. |
| `1.assess_artificial_score.py` | Evaluates all single and combinatorial rule-based scoring strategies (up to 5 tools) on test data. Generates `artificial_score_combinations_with_2_20k.tsv`. |
| `2.build_ml_matrix.py` | Scans the `1.score/` directory, merges per-gradient TSV files, adds labels and metadata, and outputs `{train,val,test}_feature_matrix.csv`. |
| `3.preprocess_ml_features_sample_balanced.py` | Performs feature encoding, missing value handling, and **stratified downsampling** of the training set to the smallest gradient class. Outputs `*_cleaned_matrix.csv`. |
| `4.vircraft_unified_train-v260328.py` | Trains two Random Forest models: one for `1-2k` contigs (`lt2k`) and one for `>2k` contigs (`gt2k`). Uses `PredefinedSplit` with a validation set for hyperparameter tuning. Saves models and optimized thresholds. |
| `5.vircraft_rf_model_info.py` | Loads and prints model details: number of trees, depth statistics, top 15 feature importances, and memory usage. |
| `6.vircraft_rf_benchmark-v260330.py` | Comprehensive benchmark comparing VirCraft v0330 (experts) against external tools (geNomad, DeepVirFinder, VirSorter2, VIBRANT) at 1:19 pos:neg ratio. |
| `6.vircraft_rf_benchmark_rm_tool_score_gt2.py` | **Hard-zone benchmark**: Evaluates only samples where the sum of four raw tool scores is < 2.0. Compares VirCraft experts against external tools on this challenging subset. |
| `rules_contribution.py` | Utility that calculates the marginal contribution of each base rule to combinatorial rule MCC scores. Used internally by `1-2.assess_artificial_score.py`. |

## Output Models & Files

The training script (`4.vircraft_unified_train-v260328.py`) produces:

| File | Description |
|------|-------------|
| `vircraft_rf_vs2-vb-dvf-gn_lt2k_20260330.joblib` | Random Forest model for contigs < 2000 bp |
| `vircraft_rf_vs2-vb-dvf-gn_gt2k_20260330.joblib` | Random Forest model for contigs >= 2000 bp |
| `vircraft_rf_vs2-vb-dvf-gn_thr_20260330.joblib` | Optimal probability thresholds per gradient (1-2k, 2-5k, 5-10k, 10-20k) |

## Workflow Execution Order

To reproduce the full pipeline, run the scripts in the following order:

```
# 0. Extract feature tables from VirCraft results
python 0.collect_vc_result_features.py /path/to/project/root

# 1. Apply rule-based scoring
python 1.score_by_rule4xlsx.py

# 2. Build raw feature matrices from tool outputs
python 2.build_ml_matrix.py

# 3. Preprocess and balance training data
python 3.preprocess_ml_features_sample_balanced.py

# 4. (Optional) Evaluate baseline rule-based combinations
python 1.assess_artificial_score.py

# 5. Train the Random Forest expert models
python 4.vircraft_unified_train-v260328.py

# 6. Inspect trained models
python 5.vircraft_rf_model_info.py

# 7. Run benchmarks
python 6.vircraft_rf_benchmark-v260330.py
python 6.vircraft_rf_benchmark_rm_tool_score_gt2.py
```
