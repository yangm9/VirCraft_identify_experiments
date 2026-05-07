import os
import subprocess
import math

SUB_WEIGHTS = {
    'bacteria': 0.68,
    'archaea': 0.10,
    'plasmid': 0.05,
    'protist': 0.05,
    'fungi': 0.02
} #total = 0.9
TOTAL_NV_RATIO = 3.0
WEIGHT_SUM = sum(SUB_WEIGHTS.values()) # 0.9
SEED = 9527
GRADIENTS = ['1-2k', '2-5k', '5-10k', '10-20k']

def get_count(fasta_path):
    #Get the sequence number in Fasta
    try:
        res = subprocess.check_output(f"grep -c '>' {fasta_path}", shell=True)
        return int(res.strip())
    except:
        return 0

def main():
    print(f"Subsampling, seed: {SEED}")
    
    for grad in GRADIENTS:
        print(f"\n--- length level: {grad} ---")
        # 1. Find and determine the number of viral reference sequences (N) for this gradient
        v_file = f"viral_genome_train_{grad}_uniq.fasta"
        if not os.path.exists(v_file):
            print(f"Error: could not find file: {v_file}")
            continue
            
        n_viral = get_count(v_file)
        print(f"viral sequence number: {n_viral}")

        # 2. Iterate through all non-virus categories under this gradient
        for species, weight in SUB_WEIGHTS.items():
            # Compatible with filename format (some with '_genome', some without)
            potential_names = [
                f"{species}_genome_train_{grad}_uniq.fasta",
                f"{species}_train_{grad}_uniq.fasta"
            ]
            
            input_f = next((f for f in potential_names if os.path.exists(f)), None)
            
            if not input_f:
                print(f"Skip {species}: could not find the input file.")
                continue

            # Calculate the target extraction number (Target = N * 3 * (w / 0.9)) 
            target_n = math.ceil(n_viral * TOTAL_NV_RATIO * (weight / WEIGHT_SUM))
            actual_n = get_count(input_f)
            
            # Determine the final execution quantity (if insufficient, retain the full amount)
            final_n = min(target_n, actual_n)
            output_f = f"{species}_train_{grad}_sampled.fasta"

            print(f"  > {species.ljust(10)}: Target {target_n:6d} | Actual {actual_n:8d} -> Sampled {final_n:6d}")

            # Use seqkit for subsampling
            cmd = f"seqkit sample -n {final_n} -s {SEED} {input_f} -o {output_f}"
            subprocess.run(cmd, shell=True)

    # 3. Directly link or rename the virus file as the result
    for grad in GRADIENTS:
        v_in = f"viral_genome_train_{grad}_uniq.fasta"
        v_out = f"viral_train_{grad}_sampled.fasta"
        if os.path.exists(v_in):
            subprocess.run(f"cp {v_in} {v_out}", shell=True)

    print("\nAll done! The suffix of result file is: _sampled.fasta")

if __name__ == "__main__":
    main()
