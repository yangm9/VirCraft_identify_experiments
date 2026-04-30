# 02_dedupe_similar_genomes

This directory contains shell scripts for removing redundant genome sequences by comparing pre-2021-07-23 and post-2021-07-23 datasets. The deduplication process removes highly similar sequences (95% identity threshold) to reduce bias and ensure independent training and testing sets. The scripts support six microbial groups: archaea, bacteria, fungi, protozoa, algae, and viruses, with separate handling for genomes and plasmids (archaea and bacteria only).

## Dependencies

- BBMap suite (dedupe.sh): https://sourceforge.net/projects/bbmap/

## Scripts and Usage

```
bash archaea_genome_dedupe.sh
bash archaea_plasmid_dedupe.sh
bash bacteria_genome_dedupe.sh
bash bacteria_plasmid_dedupe.sh
bash fungi_genome_dedupe.sh
bash protist_genome_dedupe.sh
bash viral_genome_dedupe.sh
```

## Workflow

1. **Create soft links** to input files from `../01_download_ncbi_data/`
2. **Remove intra-set duplicates** from pre and post sets independently
3. **Create union** of pre and post sets
4. **Remove pre sequences from union** to generate dereplicated post set (95% identity threshold)

## Final Output

| Organism | Genome (deduped post-2021-07-23) | Plasmid (deduped post-2021-07-23) |
|----------|--------------------------------|----------------------------------|
| Archaea | `archaea_genome_post20210723_deduped.fasta` | `archaea_plasmid_post20210723_deduped.fasta` |
| Bacteria | `bacteria_genome_post20210723_deduped.fasta` | `bacteria_plasmid_post20210723_deduped.fasta` |
| Fungi | `fungi_genome_post20210723_deduped.fasta` | - |
| Protist | `protist_genome_post20210723_deduped.fasta` | - |
| Viral | `viral_genome_post20210723_deduped.fasta` | - |

