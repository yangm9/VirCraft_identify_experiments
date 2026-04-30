#!/bin/bash
# Set cretion - removing duplicates in training data
# Create set union between pre and post 2020
ln -s ../02_remove_similar_genomes/archaea_genome_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,archaea_genome_post20210723_deduped.fasta out=archaea_genome_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,archaea_genome_union_train_post20210723.fasta out=archaea_genome_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/archaea_plasmid_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,archaea_plasmid_post20210723_deduped.fasta out=archaea_plasmid_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,archaea_plasmid_union_train_post20210723.fasta out=archaea_plasmid_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/bacteria_genome_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,bacteria_genome_post20210723_deduped.fasta out=bacteria_genome_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,bacteria_genome_union_train_post20210723.fasta out=bacteria_genome_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/bacteria_plasmid_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,bacteria_plasmid_post20210723_deduped.fasta out=bacteria_plasmid_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,bacteria_plasmid_union_train_post20210723.fasta out=bacteria_plasmid_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/fungi_genome_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,fungi_genome_post20210723_deduped.fasta out=fungi_genome_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,fungi_genome_union_train_post20210723.fasta out=fungi_genome_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/protist_genome_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,protist_genome_post20210723_deduped.fasta out=protist_genome_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_host.fasta,protist_genome_union_train_post20210723.fasta out=protist_genome_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95


ln -s ../02_remove_similar_genomes/viral_genome_post20210723_deduped.fasta
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_virus.fasta,viral_genome_post20210723_deduped.fasta out=viral_genome_union_train_post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2-vb-dvf-gn_virus.fasta,viral_genome_union_train_post20210723.fasta out=viral_genome_post20210723_deduped_rm_train.fasta uniqueonly=t minidentity=95
