#!/bin/bash
# Viral genome
ln -s ../01_download_ncbi_data/viral_pre20210723_complete_id.gt1500.fa
ln -s ../01_download_ncbi_data/viral_post20210723_complete_id.gt1500.fa
# Set cretion - removing duplicates
# Removing dupes from within pre and post sets
dedupe.sh -Xmx1000G in=viral_genome_post20210723_complete_id.gt1500.fa out=viral_genome_post20210723_set.fasta ac=f
dedupe.sh -Xmx1000G in=viral_genome_pre20210723_complete_id.gt1500.fa out=viral_genome_pre20210723_set.fasta ac=f
# Create set union between pre and post 2020
dedupe.sh -Xmx1000G in=viral_genome_pre20210723_set.fasta,viral_genome_post20210723_complete_id.gt1500.fa out=viral_genome_union_pre-post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=viral_genome_pre20210723_set.fasta,viral_genome_union_pre-post20210723.fasta out=viral_genome_post20210723_deduped.fasta uniqueonly=t minidentity=95