# 01_download_ncbi_data

This directory contains shell scripts for downloading and preprocessing microbial genomic data from NCBI RefSeq database. The scripts support six microbial groups: archaea, bacteria, fungi, protozoa, algae, and viruses. Each script performs the following key steps: (1) downloads the assembly summary from NCBI, (2) filters complete genomes and chromosomes based on a cutoff date (2021-07-23), (3) generates FTP links, (4) downloads genomic FASTA files using GNU Parallel, (5) separates chromosomes from plasmids (for archaea and bacteria), (6) cleans sequence headers, and (7) filters sequences by length (≥1500 bp). The pre-2021-07-23 and post-2021-07-23 splits are used for subsequent similarity removal and model training.

## Dependencies

- GNU Parallel, wget, Perl
- `../bin/extrSeqByName.pl`
- `../bin/SeqLenCutoff.pl`

## Scripts and Usage

```
bash download_and_divide_archaea_genomes.sh
bash download_and_divide_bacteria_genomes.sh
bash download_and_divide_fungi_genomes.sh
bash download_and_divide_protozoa_genomes.sh
bash download_and_divide_algae_genomes.sh
bash download_and_divide_viral_genomes.sh
```

## Workflow

1. **Filter by date** (pre/post 2021-07-23) and completeness (Complete Genome/Chromosome)
2. **Generate FTP links** from assembly summary
3. **Download** with GNU Parallel (`-j 20`)
4. **Merge** all `.fna.gz` files
5. **Clean headers** (replace spaces with `~`, remove quotes)
6. **Separate** genomes from plasmids
7. **Filter by length** (≥1500 bp)

## Final Output

| Organism | pre-2021-07-23 (Genome) | post-2021-07-23 (Genome) | pre-2021-07-23 (Plasmid) | post-2021-07-23 (Plasmid) |
|----------|------------------------|--------------------------|--------------------------|---------------------------|
| Archaea | `archaea_genome_pre20210723_complete_id.gt1500.fa` | `archaea_genome_post20210723_complete_id.gt1500.fa` | `archaea_plasmid_pre20210723_complete_id.gt1500.fa` | `archaea_plasmid_post20210723_complete_id.gt1500.fa` |
| Bacteria | `bacteria_genome_pre20210723_complete_id.gt1500.fa` | `bacteria_genome_post20210723_complete_id.gt1500.fa` | `bacteria_plasmid_pre20210723_complete_id.gt1500.fa` | `bacteria_plasmid_post20210723_complete_id.gt1500.fa` |
| Fungi | `fungi_genome_pre20210723_complete_id.gt1500.fa` | `fungi_genome_post20210723_complete_id.gt1500.fa` | - | - |
| Protozoa | `protozoa_genome_pre20210723_complete_id.gt1500.fa` | `protozoa_genome_post20210723_complete_id.gt1500.fa` | - | - |
| Algae | `algae_genome_pre20210723_complete_id.gt1500.fa` | `algae_genome_post20210723_complete_id.gt1500.fa` | - | - |
| Viral | `viral_pre20210723_complete_id.gt1500.fa` | `viral_post20210723_complete_id.gt1500.fa` | - | - |

