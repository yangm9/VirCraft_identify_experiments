# Set cretion - removing duplicates
# Create set union between pre and post 2020
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2_vb_dvf_gn_prokaryote.fasta,archaea_genome_post20210723_deduped.fasta out=archaea_genome_union_training-post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx1000G in=traning_data_deduplication/vs2_vb_dvf_gn_prokaryote.fasta,archaea_genome_union_training-post20210723.fasta out=archaea_genome_post20210723_deduped_rm_training.fasta uniqueonly=t minidentity=95
