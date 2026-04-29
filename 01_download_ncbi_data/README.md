# download_and_divide_ncbi_data

Scripts for downloading microbial genomic data from NCBI RefSeq (archaea, bacteria, fungi, protozoa, algae, viruses).

## Scripts

`download_and_divide_archaea_genomes.sh`
`download_and_divide_bacteria_genomes.sh`
`download_and_divide_fungi_genomes.sh`
`download_and_divide_protozoa_genomes.sh`
`download_and_divide_algae_genomes.sh`
`download_and_divide_viral_genomes.sh`

## Workflow

1. **Filter by date** (pre/post 2021-07-23) and completeness (Complete Genome/Chromosome)
2. **Generate FTP links** from assembly summary
3. **Download** with GNU Parallel (`-j 20`)
4. **Merge** all `.fna.gz` files
5. **Clean headers** (replace spaces with `~`, remove quotes)
6. **Separate** genomes from plasmids
7. **Filter by length** (≥1500 bp)

## Output

| Organism | pre-2021-07-23 (Genome) | post-2021-07-23 (Genome) | pre-2021-07-23 (Plasmid) | post-2021-07-23 (Plasmid) |
|----------|------------------------|--------------------------|--------------------------|---------------------------|
| Archaea | `archaea_genome_pre20210723_complete_id.fna` | `archaea_genome_post20210723_complete_id.fna` | `archaea_plasmid_pre20210723_complete_id.fna` | `archaea_plasmid_post20210723_complete_id.fna` |
| Bacteria | `bacteria_genome_pre20210723_complete_id.fna` | `bacteria_genome_post20210723_complete_id.fna` | `bacteria_plasmid_pre20210723_complete_id.fna` | `bacteria_plasmid_post20210723_complete_id.fna` |
| Fungi | `fungi_genome_pre20210723_complete_id.fna` | `fungi_genome_post20210723_complete_id.fna` | - | - |
| Protozoa | `protozoa_genome_pre20210723_complete_id.fna` | `protozoa_genome_post20210723_complete_id.fna` | - | - |
| Algae | `algae_genome_pre20210723_complete_id.fna` | `algae_genome_post20210723_complete_id.fna` | - | - |
| Viral | `viral_pre20210723_complete_id.fna` | `viral_post20210723_complete_id.fna` | - | - |

## Dependencies

- GNU Parallel, wget, Perl
- `../bin/extrSeqByName.pl`
- `../bin/SeqLenCutoff.pl`

## Usage

```bash
bash download_and_divide_archaea_genomes.sh
```
