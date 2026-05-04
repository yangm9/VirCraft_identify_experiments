#!/usr/bin/env python3

import os
from Bio import SeqIO

ani_dir = "bacteria_genus_ani"
train_fasta = "fa/bacteria_genome_train.fasta"
output_fasta = "bacteria_genome_train_sub1540_longest.fasta"

def parse_id_from_path(path_str):
    return path_str.split('/')[-1].replace('.fasta', '')

def run_longest_sampling():
    # 1. Pre-scanning training set: building ID-to-length mapping and storing in whitelist...
    print(f'Scanning training set length information...: {train_fasta}...')
    id_to_len = {}
    for record in SeqIO.parse(train_fasta, "fasta"):
        id_to_len[record.id.split()[0]] = len(record.seq)
    
    train_whitelist = set(id_to_len.keys())
    print(f'Whitelist loaded successfully. Total {len(train_whitelist)} sequences.')

    # 2. Iterating through ANI folders, selecting the longest sequence per genus...
    genus_files = [f for f in os.listdir(ani_dir) if f.endswith('_ani.tsv')]
    selected_ids = set()
    
    print(f'Starting to extract the longest representative from {len(genus_files)} genera...')
    
    for filename in genus_files:
        genus_pool = set()
        filepath = os.path.join(ani_dir, filename)
        
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 2: continue
                id1 = parse_id_from_path(parts[0])
                id2 = parse_id_from_path(parts[1])
                
                if id1 in train_whitelist: genus_pool.add(id1)
                if id2 in train_whitelist: genus_pool.add(id2)
        
        if genus_pool:
            # --- select the longest ---
            best_id = max(genus_pool, key=lambda x: id_to_len[x])
            selected_ids.add(best_id)

    print(f'Genus-level longest representative screening completed. A total of {len(selected_ids)} sequences selected.')

    # 3. Writing to final file...
    print('Writing Fasta...')
    final_count = 0
    with open(output_fasta, "w") as out_f:
        # To improve efficiency, rescanning Fasta to extract selected IDs...
        for record in SeqIO.parse(train_fasta, "fasta"):
            rid = record.id.split()[0]
            if rid in selected_ids:
                SeqIO.write(record, out_f, "fasta")
                final_count += 1
                selected_ids.remove(rid)
    
    print(f"\nFinished! Finally wrote: {final_count} sequences, file: {output_fasta}")

if __name__ == "__main__":
    if not os.path.exists(train_fasta):
        print(f"Error: could not find input file: {train_fasta}")
    else:
        run_longest_sampling()
