ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_plasmid_train.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_plasmid_val.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_plasmid_test.fasta


source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-Phigaro
#Removing prophages with phigaro
phigaro -f archaea_plasmid_train.fasta -e bed -o archaea_plasmid_train_phigaro -t 32 -d 
phigaro -f archaea_plasmid_val.fasta -e bed -o archaea_plasmid_val_phigaro -t 32 -d 
phigaro -f archaea_plasmid_test.fasta -e bed -o archaea_plasmid_test_phigaro -t 32 -d 

# Index fasta file
samtools faidx archaea_plasmid_train.fasta
samtools faidx archaea_plasmid_val.fasta
samtools faidx archaea_plasmid_test.fasta

# Create genomeFile
conda activate VC-General
awk -v OFS='\t' {'print $1,$2'} archaea_plasmid_train.fasta.fai | sort > archaea_plasmid_train_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} archaea_plasmid_val.fasta.fai | sort > archaea_plasmid_val_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} archaea_plasmid_test.fasta.fai | sort > archaea_plasmid_test_phigaro_genomeFile.txt

# Sort bed file by genomeFile
bedtools sort -faidx archaea_plasmid_train_phigaro_genomeFile.txt -i archaea_plasmid_train_phigaro/archaea_plasmid_train.phigaro.bed > archaea_plasmid_train.phigaro_sorted.bed
bedtools sort -faidx archaea_plasmid_val_phigaro_genomeFile.txt -i archaea_plasmid_val_phigaro/archaea_plasmid_val.phigaro.bed > archaea_plasmid_val.phigaro_sorted.bed
bedtools sort -faidx archaea_plasmid_test_phigaro_genomeFile.txt -i archaea_plasmid_test_phigaro/archaea_plasmid_test.phigaro.bed > archaea_plasmid_test.phigaro_sorted.bed

# Create a bed file of phigaro non prophage regions
bedtools complement -i archaea_plasmid_train.phigaro_sorted.bed -g archaea_plasmid_train_phigaro_genomeFile.txt > archaea_plasmid_train_phigaro_bedtools_complement.bed
bedtools complement -i archaea_plasmid_val.phigaro_sorted.bed -g archaea_plasmid_val_phigaro_genomeFile.txt > archaea_plasmid_val_phigaro_bedtools_complement.bed
bedtools complement -i archaea_plasmid_test.phigaro_sorted.bed -g archaea_plasmid_test_phigaro_genomeFile.txt > archaea_plasmid_test_phigaro_bedtools_complement.bed

# Get non prophage (archaea/archaea chromosome/plasmid) fasta file
bedtools getfasta -fi archaea_plasmid_train.fasta -bed archaea_plasmid_train_phigaro_bedtools_complement.bed -fo archaea_plasmid_train.phigaro.fasta
bedtools getfasta -fi archaea_plasmid_val.fasta -bed archaea_plasmid_val_phigaro_bedtools_complement.bed -fo archaea_plasmid_val.phigaro.fasta
bedtools getfasta -fi archaea_plasmid_test.fasta -bed archaea_plasmid_test_phigaro_bedtools_complement.bed -fo archaea_plasmid_test.phigaro.fasta

