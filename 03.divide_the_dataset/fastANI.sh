source ~/.bashrc
seqkit split -i viral_genome_post20210723_deduped_rm_training.fasta -O viral_genome_split
ls viral_genome_split/*.fasta > viral_genome_list.txt
fastANI --ql viral_genome_list.txt --rl viral_genome_list.txt -o viral_genome_ani.tsv --fragLen 3000 -t 32
python ani_cluster_split.py --ani viral_genome_ani.tsv --fasta_dir viral_genome_split --out_prefix viral_genome
