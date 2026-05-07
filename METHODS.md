# Methods draft for manuscript

The following text is a manuscript-ready methods draft for the VirCraft `identify` data-preparation and Random Forest training workflow. Please adapt the tense, citation style, software versions, database access dates, and final sample counts to the target journal requirements before submission.

## Dataset acquisition and temporal partitioning

Microbial genome sequences were obtained from the NCBI RefSeq assembly resources for viruses, bacteria, archaea, fungi, algae, and protozoa. Only complete genomes or chromosome-level assemblies were retained. Records were divided according to an acquisition-date cutoff of 23 July 2021, producing pre-cutoff and post-cutoff sequence collections. FASTA headers were normalized to avoid downstream parsing errors, bacterial and archaeal plasmid sequences were separated from chromosomal genome sequences, and sequences shorter than 1,500 bp were removed. This temporal separation was used to reduce the possibility that the evaluation data overlapped with older public references or tool training data.

## Redundancy reduction and training-reference decontamination

To reduce redundancy and potential information leakage, highly similar genomes were removed before model construction. Pre-cutoff and post-cutoff datasets were deduplicated within each organismal group, and post-cutoff sequences with high similarity to pre-cutoff sequences were excluded. In addition, training references associated with commonly used viral-identification tools, including VirSorter2, VIBRANT, VirFinder/DeepVirFinder, and geNomad, were collected from their public training or reference resources. Experimental sequences similar to these reference collections were removed to minimize overlap between benchmark sequences and external model-training data.

## ANI-aware train, validation, and test splitting

Average nucleotide identity (ANI) was used to construct similarity-aware dataset partitions. Each organismal dataset was first split into individual genome FASTA files and compared all-against-all using fastANI with a fragment length of 3,000 bp. ANI hits were filtered using an ANI threshold of 95% and an aligned-fraction threshold of 0.85. A graph was then constructed in which genomes were represented as nodes and high-similarity ANI relationships were represented as edges. Connected components of this graph were treated as sequence-similarity clusters. Clusters, rather than individual sequences, were randomly assigned to training, validation, and test partitions at an 8:1:1 ratio using a fixed random seed. This cluster-aware splitting strategy was designed to prevent closely related genomes from being distributed across different model-development partitions.

## Genome and plasmid subsampling

Subsampling was performed after dataset splitting to limit over-representation of large or densely sampled organismal groups. Eukaryotic training genomes were reduced by selecting the longest available sequences up to fixed target counts. Bacterial genomes were subsampled using genus-aware ANI information, selecting representative long sequences within genus-level groupings. Bacterial and archaeal plasmids were merged where appropriate and clustered using ANI-based criteria; the longest sequence from each cluster was retained as a representative before random subsampling to the target split-specific counts. This step generated a more balanced negative-sequence collection while preserving taxonomic and sequence diversity.

## Removal of prophage regions from prokaryotic negative controls

Because bacterial and archaeal genomes can contain integrated prophages, prophage regions were removed before using prokaryotic genomes as negative controls. Prophage prediction was performed with Phigaro and PhageBoost for archaeal genome, archaeal plasmid, bacterial genome, and bacterial plasmid datasets across the training, validation, and test splits. Predicted viral/prophage intervals were converted to genomic coordinates, sorted, and subtracted from the corresponding host genome intervals using bedtools. The remaining non-prophage regions were extracted as FASTA sequences and used for subsequent negative-fragment generation. This step was intended to reduce viral signal contamination in host-derived negative examples.

## Fragment generation and length stratification

Full-length viral, prokaryotic, plasmid, fungal, and protist sequences were fragmented into non-overlapping contigs to emulate metagenomic contig inputs. Fragment lengths were sampled within four predefined bins: 1,000-2,000 bp, 2,000-5,000 bp, 5,000-10,000 bp, and 10,000-20,000 bp. Fragmentation used a fixed random seed to improve reproducibility. After fragmentation, additional split-specific subsampling was applied to produce standardized positive and negative sequence sets for model training, validation, and independent testing. The length-stratified design allowed model behavior to be assessed separately for short contigs and longer contigs.

## VirCraft feature generation and quality annotation

VirCraft `identify` was run on each length-stratified FASTA file under permissive mode using the `vs2-vb-dvf-gn` tool combination, which integrates VirSorter2, VIBRANT, DeepVirFinder, and geNomad evidence. Candidate viral contig tables and associated quality feature files were collected from the VirCraft working directories. CheckV was additionally run on the same input fragments, and proviral prediction results were generated from the candidate viral contig information and CheckV outputs. These outputs were used to build per-contig feature tables containing tool-specific scores, rule-derived scores, sequence labels, dataset split identifiers, and length-bin metadata.

## Rule-based scoring and feature-matrix construction

Raw tool outputs were transformed into rule-based feature scores for each contig. The scoring workflow incorporated evidence from geNomad, VIBRANT, VirSorter2, and DeepVirFinder, together with additional positive evidence based on viral-gene enrichment and negative evidence reflecting host-contamination signals. Per-length-bin score tables were merged into train, validation, and test feature matrices. Missing values and categorical fields were standardized during preprocessing. To reduce imbalance during model fitting, the training set was stratified and downsampled according to the smallest length-bin class, while validation and test matrices were retained for threshold optimization and final evaluation.

## Random Forest model training and threshold optimization

Random Forest classifiers were trained using the cleaned feature matrices. Because short contigs are typically more difficult to classify and may have different feature distributions, two length-aware expert models were trained: one model for 1,000-2,000 bp contigs and one model for contigs longer than 2,000 bp. Hyperparameters were selected by grid search using a predefined split in which the training partition was used for model fitting and the validation partition was used for parameter selection. Matthews correlation coefficient (MCC) was used as the optimization metric. Each Random Forest used 300 trees, balanced class weighting, parallel execution, and a fixed random seed. After hyperparameter selection, probability thresholds were optimized separately for each length bin on the validation set by scanning thresholds from 0.10 to 0.90 in 0.01 increments and selecting the threshold with the highest MCC. The final model artifacts and length-bin threshold map were saved for downstream benchmarking.

## Benchmarking and evaluation

The trained VirCraft Random Forest models were evaluated on held-out test data and compared with external viral-identification evidence from geNomad, DeepVirFinder, VirSorter2, and VIBRANT. Benchmarking was performed using length-stratified test sets and a positive-to-negative ratio designed to approximate low-prevalence viral discovery settings. In addition to overall benchmarking, a hard-sample analysis was performed on contigs with weak aggregate evidence from the component tools, enabling assessment of whether the Random Forest model improved classification for difficult cases. Performance should be reported using threshold-dependent metrics such as sensitivity, specificity, precision, F1 score, and MCC, together with any journal-required confidence intervals or replicate analyses.

## Reproducibility notes

The workflow uses fixed random seeds for ANI-aware splitting, fragment generation, and Random Forest training where implemented in the scripts. Exact reproducibility additionally requires recording software versions, database versions, NCBI download dates, CheckV database version, VirCraft version, and final sample counts after each filtering and subsampling step. These details should be added to the final manuscript and supplementary materials once the production run is complete.
