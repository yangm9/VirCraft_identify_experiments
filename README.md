# VirCraft identify experiments

This repository contains the reproducible data-preparation, VirCraft feature-generation, and Random Forest training workflow used for the VirCraft `identify` experiments. The pipeline is organized as numbered stages so that each directory represents one step in the experimental workflow.

> **Scope:** this repository stores scripts, documentation, and trained Random Forest model artifacts for the VirCraft identify benchmark. Large intermediate FASTA files and tool outputs are expected to be generated locally and are not necessarily tracked in Git.

## Repository layout

| Stage | Directory | Purpose | Main entry points |
|---:|---|---|---|
| 01 | [`01_download_ncbi_data/`](01_download_ncbi_data/) | Download complete microbial genomes/chromosomes from NCBI RefSeq, split records by the 2021-07-23 cutoff date, clean FASTA headers, separate archaeal/bacterial plasmids, and retain sequences ≥1,500 bp. | `download_and_divide_archaea_genomes.sh`, `download_and_divide_bacteria_genomes.sh`, `download_and_divide_fungi_genomes.sh`, `download_and_divide_protozoa_genomes.sh`, `download_and_divide_alga_genomes.sh`, `download_and_divide_viral_genomes.sh` |
| 02 | [`02_remove_similar_genomes/`](02_remove_similar_genomes/) | Remove highly similar genomes between pre-cutoff and post-cutoff datasets to reduce redundancy and temporal leakage. | `*_dedupe.sh` |
| 03 | [`03_remove_training_duplicates/`](03_remove_training_duplicates/) | Collect training references from VirSorter2, VIBRANT, VirFinder/DeepVirFinder, and geNomad, then remove sequences similar to those training references. | `1.collect_vs2-vb-dvf-gn_train_data.sh`, `2.rm_similar_in_vs2-vb-dvf-gn_train_data.sh` |
| 04 | [`04_split_dataset/`](04_split_dataset/) | Cluster datasets by ANI and split clusters into train/validation/test sets. | `mk_run_dataset_split.sh`, `realm.list` |
| 05 | [`05_subsample_genomes/`](05_subsample_genomes/) | Subsample genomes/plasmids to control class imbalance and over-representation of closely related taxa. | `collect_subsampling_fasta.sh` |
| 06 | [`06_remove_prophage/`](06_remove_prophage/) | Remove predicted prophage regions from prokaryotic genomes using Phigaro and PhageBoost before negative-set construction. | `1.remove_provirus.sh`, `2.link_dataset.sh` |
| 07 | [`07_fragment_subsample/`](07_fragment_subsample/) | Fragment full-length sequences into non-overlapping contigs and subsample by dataset split and length bin. | `1.fragment_train_val_test_data.sh`, `2.subsampling_after_fragment.sh` |
| 08 | [`08_run_vircraft/`](08_run_vircraft/) | Run VirCraft `identify`, CheckV, and proviral prediction on train/validation/test fragments. | `mk_identify_data.sh`, `train_sample.list`, `val_sample.list`, `test_sample.list` |
| 09 | [`09_train_random_forest/`](09_train_random_forest/) | Convert VirCraft outputs into scored feature matrices, train length-aware Random Forest models, inspect models, and run benchmarks. | `0.collect_vc_result_features.py` through `6.vircraft_rf_benchmark-v260330.py` |
| tools | [`bin/`](bin/) | Shared helper scripts for sequence extraction, length filtering, ANI splitting, linking tables, and genome fragmentation. | `ani_cluster_split.py`, `fragment_genomes_comprehensively_isoverlap.py`, `SeqLenCutoff.pl`, `extrSeqByName.pl` |

## End-to-end workflow

Run the stages in numerical order. The typical workflow is:

