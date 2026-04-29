# VirCraft_identify_experiments

This repository provides a comprehensive experimental framework for the VirCraft identify module, including data preparation, model training, validation, and evaluation. The codebase is developed to ensure reproducibility and facilitate systematic benchmarking of identification tasks described in our study.


[01_download_ncbi_data](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/01_download_ncbi_data): Download microbial genomic FASTA files from NCBI, including virus, bacteria, archaea, fungi, algae, and protozoa.

[02_remove_similar_genomes](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/02_remove_similar_genomes): Remove highly similar genomes using a pre-2021-07-23 similarity threshold to reduce redundancy and bias in the dataset.

[03_remove_training_duplicates](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/03_remove_training_duplicates): Eliminate duplicate sequences within the training data to prevent data leakage and ensure fair model evaluation.

[04_split_dataset](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/04_split_dataset): Split the complete dataset into training, validation, and testing sets according to predefined ratios and stratification strategies.

[05_subsample_genomes](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/05_subsample_genomes): Perform genome-level downsampling to balance the distribution of different microbial species in the training set.

[06_remove_prophage](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/06_remove_prophage): Remove prophage sequences from prokaryotic genomes to avoid confounding signals between viral and bacterial sequences.

[07_fragment_subsample](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/07_fragment_subsample): Fragment genomes into fixed-length segments and apply subsampling to generate standardized input sequences for model training.

[08_run_vircraft](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/08_run_vircraft): Execute the VirCraft identification pipeline to extract features and generate predictions on the prepared datasets.

[09_train_random_forest](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/09_train_random_forest): Train a Random Forest classifier using the extracted features, with hyperparameter tuning and cross-validation.

[10_statistics_analysis](https://github.com/yangm9/VirCraft_identify_experiments/tree/master/10_statistics_analysis): Perform comprehensive statistical analysis and visualization of experimental results, including performance metrics, confusion matrices, and comparative benchmarks.


# Repository Structure Notes

Each directory contains the relevant scripts, configuration files, and documentation for its respective pipeline stage. The pipeline is designed to be executed sequentially from `01` to `10`, though intermediate results can be reused for ablation studies or parameter sensitivity analyses.

For detailed usage instructions, please refer to the individual README files within each subdirectory.
