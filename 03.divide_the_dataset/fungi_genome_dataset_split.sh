source ~/.bashrc
seqkit split -i fungi_genome_post20210723_deduped_rm_training.fasta -O fungi_genome_split
find fungi_genome_split -name "*.fasta" > fungi_genome_list.txt
fastANI --ql fungi_genome_list.txt --rl fungi_genome_list.txt -o fungi_genome_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani fungi_genome_ani.tsv --fasta_dir fungi_genome_split --out_prefix fungi_genome
