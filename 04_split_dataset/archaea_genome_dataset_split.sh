source ~/.bashrc
seqkit split -i archaea_genome_post20210723_deduped_rm_training.fasta -O archaea_genome_split
find archaea_genome_split -name "*.fasta" > archaea_genome_list.txt
fastANI --ql archaea_genome_list.txt --rl archaea_genome_list.txt -o archaea_genome_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani archaea_genome_ani.tsv --fasta_dir archaea_genome_split --out_prefix archaea_genome
