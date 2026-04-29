# Set cretion - removing duplicates
# Create set union between pre and post 2020
dedupe.sh -Xmx1000G in=traning_data_deduplication/gn_euk_reference_sequences_deduped.fasta,fungi_genome_post20210723_deduped.fasta out=fungi_genome_union_training-post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/gn_euk_reference_sequences_deduped.fasta,fungi_genome_union_training-post20210723.fasta out=fungi_genome_post20210723_deduped_rm_training.fasta uniqueonly=t minidentity=95
