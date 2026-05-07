#!/bin/bash

# Archaea genome
ln -s archaea_genome_train.phigaro.phageboost.fasta archaea_genome_train.fasta
ln -s archaea_genome_val.phigaro.phageboost.fasta archaea_genome_val.fasta
ln -s archaea_genome_test.phigaro.phageboost.fasta archaea_genome_test.fasta

# Bacteria genome
ln -s bacteria_genome_train.phigaro.phageboost.fasta bacteria_genome_train.fasta
ln -s bacteria_genome_val.phigaro.phageboost.fasta bacteria_genome_val.fasta
ln -s bacteria_genome_test.phigaro.phageboost.fasta bacteria_genome_test.fasta

# Plasmid sequence
cat archaea_plasmid_test.phigaro.phageboost.fasta bacteria_plasmid_test.phigaro.phageboost.fasta >plasmid_test.fasta
cat archaea_plasmid_train.phigaro.phageboost.fasta bacteria_plasmid_train.phigaro.phageboost.fasta >plasmid_train.fasta
cat archaea_plasmid_val.phigaro.phageboost.fasta bacteria_plasmid_val.phigaro.phageboost.fasta >plasmid_val.fasta

# Fungi genome
ln -s ../05_subsample_genomes/fungi_genome_train_sub150_longest.fasta fungi_genome_train.fasta
ln -s ../04_split_dataset/fungi_genome_val.fasta
ln -s ../04_split_dataset/fungi_genome_test.fasta 

# Protist genome
ln -s ../05_subsample_genomes/protist_genome_train_sub250_longest.fasta protist_genome_train.fasta
ln -s ../04_split_dataset/protist_genome_val.fasta
ln -s ../04_split_dataset/protist_genome_test.fasta

# Viral Genome
ln -s ../04_split_dataset/viral_genome_train.fasta
ln -s ../04_split_dataset/viral_genome_test.fasta
ln -s ../04_split_dataset/viral_genome_val.fasta
