source ~/.bashrc
seqkit split -i archaea_plasmid_post20210723_deduped_rm_training.fasta -O archaea_plasmid_split
find archaea_plasmid_split -name "*.fasta" > archaea_plasmid_list.txt
fastANI --ql archaea_plasmid_list.txt --rl archaea_plasmid_list.txt -o archaea_plasmid_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani archaea_plasmid_ani.tsv --fasta_dir archaea_plasmid_split --out_prefix archaea_plasmid
