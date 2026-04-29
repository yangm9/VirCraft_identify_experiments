# 01 Prepare ftp links
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/fungi/assembly_summary.txt -O fungi_assembly_summary.txt
awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' fungi_assembly_summary.txt > fungi_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' fungi_assembly_summary_pre20210723.refseq.txt > fungi_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' fungi_assembly_summary_pre20210723_ftplinks.txt > fungi_assembly_summary_pre20210723_ftplinks.txt1
mv fungi_assembly_summary_pre20210723_ftplinks.txt1 fungi_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' fungi_assembly_summary.txt > fungi_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' fungi_assembly_summary_post20210723.refseq.txt > fungi_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' fungi_assembly_summary_post20210723_ftplinks.txt > fungi_assembly_summary_post20210723_ftplinks.txt1
mv fungi_assembly_summary_post20210723_ftplinks.txt1 fungi_assembly_summary_post20210723_ftplinks.txt

# 02 Download refseqs
mkdir fungi_assembly_pre20210723
cd fungi_assembly_pre20210723
parallel -j 64 wget < ../fungi_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir fungi_assembly_post20210723
cd fungi_assembly_post20210723
parallel -j 64 wget < ../fungi_assembly_summary_post20210723_ftplinks.txt
cd -

# Parallel processing to speed up
find fungi_assembly_pre20210723 -name "*.gz" -type f | parallel zcat {} >> fungi_assembly_pre20210723_complete.fna
find fungi_assembly_post20210723 -name "*.gz" -type f | parallel zcat {} >> fungi_assembly_post20210723_complete.fna

sed -i 's/ /~/g' fungi_assembly_pre20210723_complete.fna
sed -i 's/ /~/g' fungi_assembly_post20210723_complete.fna

sed -i "s/'//g" fungi_assembly_pre20210723_complete.fna
sed -i "s/'//g" fungi_assembly_post20210723_complete.fna

grep '>' fungi_assembly_pre20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >fungi_plasmid_pre20210723_names.list
grep '>' fungi_assembly_post20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >fungi_plasmid_post20210723_names.list

grep '>' fungi_assembly_pre20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >fungi_genome_pre20210723_names.list
grep '>' fungi_assembly_post20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >fungi_genome_post20210723_names.list

../bin/extrSeqByName.pl fungi_plasmid_pre20210723_names.list fungi_assembly_pre20210723_complete.fna fungi_plasmid_pre20210723_complete.fna
../bin/extrSeqByName.pl fungi_plasmid_post20210723_names.list fungi_assembly_post20210723_complete.fna fungi_plasmid_post20210723_complete.fna

../bin/extrSeqByName.pl fungi_genome_pre20210723_names.list fungi_assembly_pre20210723_complete.fna fungi_genome_pre20210723_complete.fna
../bin/extrSeqByName.pl fungi_genome_post20210723_names.list fungi_assembly_post20210723_complete.fna fungi_genome_post20210723_complete.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' fungi_plasmid_pre20210723_complete.fna >fungi_plasmid_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' fungi_plasmid_post20210723_complete.fna >fungi_plasmid_post20210723_complete_id.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' fungi_genome_pre20210723_complete.fna >fungi_genome_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' fungi_genome_post20210723_complete.fna >fungi_genome_post20210723_complete_id.fna

../bin/SeqLenCutoff.pl fungi_plasmid_pre20210723_complete_id.fna fungi_plasmid_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl fungi_plasmid_post20210723_complete_id.fna fungi_plasmid_post20210723_complete_id 1500

../bin/SeqLenCutoff.pl fungi_genome_pre20210723_complete_id.fna fungi_genome_pre20210723_complete_id 1500
../bin/SeqLenCutoff.pl fungi_genome_post20210723_complete_id.fna fungi_genome_post20210723_complete_id 1500
