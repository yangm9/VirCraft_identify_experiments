source ~/.bashrc
#seqkit split -i bacteria_genome_post20210723_deduped_rm_training.fasta -O bacteria_genome_split
#find bacteria_genome_split -name "*.fasta" > bacteria_genome_list.txt
#fastANI --ql bacteria_genome_list.txt --rl bacteria_genome_list.txt -o bacteria_genome_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
#python ani_cluster_split.py --ani bacteria_genome_ani.tsv --fasta_dir bacteria_genome_split --out_prefix bacteria_genome
python ani_cluster_split_for_bacteria.py --ani bacteria_genome_ani.tsv --fasta_dir bacteria_split/bacteria_genome_split --out_prefix bacteria_genome
