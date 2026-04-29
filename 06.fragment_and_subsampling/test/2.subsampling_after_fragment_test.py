import os
import subprocess
import math

# ================= Configuration =================
# 1. Original weight benchmark (sum is 0.9)
BASE_WEIGHTS = {
    'bacteria': 0.68,
    'archaea': 0.10,
    'plasmid': 0.05,
    'protist': 0.05,
    'fungi': 0.02
}

# 2. Set target total multiple (Negative Total = 19 * Viral)
TARGET_RATIO = 19.0
BASE_SUM = sum(BASE_WEIGHTS.values()) # 0.9

# 3. Runtime parameters
SEED = 9527
GRADIENTS = ['1-2k', '2-5k', '5-10k', '10-20k']
# =================================================

def get_count(fasta_path):
    """Get the number of sequences in a Fasta file"""
    try:
        res = subprocess.check_output(f"grep -c '>' {fasta_path}", shell=True)
        return int(res.strip())
    except:
        return 0

def main():
    print(f"Start test set (Test) 1:19 downsampling")
    print(f"Strategy: Normalize weights and match total amount to 1:{int(TARGET_RATIO)}")
    
    for grad in GRADIENTS:
        # Locate virus baseline for this gradient (N)
        v_file = f"viral_genome_test_{grad}_uniq.fasta"
        if not os.path.exists(v_file):
            continue
            
        n_viral = get_count(v_file)
        if n_viral == 0:
            continue
            
        print(f"\n--- Gradient {grad} | Virus count (N): {n_viral} ---")
        target_total_neg = n_viral * TARGET_RATIO
        print(f"Total negative target: {int(target_total_neg)}")

        for species, weight in BASE_WEIGHTS.items():
            # Compatible with filename formats
            potential_names = [
                f"{species}_genome_test_{grad}_uniq.fasta",
                f"{species}_test_{grad}_uniq.fasta"
            ]
            input_f = next((f for f in potential_names if os.path.exists(f)), None)
            
            if not input_f:
                continue

            # Core algorithm: (total negative count) * (class weight / 0.9)
            # This ensures bacteria accounts for 0.68/0.9 = 75.56% of total negatives
            target_n = math.ceil(target_total_neg * (weight / BASE_SUM))
            actual_n = get_count(input_f)
            
            final_n = min(target_n, actual_n)
            output_f = f"{species}_test_{grad}_sampled.fasta"

            print(f"  > {species.ljust(10)}: Allocation ratio {(weight/BASE_SUM)*100:.2f}% | Extract {final_n}")

            if final_n > 0:
                cmd = f"seqkit sample -n {final_n} -s {SEED} {input_f} -o {output_f}"
                subprocess.run(cmd, shell=True)

    # 4. Copy virus file as final input
    for grad in GRADIENTS:
        v_in = f"viral_genome_test_{grad}_uniq.fasta"
        v_out = f"viral_test_{grad}_sampled.fasta"
        if os.path.exists(v_in):
            subprocess.run(f"cp {v_in} {v_out}", shell=True)

    print("\nTask completed! All negative samples total is aligned to 19 times the virus count.")

if __name__ == "__main__":
    main()
