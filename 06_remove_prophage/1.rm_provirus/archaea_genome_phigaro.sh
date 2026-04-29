:<<!
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_genome_train.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_genome_val.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/archaea_genome_test.fasta

source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-Phigaro
#Removing prophages with phigaro
phigaro -f archaea_genome_train.fasta -e bed -o archaea_genome_train_phigaro -t 32 -d 
!
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-Phigaro
phigaro -f archaea_genome_val.fasta -e bed -o archaea_genome_val_phigaro -t 32 -d 
phigaro -f archaea_genome_test.fasta -e bed -o archaea_genome_test_phigaro -t 32 -d

# Index fasta file
samtools faidx archaea_genome_train.fasta
samtools faidx archaea_genome_val.fasta
samtools faidx archaea_genome_test.fasta

# Create genomeFile
conda activate VC-General
awk -v OFS='\t' {'print $1,$2'} archaea_genome_train.fasta.fai | sort > archaea_genome_train_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} archaea_genome_val.fasta.fai | sort > archaea_genome_val_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} archaea_genome_test.fasta.fai | sort > archaea_genome_test_phigaro_genomeFile.txt

# Sort bed file by genomeFile
bedtools sort -faidx archaea_genome_train_phigaro_genomeFile.txt -i archaea_genome_train_phigaro/archaea_genome_train.phigaro.bed > archaea_genome_train.phigaro_sorted.bed
bedtools sort -faidx archaea_genome_val_phigaro_genomeFile.txt -i archaea_genome_val_phigaro/archaea_genome_val.phigaro.bed > archaea_genome_val.phigaro_sorted.bed
bedtools sort -faidx archaea_genome_test_phigaro_genomeFile.txt -i archaea_genome_test_phigaro/archaea_genome_test.phigaro.bed > archaea_genome_test.phigaro_sorted.bed

# Create a bed file of phigaro non prophage regions
bedtools complement -i archaea_genome_train.phigaro_sorted.bed -g archaea_genome_train_phigaro_genomeFile.txt > archaea_genome_train_phigaro_bedtools_complement.bed
bedtools complement -i archaea_genome_val.phigaro_sorted.bed -g archaea_genome_val_phigaro_genomeFile.txt > archaea_genome_val_phigaro_bedtools_complement.bed
bedtools complement -i archaea_genome_test.phigaro_sorted.bed -g archaea_genome_test_phigaro_genomeFile.txt > archaea_genome_test_phigaro_bedtools_complement.bed

# Get non prophage (archaea/archaea chromosome/plasmid) fasta file
bedtools getfasta -fi archaea_genome_train.fasta -bed archaea_genome_train_phigaro_bedtools_complement.bed -fo archaea_genome_train.phigaro.fasta
bedtools getfasta -fi archaea_genome_val.fasta -bed archaea_genome_val_phigaro_bedtools_complement.bed -fo archaea_genome_val.phigaro.fasta
bedtools getfasta -fi archaea_genome_test.fasta -bed archaea_genome_test_phigaro_bedtools_complement.bed -fo archaea_genome_test.phigaro.fasta