```bash
# 01. Download and preprocess NCBI RefSeq data
cd 01_download_ncbi_data
bash download_and_divide_archaea_genomes.sh
bash download_and_divide_bacteria_genomes.sh
bash download_and_divide_fungi_genomes.sh
bash download_and_divide_protozoa_genomes.sh
bash download_and_divide_alga_genomes.sh
bash download_and_divide_viral_genomes.sh

# 02. Remove highly similar post-cutoff genomes
cd ../02_remove_similar_genomes
bash archaea_genome_dedupe.sh
bash archaea_plasmid_dedupe.sh
bash bacteria_genome_dedupe.sh
bash bacteria_plasmid_dedupe.sh
bash fungi_genome_dedupe.sh
bash protist_genome_dedupe.sh
bash viral_genome_dedupe.sh

# 03. Remove sequences similar to public training references
cd ../03_remove_training_duplicates
bash 1.collect_vs2-vb-dvf-gn_train_data.sh
bash 2.rm_similar_in_vs2-vb-dvf-gn_train_data.sh

# 04. ANI-aware train/validation/test split
cd ../04_split_dataset
sh mk_run_dataset_split.sh

# 05. Genome/plasmid subsampling
cd ../05_subsample_genomes
bash collect_subsampling_fasta.sh

# 06. Prophage removal and dataset linking
cd ../06_remove_prophage
bash 1.remove_provirus.sh
bash 2.link_dataset.sh

# 07. Fragment and subsample contigs
cd ../07_fragment_subsample
bash 1.fragment_train_val_test_data.sh
bash 2.subsampling_after_fragment.sh

# 08. Run VirCraft identify and CheckV
cd ../08_run_vircraft
bash mk_identify_data.sh

# 09. Build ML matrices, train models, and benchmark
cd ../09_train_random_forest
python 0.collect_vc_result_features.py ..
python 1.score_by_rule4xlsx.py
python 2.build_ml_matrix.py
python 3.preprocess_ml_features_sample_balanced.py
python 1.assess_artificial_score.py
python 4.vircraft_unified_train-v260328.py
python 5.vircraft_rf_model_info.py
python 6.vircraft_rf_benchmark-v260330.py
python 6.vircraft_rf_benchmark_rm_tool_score_gt2.py
```

## Key methodological design choices

- **Temporal holdout:** genome records are separated using a 2021-07-23 cutoff date before downstream processing, reducing the risk that evaluation sequences overlap with older reference/training material.
- **Similarity-aware filtering:** BBMap `dedupe.sh`, fastANI, and ANI graph clustering are used to reduce redundant sequences and keep train/validation/test partitions more independent.
- **Training-reference decontamination:** reference sequences used by VirSorter2, VIBRANT, VirFinder/DeepVirFinder, and geNomad are collected and compared against the experimental datasets to limit external training-set leakage.
- **Prophage-aware negative controls:** predicted prophage regions are removed from archaeal and bacterial genomes before constructing negative examples, reducing viral-signal contamination in host-derived contigs.
- **Length-stratified evaluation:** fragments are generated in four bins (`1-2k`, `2-5k`, `5-10k`, and `10-20k`) to evaluate performance across short and longer contigs.
- **Length-aware models:** Random Forest classifiers are trained separately for short (`1-2k`) and standard (`>2k`) contigs, with validation-set threshold tuning by length bin.

## Dependencies

The workflow uses a mixture of command-line bioinformatics tools, Python packages, and external viral-identification programs. Install only the components required for the stages you plan to run.

### Command-line tools

- GNU Parallel, `wget`, Perl
- BBMap (`dedupe.sh`)
- `seqkit`
- fastANI
- samtools / faidx
- bedtools
- minimap2
- Phigaro
- PhageBoost
- VirCraft
- CheckV

### Python packages

Common Python dependencies include:

```bash
pip install biopython pandas numpy networkx scikit-learn joblib
```

Some benchmarking or downstream analysis scripts may require additional plotting/statistics packages depending on local usage.

## Methodology text for manuscripts

A journal-ready methodology draft is provided in [`METHODS.md`](METHODS.md). It summarizes data acquisition, leakage control, train/validation/test splitting, fragment construction, VirCraft feature extraction, Random Forest training, threshold optimization, and benchmarking in manuscript style.

## Notes and known assumptions

- The workflow expects large FASTA files and intermediate tool outputs to be present in the stage directories at runtime; these files are typically generated locally and are not tracked in the repository.
- Several scripts assume execution from their own directory and use relative paths to neighboring stages.
- `10_statistics_analysis/` is not present in the current repository snapshot; statistical analysis should therefore be documented separately or added as a new stage if needed.
- For detailed per-stage parameters and expected outputs, see each subdirectory README.
