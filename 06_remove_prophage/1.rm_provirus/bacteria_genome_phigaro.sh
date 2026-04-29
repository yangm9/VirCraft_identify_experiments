:<<~
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_genome_train.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_genome_val.fasta
ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_genome_test.fasta

source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-Phigaro
#Removing prophages with phigaro
phigaro -f bacteria_genome_train.fasta -e bed -o bacteria_genome_train_phigaro -t 32 -d 
phigaro -f bacteria_genome_val.fasta -e bed -o bacteria_genome_val_phigaro -t 32 -d 
phigaro -f bacteria_genome_test.fasta -e bed -o bacteria_genome_test_phigaro -t 32 -d 
~

# Index fasta file
source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-General
samtools faidx bacteria_genome_train.fasta
samtools faidx bacteria_genome_val.fasta
samtools faidx bacteria_genome_test.fasta

# Create genomeFile
awk -v OFS='\t' {'print $1,$2'} bacteria_genome_train.fasta.fai | sort > bacteria_genome_train_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} bacteria_genome_val.fasta.fai | sort > bacteria_genome_val_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} bacteria_genome_test.fasta.fai | sort > bacteria_genome_test_phigaro_genomeFile.txt

# Sort bed file by genomeFile
bedtools sort -faidx bacteria_genome_train_phigaro_genomeFile.txt -i bacteria_genome_train_phigaro/bacteria_genome_train.phigaro.bed > bacteria_genome_train.phigaro_sorted.bed
bedtools sort -faidx bacteria_genome_val_phigaro_genomeFile.txt -i bacteria_genome_val_phigaro/bacteria_genome_val.phigaro.bed > bacteria_genome_val.phigaro_sorted.bed
bedtools sort -faidx bacteria_genome_test_phigaro_genomeFile.txt -i bacteria_genome_test_phigaro/bacteria_genome_test.phigaro.bed > bacteria_genome_test.phigaro_sorted.bed

# Create a bed file of phigaro non prophage regions
bedtools complement -i bacteria_genome_train.phigaro_sorted.bed -g bacteria_genome_train_phigaro_genomeFile.txt > bacteria_genome_train_phigaro_bedtools_complement.bed
bedtools complement -i bacteria_genome_val.phigaro_sorted.bed -g bacteria_genome_val_phigaro_genomeFile.txt > bacteria_genome_val_phigaro_bedtools_complement.bed
bedtools complement -i bacteria_genome_test.phigaro_sorted.bed -g bacteria_genome_test_phigaro_genomeFile.txt > bacteria_genome_test_phigaro_bedtools_complement.bed

# Get non prophage (archaea/archaea chromosome/plasmid) fasta file
bedtools getfasta -fi bacteria_genome_train.fasta -bed bacteria_genome_train_phigaro_bedtools_complement.bed -fo bacteria_genome_train.phigaro.fasta
bedtools getfasta -fi bacteria_genome_val.fasta -bed bacteria_genome_val_phigaro_bedtools_complement.bed -fo bacteria_genome_val.phigaro.fasta
bedtools getfasta -fi bacteria_genome_test.fasta -bed bacteria_genome_test_phigaro_bedtools_complement.bed -fo bacteria_genome_test.phigaro.fasta

