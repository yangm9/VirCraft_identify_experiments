source ~/.bashrc
#seqkit split -i bacteria_plasmid_post20210723_deduped_rm_training.fasta -O bacteria_plasmid_split
#find bacteria_plasmid_split -name "*.fasta" > bacteria_plasmid_list.txt
fastANI --ql bacteria_plasmid_list.txt --rl bacteria_plasmid_list.txt -o bacteria_plasmid_ani.tsv --fragLen 3000 -t 32
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate machine_learning
python ani_cluster_split.py --ani bacteria_plasmid_ani.tsv --fasta_dir bacteria_plasmid_split --out_prefix bacteria_plasmid
