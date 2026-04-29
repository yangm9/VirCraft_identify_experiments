# 01 Prepare ftp links
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/protozoa/assembly_summary.txt -O protozoa_assembly_summary.txt
awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' protozoa_assembly_summary.txt > protozoa_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' protozoa_assembly_summary_pre20210723.refseq.txt > protozoa_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' protozoa_assembly_summary_pre20210723_ftplinks.txt > protozoa_assembly_summary_pre20210723_ftplinks.txt1
mv protozoa_assembly_summary_pre20210723_ftplinks.txt1 protozoa_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' protozoa_assembly_summary.txt > protozoa_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' protozoa_assembly_summary_post20210723.refseq.txt > protozoa_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' protozoa_assembly_summary_post20210723_ftplinks.txt > protozoa_assembly_summary_post20210723_ftplinks.txt1
mv protozoa_assembly_summary_post20210723_ftplinks.txt1 protozoa_assembly_summary_post20210723_ftplinks.txt



# 02 Download refseqs
mkdir protozoa_assembly_pre20210723
cd protozoa_assembly_pre20210723
parallel -j 64 wget < ../protozoa_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir protozoa_assembly_post20210723
cd protozoa_assembly_post20210723
parallel -j 64 wget < ../protozoa_assembly_summary_post20210723_ftplinks.txt
cd -

# Parallel processing to speed up
find protozoa_assembly_pre20210723 -name "*.gz" -type f | parallel zcat {} >> protozoa_assembly_pre20210723_complete.fna
find protozoa_assembly_post20210723 -name "*.gz" -type f | parallel zcat {} >> protozoa_assembly_post20210723_complete.fna

sed -i 's/ /~/g' protozoa_assembly_pre20210723_complete.fna
sed -i 's/ /~/g' protozoa_assembly_post20210723_complete.fna

sed -i "s/'//g" protozoa_assembly_pre20210723_complete.fna
sed -i "s/'//g" protozoa_assembly_post20210723_complete.fna

grep '>' protozoa_assembly_pre20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >protozoa_plasmid_pre20210723_names.list
grep '>' protozoa_assembly_post20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >protozoa_plasmid_post20210723_names.list

grep '>' protozoa_assembly_pre20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >protozoa_genome_pre20210723_names.list
grep '>' protozoa_assembly_post20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >protozoa_genome_post20210723_names.list

../bin/extrSeqByName.pl protozoa_plasmid_pre20210723_names.list protozoa_assembly_pre20210723_complete.fna protozoa_plasmid_pre20210723_complete.fna
../bin/extrSeqByName.pl protozoa_plasmid_post20210723_names.list protozoa_assembly_post20210723_complete.fna protozoa_plasmid_post20210723_complete.fna

../bin/extrSeqByName.pl protozoa_genome_pre20210723_names.list protozoa_assembly_pre20210723_complete.fna protozoa_genome_pre20210723_complete.fna
../bin/extrSeqByName.pl protozoa_genome_post20210723_names.list protozoa_assembly_post20210723_complete.fna protozoa_genome_post20210723_complete.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' protozoa_plasmid_pre20210723_complete.fna >protozoa_plasmid_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' protozoa_plasmid_post20210723_complete.fna >protozoa_plasmid_post20210723_complete_id.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' protozoa_genome_pre20210723_complete.fna >protozoa_genome_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' protozoa_genome_post20210723_complete.fna >protozoa_genome_post20210723_complete_id.fna

../bin/SeqLenCutoff.pl protozoa_plasmid_pre20210723_complete_id.fna protozoa_plasmid_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl protozoa_plasmid_post20210723_complete_id.fna protozoa_plasmid_post20210723_complete_id 1500

../bin/SeqLenCutoff.pl protozoa_genome_pre20210723_complete_id.fna protozoa_genome_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl protozoa_genome_post20210723_complete_id.fna protozoa_genome_post20210723_complete_id 1500
