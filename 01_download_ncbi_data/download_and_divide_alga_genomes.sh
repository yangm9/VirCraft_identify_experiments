# 01 Prepare ftp links
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt -O all_assembly_summary.txt

grep 'Auxenochlorella' all_assembly_summary.txt > alga_assembly_summary.txt
grep 'Ostreococcus' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Bathycoccus' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Chlorella' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Coccomyxa' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Micromonas' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Chlamydomonas' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Volvox' all_assembly_summary.txt >> alga_assembly_summary.txt
grep 'Monoraphidium' all_assembly_summary.txt >> alga_assembly_summary.txt
rm -f all_assembly_summary.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' alga_assembly_summary.txt > alga_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' alga_assembly_summary_pre20210723.refseq.txt > alga_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' alga_assembly_summary_pre20210723_ftplinks.txt > alga_assembly_summary_pre20210723_ftplinks.txt1
mv alga_assembly_summary_pre20210723_ftplinks.txt1 alga_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' alga_assembly_summary.txt > alga_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' alga_assembly_summary_post20210723.refseq.txt > alga_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' alga_assembly_summary_post20210723_ftplinks.txt > alga_assembly_summary_post20210723_ftplinks.txt1
mv alga_assembly_summary_post20210723_ftplinks.txt1 alga_assembly_summary_post20210723_ftplinks.txt



# 02 Download refseqs
mkdir alga_assembly_pre20210723
cd alga_assembly_pre20210723
parallel -j 64 wget < ../alga_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir alga_assembly_post20210723
cd alga_assembly_post20210723
parallel -j 64 wget < ../alga_assembly_summary_post20210723_ftplinks.txt
cd -

# Parallel processing to speed up
find alga_assembly_pre20210723 -name "*.gz" -type f | parallel zcat {} >> alga_assembly_pre20210723_complete.fna
find alga_assembly_post20210723 -name "*.gz" -type f | parallel zcat {} >> alga_assembly_post20210723_complete.fna

sed -i 's/ /~/g' alga_assembly_pre20210723_complete.fna
sed -i 's/ /~/g' alga_assembly_post20210723_complete.fna

sed -i "s/'//g" alga_assembly_pre20210723_complete.fna
sed -i "s/'//g" alga_assembly_post20210723_complete.fna

grep '>' alga_assembly_pre20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >alga_plasmid_pre20210723_names.list
grep '>' alga_assembly_post20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >alga_plasmid_post20210723_names.list

grep '>' alga_assembly_pre20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >alga_genome_pre20210723_names.list
grep '>' alga_assembly_post20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >alga_genome_post20210723_names.list

../bin/extrSeqByName.pl alga_plasmid_pre20210723_names.list alga_assembly_pre20210723_complete.fna alga_plasmid_pre20210723_complete.fna
../bin/extrSeqByName.pl alga_plasmid_post20210723_names.list alga_assembly_post20210723_complete.fna alga_plasmid_post20210723_complete.fna

../bin/extrSeqByName.pl alga_genome_pre20210723_names.list alga_assembly_pre20210723_complete.fna alga_genome_pre20210723_complete.fna
../bin/extrSeqByName.pl alga_genome_post20210723_names.list alga_assembly_post20210723_complete.fna alga_genome_post20210723_complete.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' alga_plasmid_pre20210723_complete.fna >alga_plasmid_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' alga_plasmid_post20210723_complete.fna >alga_plasmid_post20210723_complete_id.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' alga_genome_pre20210723_complete.fna >alga_genome_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' alga_genome_post20210723_complete.fna >alga_genome_post20210723_complete_id.fna

../bin/SeqLenCutoff.pl alga_plasmid_pre20210723_complete_id.fna alga_plasmid_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl alga_plasmid_post20210723_complete_id.fna alga_plasmid_post20210723_complete_id 1500

../bin/SeqLenCutoff.pl alga_genome_pre20210723_complete_id.fna alga_genome_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl alga_genome_post20210723_complete_id.fna alga_genome_post20210723_complete_id 1500
