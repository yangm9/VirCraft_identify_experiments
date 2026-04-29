source ~/.bashrc
seqkit split -i protist_genome_post20210723_deduped_rm_training.fasta -O protist_genome_split
find protist_genome_split -name "*.fasta" > protist_genome_list.txt
fastANI --ql protist_genome_list.txt --rl protist_genome_list.txt -o protist_genome_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani protist_genome_ani.tsv --fasta_dir protist_genome_split --out_prefix protist_genome
