# remove_provirus.sh

## Overview

This script integrates **Phigaro** and **PhageBoost** pipelines to remove prophage sequences from archaeal and bacterial genomes and plasmids. It processes training, validation, and test datasets in a unified workflow.

## Pipeline Workflow

Input FASTA files
      ↓
Phigaro (prophage prediction)
      ↓
Extract non-prophage regions
      ↓
PhageBoost (phage sequence detection)
      ↓
Mapping & filtering
      ↓
Output: Cleaned FASTA files


## Input Requirements

### Directory Structure

Current working directory/
├── remove_provirus.sh
└── ../2-2.subsampling_rm_training/
└── 1.tran_val_test/
├── archaea_genome_train.fasta
├── archaea_genome_val.fasta
├── archaea_genome_test.fasta
├── archaea_plasmid_train.fasta
├── archaea_plasmid_val.fasta
├── archaea_plasmid_test.fasta
├── bacteria_genome_train.fasta
├── bacteria_genome_val.fasta
├── bacteria_genome_test.fasta
├── bacteria_plasmid_train.fasta
├── bacteria_plasmid_val.fasta
└── bacteria_plasmid_test.fasta


### Software Dependencies

The following tools must be installed and available in your PATH:

| Tool | Purpose |
|------|---------|
| **Phigaro** | Prophage prediction |
| **PhageBoost** | Phage sequence detection |
| **samtools** | FASTA indexing and SAM/BAM processing |
| **bedtools** | BED file operations |
| **minimap2** | Sequence alignment |
| **faidx** | FASTA splitting |
| **parallel** | Parallel processing |

## Usage

### Basic Execution

Run the complete pipeline (Phigaro + PhageBoost):

```
sh 1.remove_provirus.sh
sh 2.link_dataset.sh
```
