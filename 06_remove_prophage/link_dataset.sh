cat ../1.rm_provirus/archaea_plasmid_test.phigaro.phageboost.fasta ../1.rm_provirus/bacteria_plasmid_test.phigaro.phageboost.fasta >plasmid_test.fasta
cat ../1.rm_provirus/archaea_plasmid_train.phigaro.phageboost.fasta ../1.rm_provirus/bacteria_plasmid_train.phigaro.phageboost.fasta >plasmid_train.fasta
cat ../1.rm_provirus/archaea_plasmid_val.phigaro.phageboost.fasta ../1.rm_provirus/bacteria_plasmid_val.phigaro.phageboost.fasta >plasmid_val.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/fungi_genome_test.fasta
ln -s ../../2-2.subsampling_rm_training/2.subsampling/fungi_genome_train_sub150_longest.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/fungi_genome_val.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/protist_genome_test.fasta
ln -s ../../2-2.subsampling_rm_training/2.subsampling/protist_genome_train_sub250_longest.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/protist_genome_val.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/viral_genome_test.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/viral_genome_train.fasta
ln -s ../../2-2.subsampling_rm_training/1.tran_val_test/viral_genome_val.fasta
