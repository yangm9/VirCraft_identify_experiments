#!/bin/bash

# Define all combinations: dataset_type_length_lower_length_upper_suffix

for dataset in train val test; do
    mkdir dataset
    for type in archaea_genome bacteria_genome fungi_genome plasmid protist_genome viral_genome; do
        for len_range in "1000 2000 1-2k" "2000 5000 2-5k" "5000 10000 5-10k" "10000 20000 10-20k"; do
            set -- $len_range
            min=$1; max=$2; suf=$3
            ../../bin/fragment_genomes_comprehensively_isoverlap.py $min $max "../06_remove_prophage/${type}_${dataset}.fasta" 9527 unique > "${dataset}/${type}_${dataset}_${suf}_uniq.fasta"
        done
    done
done

echo "All done!"
