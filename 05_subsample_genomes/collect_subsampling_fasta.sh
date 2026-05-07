mkdir fa
cat ../04_split_dataset/archaea_plasmid_test.fasta ../04_split_dataset/bacteria_plasmid_test.fasta >fa/prokaryote_plasmid_test.fasta
cat ../04_split_dataset/archaea_plasmid_val.fasta ../04_split_dataset/bacteria_plasmid_val.fasta >fa/prokaryote_plasmid_val.fasta
cat ../04_split_dataset/archaea_plasmid_train.fasta ../04_split_dataset/bacteria_plasmid_train.fasta >fa/prokaryote_plasmid_train.fasta

for prefix in archaea bacteria fungi protist viral; do
    ln -s "../04_split_dataset/${prefix}_genome_train.fasta" "fa/${prefix}_genome_train.fasta"
    ln -s "../04_split_dataset/${prefix}_genome_val.fasta" "fa/${prefix}_genome_val.fasta"
    ln -s "../04_split_dataset/${prefix}_genome_test.fasta" "fa/${prefix}_genome_test.fasta"
done

ln -s ../04_split_dataset/bacteria/fastani_output bacteria_genus_ani
python ani_subsampling_for_bacteria_train_longest_by_genus.py
python final_plasmid_sampler_tr245_va95_te91.py
python filter_each_eukaryote_train_longest.py
python plasmid_train_ani_subsampling_249.py
