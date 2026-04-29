#!/usr/bin/env python3
import pandas as pd
import os
import glob

def build_matrices():
    """
    Feature Matrix Builder:
    1. Scans the '1.score' directory for scattered feature files.
    2. Merges them into standardized training/validation/test datasets.
    3. Performs feature engineering (labeling, metadata recording, cleaning).
    4. Saves the results to '2.build_ml_matrix'.
    """
    current_dir = os.getcwd()
    
    # Define input and output directories
    input_dir = os.path.join(current_dir, "1.score")
    output_dir = os.path.join(current_dir, "2.build_ml_matrix")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    datasets = ['train', 'val', 'test']
    print(f"🚀 Starting to merge feature matrices from {input_dir}...")

    for ds in datasets:
        # 1. Automated File Matching (Scan)
        # Search within the 1.score directory for files matching the pattern
        pattern = f"*_{ds}_*_viral_ctgs.qual.score.tsv"
        files = glob.glob(os.path.join(input_dir, pattern))
        
        if not files:
            print(f"⚠️ No files found for {ds} collection, skipping...")
            continue
            
        all_dfs = []
        print(f"📂 Processing {ds} collection, total {len(files)} files found...")

        for f in files:
            fname = os.path.basename(f)
            
            # 2. Core Feature Engineering
            # Parse filenames to extract metadata (label and gradient)
            parts = fname.split('_')
            label_str = parts[0]    # e.g., positive or negative
            gradient = parts[2]     # e.g., 1-2k, 2-5k, etc.
            
            # Read the TSV file
            df = pd.read_csv(f, sep='\t')
            
            # --- Main Data Operations ---
            # A. Labeling: 1 for positive (virus), 0 for negative (non-virus)
            df['label'] = 1 if label_str == "positive" else 0
            
            # B. Metadata: Record length gradient and dataset source
            df['origin_gradient'] = gradient
            df['dataset_type'] = ds
            
            all_dfs.append(df)

        # 3. Dataset Merging (Merge)
        if all_dfs:
            # Vertically stack all dataframes from different gradients
            final_df = pd.concat(all_dfs, axis=0, ignore_index=True)
            
            # C. Data Cleaning: Fill missing values (NaN) with 0 for ML compatibility
            final_df = final_df.fillna(0)
            
            # 4. Statistics and Output
            output_file = os.path.join(output_dir, f"{ds}_feature_matrix.csv")
            final_df.to_csv(output_file, index=False)
            
            # Print class distribution statistics (Check for class imbalance)
            pos_count = len(final_df[final_df['label'] == 1])
            neg_count = len(final_df[final_df['label'] == 0])
            print(f"✅ Generated: {output_file}")
            print(f"📊 Stats: Total rows: {len(final_df)} (Positives: {pos_count}, Negatives: {neg_count})")

    print(f"\n✨ All matrices constructed in {output_dir}! You can now proceed to Random Forest training.")

if __name__ == "__main__":
    build_matrices()
