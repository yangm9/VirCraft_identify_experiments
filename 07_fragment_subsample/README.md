# 07_fragment_subsample

This pipeline performs two main steps:

1. **Fragment Generation**: Generate genome fragments of various length ranges from source genomes
2. **Subsampling**: Further subsample the generated fragments to create balanced datasets

## Directory Structure

Current directory (07_fragment_subsample)
├── 1.fragment_train_val_test_data.sh # Main fragment generation script
├── 2.subsampling_after_fragment.sh # Subsampling wrapper script
├── 2.subsampling_after_fragment_train.py
├── 2.subsampling_after_fragment_val.py
├── 2.subsampling_after_fragment_test.py
├── train/ # Training set output directory (generated)
├── val/ # Validation set output directory (generated)
└── test/ # Test set output directory (generated)

## Script 1: `1.fragment_train_val_test_data.sh`

This script generates DNA fragments from source genomes for three datasets (train/val/test) across six genome types and four length ranges.

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Fragment length ranges | 1-2k, 2-5k, 5-10k, 10-20k | Four fragment size categories |
| Genome types | archaea, bacteria, fungi, plasmid, protist, viral | Six source genome types |
| Datasets | train, val, test | Three dataset splits |
| Random seed | 9527 | Fixed seed for reproducibility |
| Mode | unique | Generate unique fragments (no overlaps) |

### Input File Convention

Input genome files are expected at:

`../../0-1.data_new/{type}_{dataset}.fasta`

Examples:
- `../../0-1.data_new/archaea_genome_train.fasta`
- `../../0-1.data_new/viral_genome_test.fasta`
- `../../0-1.data_new/plasmid_val.fasta`

### Output Structure

Generated fragments are saved as:

`{dataset}/{type}{dataset}{suffix}_uniq.fasta`


Example output files:
- `train/archaea_genome_train_1-2k_uniq.fasta`
- `val/viral_genome_val_5-10k_uniq.fasta`
- `test/plasmid_test_10-20k_uniq.fasta`

### Usage

```
# Make sure you are in the 07_fragment_subsample directory
cd /backup/yangming/VIRPHA230501MV/vc_test/mock_data/VirCraft_identify_experiments/07_fragment_subsample

# Run fragment generation
bash 1.fragment_train_val_test_data.sh
```

## Script 2: `2.subsampling_after_fragment.sh`

This wrapper script copies the subsampling Python scripts to each dataset directory and executes them.

### Sub-scripts

| Script | Dataset | Description |
|--------|---------|-------------|
| `2.subsampling_after_fragment_train.py` | train | Subsampling for training set |
| `2.subsampling_after_fragment_val.py` | val | Subsampling for validation set |
| `2.subsampling_after_fragment_test.py` | test | Subsampling for testing set |

### Usage

```
# Run after fragment generation is complete
bash 2.subsampling_after_fragment.sh
```

## Complete Workflow

```bash
# Step 1: Generate fragments
bash 1.fragment_train_val_test_data.sh

# Step 2: Perform subsampling
bash 2.subsampling_after_fragment.sh

## Important Notes

1. **Tool Dependency**: The script requires `fragment_genomes_comprehensively_isoverlap.py` located at `../../bin/`
2. **Input Files**: Ensure all source genome files exist in `../../0-1.data_new/` before running:
  - `*_genome_train.fasta` (archaea, bacteria, fungi, protist, viral)
  - `*_train.fasta` (plasmid)
  - Same for `val` and `test` datasets
3. **Output Directories**: The script creates `train/`, `val/`, and `test/` directories automatically
4. **Random Seed**: Fixed seed (9527) ensures reproducible fragment generation
5. **Python Scripts**: The subsampling Python scripts (`2.subsampling_after_fragment_*.py`) must be present in the current directory before running step 2

## Output File Naming Convention

The naming follows this pattern:

`{dataset}/{genome_type}{dataset}{length_range}_uniq.fasta`


| Component | Example | Description |
|-----------|---------|-------------|
| dataset | train/val/test | Dataset split |
| genome_type | archaea_genome, viral_genome, etc. | Source organism type |
| length_range | 1-2k, 2-5k, 5-10k, 10-20k | Fragment size category |
| uniq | uniq | Indicates unique fragments (no overlaps) |

## Author & Date

- **Experiment:** VIRPHA230501MV
- **Script Location:** `mock_data/VirCraft_identify_experiments/07_fragment_subsample/`
