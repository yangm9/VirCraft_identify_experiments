# Set cretion - removing duplicates
# Create set union between pre and post 2020
dedupe.sh -Xmx50G in=traning_data_deduplication/vs2_vb_dvf_gn_plasmid.fasta,bacteria_plasmid_post20210723_deduped.fasta out=bacteria_plasmid_union_training-post20210723.fasta ac=f
# Minus pre sequences from union to create dereplicated post 2020 sequences.
dedupe.sh -Xmx50G in=traning_data_deduplication/vs2_vb_dvf_gn_plasmid.fasta,bacteria_plasmid_union_training-post20210723.fasta out=bacteria_plasmid_post20210723_deduped_rm_training.fasta uniqueonly=t minidentity=95
