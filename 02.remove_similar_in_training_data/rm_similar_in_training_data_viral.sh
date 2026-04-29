# Set cretion - removing duplicates
# Create set union between pre and post 2020
dedupe.sh -Xmx50G in=traning_data_deduplication/vs2_vb_dvf_gn_virus.fasta,viral_genome_post20210723_deduped.fasta out=viral_union_training-post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx50G in=traning_data_deduplication/vs2_vb_dvf_gn_virus.fasta,viral_union_training-post20210723.fasta out=viral_post20210723_deduped_rm_training.fasta uniqueonly=t minidentity=95
