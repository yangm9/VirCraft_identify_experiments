/backup/software/miniconda3/etc/profile.d/conda.sh
conda run -n VC-General mmseqs easy-linclust bacteria_plasmid_pre20210723_complete_id.gt1500.fa bacteria_plasmid_pre20210723_complete_id.gt1500.deduped bacteria_plasmid_pre20210723_complete_id.gt1500_mmseqs_tmp --min-seq-id 1.0 -c 1.0 --cov-mode 0 --threads 32

