# 04_split_dataset

This directory contains scripts for splitting each dataset into training, validation, and testing sets based on ANI (Average Nucleotide Identity) clustering.

## Files

| File | Description |
|------|-------------|
| `realm.list` | List of dataset names to be processed |
| `mk_run_dataset_split.sh` | Script to generate and execute ANI-based splitting for each dataset |

## Dependencies

- seqkit
- fastANI
- Python with `../ani_cluster_split.py`

## Usage

```
sh mk_run_dataset_split.sh
```

## Output Files

| Type | Files |
|------|-------|
| **Training Sets** | `archaea_genome_train.fasta`, `archaea_plasmid_train.fasta`, `bacteria_genome_train.fasta`, `bacteria_plasmid_train.fasta`, `fungi_genome_train.fasta`, `protist_genome_train.fasta`, `viral_genome_train.fasta` |
| **Validation Sets** | `archaea_genome_val.fasta`, `archaea_plasmid_val.fasta`, `bacteria_genome_val.fasta`, `bacteria_plasmid_val.fasta`, `fungi_genome_val.fasta`, `protist_genome_val.fasta`, `viral_genome_val.fasta` |
| **Testing Sets** | `archaea_genome_test.fasta`, `archaea_plasmid_test.fasta`, `bacteria_genome_test.fasta`, `bacteria_plasmid_test.fasta`, `fungi_genome_test.fasta`, `protist_genome_test.fasta`, `viral_genome_test.fasta` |
| **Intermediate Directories** | `archaea_genome_split/`, `archaea_plasmid_split/`, `bacteria_genome_split/`, `bacteria_plasmid_split/`, `fungi_genome_split/`, `protist_genome_split/`, `viral_genome_split/` |

## Notes
- Input files are from `../03_remove_training_duplicates/` with suffix `_post20210723_deduped_rm_training.fasta`
- ANI calculation uses 3000bp fragments and 32 threads
- `../bin/ani_cluster_split.py` performs clustering and splits data into train/val/test sets. Specifically, this program clusters genome sequences based on fastANI-calculated similarity scores, then splits the data into training, validation, and test sets (default ratio 8:1:1) at the cluster level. It filters high-confidence sequence pairs using two parameters: --ani_cutoff (default 95.0) and --af_cutoff (default 0.85), constructs a graph, and extracts connected components as clusters. This ensures that highly similar genomes (e.g., the same species or closely related strains) are always assigned to the same dataset, preventing data leakage during model evaluation. The program outputs three FASTA files: training set (`{out_prefix}_train.fasta`), validation set (`{out_prefix}_val.fasta`), and test set ({`out_prefix}_test.fasta`).
