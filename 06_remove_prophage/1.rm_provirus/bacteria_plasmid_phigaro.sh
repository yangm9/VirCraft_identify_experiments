#ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_plasmid_train.fasta
#ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_plasmid_val.fasta
#ln -s ../2-2.subsampling_rm_training/1.tran_val_test/bacteria_plasmid_test.fasta

source /backup/software/miniconda3/etc/profile.d/conda.sh
conda activate VC-Phigaro
#Removing prophages with phigaro
#phigaro -f bacteria_plasmid_train.fasta -e bed -o bacteria_plasmid_train_phigaro -t 32 -d 
phigaro -f bacteria_plasmid_val.fasta -e bed -o bacteria_plasmid_val_phigaro -t 32 -d 
phigaro -f bacteria_plasmid_test.fasta -e bed -o bacteria_plasmid_test_phigaro -t 32 -d 

# Index fasta file
samtools faidx bacteria_plasmid_train.fasta
samtools faidx bacteria_plasmid_val.fasta
samtools faidx bacteria_plasmid_test.fasta

# Create genomeFile
conda activate VC-General
awk -v OFS='\t' {'print $1,$2'} bacteria_plasmid_train.fasta.fai | sort > bacteria_plasmid_train_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} bacteria_plasmid_val.fasta.fai | sort > bacteria_plasmid_val_phigaro_genomeFile.txt
awk -v OFS='\t' {'print $1,$2'} bacteria_plasmid_test.fasta.fai | sort > bacteria_plasmid_test_phigaro_genomeFile.txt

# Sort bed file by genomeFile
bedtools sort -faidx bacteria_plasmid_train_phigaro_genomeFile.txt -i bacteria_plasmid_train_phigaro/bacteria_plasmid_train.phigaro.bed > bacteria_plasmid_train.phigaro_sorted.bed
bedtools sort -faidx bacteria_plasmid_val_phigaro_genomeFile.txt -i bacteria_plasmid_val_phigaro/bacteria_plasmid_val.phigaro.bed > bacteria_plasmid_val.phigaro_sorted.bed
bedtools sort -faidx bacteria_plasmid_test_phigaro_genomeFile.txt -i bacteria_plasmid_test_phigaro/bacteria_plasmid_test.phigaro.bed > bacteria_plasmid_test.phigaro_sorted.bed

# Create a bed file of phigaro non prophage regions
bedtools complement -i bacteria_plasmid_train.phigaro_sorted.bed -g bacteria_plasmid_train_phigaro_genomeFile.txt > bacteria_plasmid_train_phigaro_bedtools_complement.bed
bedtools complement -i bacteria_plasmid_val.phigaro_sorted.bed -g bacteria_plasmid_val_phigaro_genomeFile.txt > bacteria_plasmid_val_phigaro_bedtools_complement.bed
bedtools complement -i bacteria_plasmid_test.phigaro_sorted.bed -g bacteria_plasmid_test_phigaro_genomeFile.txt > bacteria_plasmid_test_phigaro_bedtools_complement.bed

# Get non prophage (archaea/archaea chromosome/plasmid) fasta file
bedtools getfasta -fi bacteria_plasmid_train.fasta -bed bacteria_plasmid_train_phigaro_bedtools_complement.bed -fo bacteria_plasmid_train.phigaro.fasta
bedtools getfasta -fi bacteria_plasmid_val.fasta -bed bacteria_plasmid_val_phigaro_bedtools_complement.bed -fo bacteria_plasmid_val.phigaro.fasta
bedtools getfasta -fi bacteria_plasmid_test.fasta -bed bacteria_plasmid_test_phigaro_bedtools_complement.bed -fo bacteria_plasmid_test.phigaro.fasta

