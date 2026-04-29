import os
import subprocess
import math

SUB_WEIGHTS = {
    'bacteria': 0.68,
    'archaea': 0.10,
    'plasmid': 0.05,
    'protist': 0.05,
    'fungi': 0.02
}

# Validation set ratio is set to 1:9
TOTAL_NV_RATIO = 9.0 
WEIGHT_SUM = sum(SUB_WEIGHTS.values()) # 0.9

SEED = 9527
GRADIENTS = ['1-2k', '2-5k', '5-10k', '10-20k']
# ==========================================

def get_count(fasta_path):
    """Get the number of sequences in a Fasta file"""
    try:
        res = subprocess.check_output(f"grep -c '>' {fasta_path}", shell=True)
        return int(res.strip())
    except:
        return 0

def main():
    print(f"🚀 Start validation set (Val) downsampling")
    print(f"📍 Set ratio to 1:{int(TOTAL_NV_RATIO)} | Random seed: {SEED}")
    
    for grad in GRADIENTS:
        print(f"\n--- Gradient level: {grad} ---")
        
        # 1. Find validation set virus baseline (N)
        # Match filename like: viral_genome_val_1-2k_uniq.fasta
        v_file = f"viral_genome_val_{grad}_uniq.fasta"
        if not os.path.exists(v_file):
            print(f"  ⚠️ Cannot find virus validation set file for this gradient: {v_file}")
            continue
            
        n_viral = get_count(v_file)
        print(f"  📍 Virus baseline count (N): {n_viral}")

        # 2. Iterate over non-viral categories for this gradient
        for species, weight in SUB_WEIGHTS.items():
            # Compatible with filenames with or without _genome
            potential_names = [
                f"{species}_genome_val_{grad}_uniq.fasta",
                f"{species}_val_{grad}_uniq.fasta"
            ]
            
            input_f = next((f for f in potential_names if os.path.exists(f)), None)
            
            if not input_f:
                print(f"  ⚠️ Skipping {species}: Corresponding val file not found")
                continue

            # Calculate target extraction number (Target = N * 9 * (w/0.9))
            target_n = math.ceil(n_viral * TOTAL_NV_RATIO * (weight / WEIGHT_SUM))
            actual_n = get_count(input_f)
            
            # Determine final count (use all if actual is insufficient)
            final_n = min(target_n, actual_n)
            output_f = f"{species}_val_{grad}_sampled.fasta"

            print(f"  > {species.ljust(10)}: Target {target_n:6d} | Actual {actual_n:8d} -> Extract {final_n:6d}")

            # Use seqkit for sampling
            if final_n > 0:
                cmd = f"seqkit sample -n {final_n} -s {SEED} {input_f} -o {output_f}"
                subprocess.run(cmd, shell=True)
            else:
                print(f"  ⚠️ {species} extraction count is 0, skipping.")

    # 3. Copy validation set virus file as final input
    for grad in GRADIENTS:
        v_in = f"viral_genome_val_{grad}_uniq.fasta"
        v_out = f"viral_val_{grad}_sampled.fasta"
        if os.path.exists(v_in):
            subprocess.run(f"cp {v_in} {v_out}", shell=True)

    print("\n✅ Validation set sampling completed. Output files suffix: _val_..._sampled.fasta")

if __name__ == "__main__":
    main()