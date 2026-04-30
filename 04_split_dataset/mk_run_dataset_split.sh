# Make a script for spliting each dataset stored in realm.list
cat realm.list|while read i;do echo -e "source ~/.bashrc\nseqkit split -i ../03_remove_training_duplicates/${i}_post20210723_deduped_rm_training.fasta -O ${i}_split\nfind ${i}_split -name \"*.fasta\" > ${i}_list.txt\nfastANI --ql ${i}_list.txt --rl ${i}_list.txt -o ${i}_ani.tsv --fragLen 3000 -t 32\nsource ~/miniconda3/etc/profile.d/conda.sh\n../ani_cluster_split.py --ani ${i}_ani.tsv --fasta_dir ${i}_split --out_prefix $i">${i}_dataset_split.sh;done

# Run scripts for spliting each dataset by ANI.
cat realm.list|while read i;do sh ${i}_dataset_split.sh;done

#the output files are listed as follows:
archaea_genome_train.fasta
archaea_plasmid_train.fasta
bacteria_genome_train.fasta
bacteria_plasmid_train.fasta
fungi_genome_train.fasta
protist_genome_train.fasta
viral_genome_train.fasta
archaea_genome_val.fasta  archaea_plasmid_val.fasta  bacteria_genome_val.fasta  bacteria_plasmid_val.fasta  fungi_genome_val.fasta  protist_genome_val.fasta  viral_genome_val.fasta
archaea_genome_test.fasta  archaea_plasmid_test.fasta  bacteria_genome_test.fasta  bacteria_plasmid_test.fasta  fungi_genome_test.fasta  protist_genome_test.fasta  viral_genome_test.fasta
