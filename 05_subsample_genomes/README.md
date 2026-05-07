# Dataset Subsampling & Deduplication Toolkit

This directory contains Python scripts for subsampling, deduplication, and category-wise sampling of genome and plasmid datasets, primarily used for building balanced training/validation/test sets.

## File Descriptions

### 1. `filter_each_eukaryote_train_longest.py`
Filters eukaryotic training sets (Fungi, Protist) by selecting the longest sequences up to a specified count.

| Input | Output |
|-------|--------|
| `fungi_genome_train.fasta` | `fungi_genome_train_sub150_longest.fasta` (150 sequences) |
| `protist_genome_train.fasta` | `protist_genome_train_sub250_longest.fasta` (250 sequences) |

### 2. `final_plasmid_sampler_tr245_va95_te91.py`
Performs ANI-based clustering deduplication + random subsampling on bacterial plasmid train/val/test sets.

- Input: `bacteria_plasmid_{train,val,test}.fasta`
- Output: `plasmid_{train,val,test}_sub{249,95,91}.fasta`
- Clustering parameters: ANI ≥ 95%, alignment fraction ≥ 85%
- Selects the longest sequence per cluster as representative, then randomly samples to target count

### 3. `ani_subsampling_for_bacteria_train_longest_by_genus.py`
Selects the longest sequence per genus from the bacterial genome training set based on genus-level ANI results.

- Input:
  - `fa/bacteria_genome_train.fasta`
  - `bacteria_genus_ani/` directory (containing `*_ani.tsv` files)
- Output: `bacteria_genome_train_subsampled_longest.fasta`

### 4. `collect_subsampling_fasta.sh`
One-click execution script that performs:

- Creates `fa/` directory
- Merges bacterial + archaeal plasmids (train/val/test)
- Symlinks genome files for each species
- Sequentially executes the Python scripts above

## Usage

```
bash collect_subsampling_fasta.sh
```

## Dependencies

- Python 3.6+
- Required Python packages:

```
pip install biopython pandas networkx
```

## Expected Directory Structure

.
├── fa/                                    # Auto-created by script
├── bacteria_genus_ani/                    # Genus-level ANI results directory
│   ├── genus1_ani.tsv
│   ├── genus2_ani.tsv
│   └── ...
├── fungi_genome_train.fasta
├── protist_genome_train.fasta
├── bacteria_plasmid_train.fasta
├── bacteria_plasmid_val.fasta
├── bacteria_plasmid_test.fasta
├── archaea_plasmid_train.fasta            # Optional
├── archaea_plasmid_val.fasta              # Optional
├── archaea_plasmid_test.fasta             # Optional
├── bacteria_plasmid_ani.tsv
├── archaea_plasmid_ani.tsv
├── filter_each_eukaryote_train_longest.py
├── final_plasmid_sampler_tr245_va95_te91.py
├── plasmid_train_ani_subsampling_249.py
├── ani_subsampling_for_bacteria_train_longest_by_genus.py
└── collect_subsampling_fasta.sh

## Output Files Summary

| Output File | Source | Count |
|-------------|--------|-------|
| `fungi_genome_train_sub150_longest.fasta` | Fungi | 150 |
| `protist_genome_train_sub250_longest.fasta` | Protist | 250 |
| `plasmid_train_sub249.fasta` | Bacterial + Archaeal plasmids | 249 |
| `plasmid_val_sub95.fasta` | Bacterial plasmids (validation) | 95 |
| `plasmid_test_sub91.fasta` | Bacterial plasmids (test) | 91 |
| `bacteria_genome_train_subsampled_longest.fasta` | Bacterial genomes (per-genus representative) | Varies (number of genera) |

## Important Notes

- **Input validation**: All scripts check for input file existence and skip gracefully if missing, printing a warning message.
- **Memory usage**: Clustering graphs are built using `networkx`; memory consumption scales with the number of sequences. For very large datasets (>10,000 sequences), consider processing in batches.
- **Random sampling**: Random subsampling results are not fixed by default. To ensure reproducibility, add `random.seed(42)` (or any fixed integer) to the Python scripts before random sampling operations.
- **File naming**: All scripts assume specific input filenames as listed above. Modify the `input_file` and `output_file` variables in each script if your filenames differ.
- **ANI file format**: ANI TSV files should contain 5 columns: `query`, `ref`, `ani`, `matched_length`, `total_length` (tab-separated, no header).

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Solution |
|-------|-------------------|
| `ModuleNotFoundError: No module named 'Bio'` | Run `pip install biopython` |
| `ModuleNotFoundError: No module named 'pandas'` | Run `pip install pandas` |
| `ModuleNotFoundError: No module named 'networkx'` | Run `pip install networkx` |
| Input file not found warning | Verify the file exists in the current directory or adjust the path in the script |
| `KeyError` when accessing sequence records | Check that sequence IDs in ANI files match exactly with FASTA headers (script splits on whitespace) |
| High memory usage | For large datasets, consider processing ANI files in chunks or using a more memory-efficient graph library |

## License

This toolkit is provided for research use only. No warranty is implied.

## Contact

For questions or issues, please refer to the script comments or check input file formats.
