# 01 Prepare ftp links
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt -O bacteria_assembly_summary.txt
awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' bacteria_assembly_summary.txt > bacteria_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' bacteria_assembly_summary_pre20210723.refseq.txt > bacteria_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' bacteria_assembly_summary_pre20210723_ftplinks.txt > bacteria_assembly_summary_pre20210723_ftplinks.txt1
mv bacteria_assembly_summary_pre20210723_ftplinks.txt1 bacteria_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' bacteria_assembly_summary.txt > bacteria_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' bacteria_assembly_summary_post20210723.refseq.txt > bacteria_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' bacteria_assembly_summary_post20210723_ftplinks.txt > bacteria_assembly_summary_post20210723_ftplinks.txt1
mv bacteria_assembly_summary_post20210723_ftplinks.txt1 bacteria_assembly_summary_post20210723_ftplinks.txt

# 02 Download refseqs
mkdir bacteria_assembly_pre20210723
cd bacteria_assembly_pre20210723
parallel -j 64 wget < ../bacteria_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir bacteria_assembly_post20210723
cd bacteria_assembly_post20210723
parallel -j 64 wget < ../bacteria_assembly_summary_post20210723_ftplinks.txt
cd -

# Parallel processing to speed up
find bacteria_assembly_pre20210723 -name "*.gz" -type f | parallel zcat {} >> bacteria_assembly_pre20210723_complete.fna
find bacteria_assembly_post20210723 -name "*.gz" -type f | parallel zcat {} >> bacteria_assembly_post20210723_complete.fna

sed -i 's/ /~/g' bacteria_assembly_pre20210723_complete.fna
sed -i 's/ /~/g' bacteria_assembly_post20210723_complete.fna

sed -i "s/'//g" bacteria_assembly_pre20210723_complete.fna
sed -i "s/'//g" bacteria_assembly_post20210723_complete.fna

grep '>' bacteria_assembly_pre20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >bacteria_plasmid_pre20210723_names.list
grep '>' bacteria_assembly_post20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >bacteria_plasmid_post20210723_names.list

grep '>' bacteria_assembly_pre20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >bacteria_genome_pre20210723_names.list
grep '>' bacteria_assembly_post20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >bacteria_genome_post20210723_names.list

../bin/extrSeqByName.pl bacteria_plasmid_pre20210723_names.list bacteria_assembly_pre20210723_complete.fna bacteria_plasmid_pre20210723_complete.fna
../bin/extrSeqByName.pl bacteria_plasmid_post20210723_names.list bacteria_assembly_post20210723_complete.fna bacteria_plasmid_post20210723_complete.fna

../bin/extrSeqByName.pl bacteria_genome_pre20210723_names.list bacteria_assembly_pre20210723_complete.fna bacteria_genome_pre20210723_complete.fna
../bin/extrSeqByName.pl bacteria_genome_post20210723_names.list bacteria_assembly_post20210723_complete.fna bacteria_genome_post20210723_complete.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' bacteria_plasmid_pre20210723_complete.fna >bacteria_plasmid_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' bacteria_plasmid_post20210723_complete.fna >bacteria_plasmid_post20210723_complete_id.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' bacteria_genome_pre20210723_complete.fna >bacteria_genome_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' bacteria_genome_post20210723_complete.fna >bacteria_genome_post20210723_complete_id.fna
!

../bin/SeqLenCutoff.pl bacteria_plasmid_pre20210723_complete_id.fna bacteria_plasmid_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl bacteria_plasmid_post20210723_complete_id.fna bacteria_plasmid_post20210723_complete_id 1500

../bin/SeqLenCutoff.pl bacteria_genome_pre20210723_complete_id.fna bacteria_genome_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl bacteria_genome_post20210723_complete_id.fna bacteria_genome_post20210723_complete_id 1500
