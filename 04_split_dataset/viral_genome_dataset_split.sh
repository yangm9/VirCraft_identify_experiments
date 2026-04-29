source ~/.bashrc
seqkit split -i viral_genome_post20210723_deduped_rm_training.fasta -O viral_genome_split
find viral_genome_split -name "*.fasta" > viral_genome_list.txt
fastANI --ql viral_genome_list.txt --rl viral_genome_list.txt -o viral_genome_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani viral_genome_ani.tsv --fasta_dir viral_genome_split --out_prefix viral_genome
