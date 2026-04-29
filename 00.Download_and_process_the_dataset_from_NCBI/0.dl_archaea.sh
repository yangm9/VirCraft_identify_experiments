# 01 Prepare ftp links
#wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/archaea/assembly_summary.txt -O archaea_assembly_summary.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' archaea_assembly_summary.txt > archaea_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' archaea_assembly_summary_pre20210723.refseq.txt > archaea_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' archaea_assembly_summary_pre20210723_ftplinks.txt > archaea_assembly_summary_pre20210723_ftplinks.txt1
mv archaea_assembly_summary_pre20210723_ftplinks.txt1 archaea_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' archaea_assembly_summary.txt > archaea_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' archaea_assembly_summary_post20210723.refseq.txt > archaea_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' archaea_assembly_summary_post20210723_ftplinks.txt > archaea_assembly_summary_post20210723_ftplinks.txt1
mv archaea_assembly_summary_post20210723_ftplinks.txt1 archaea_assembly_summary_post20210723_ftplinks.txt

# 02 Download refseqs
mkdir archaea_assembly_pre20210723
cd archaea_assembly_pre20210723
parallel -j 20 wget < ../archaea_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir archaea_assembly_post20210723
cd archaea_assembly_post20210723
parallel -j 20 wget < ../archaea_assembly_summary_post20210723_ftplinks.txt
cd -

zcat archaea_assembly_pre20210723/*.gz >archaea_assembly_pre20210723_complete.fna
zcat archaea_assembly_post20210723/*.gz >archaea_assembly_post20210723_complete.fna

sed -i 's/ /~/g' archaea_assembly_pre20210723_complete.fna
sed -i 's/ /~/g' archaea_assembly_post20210723_complete.fna

sed -i "s/'//g" archaea_assembly_pre20210723_complete.fna
sed -i "s/'//g" archaea_assembly_post20210723_complete.fna

grep '>' archaea_assembly_pre20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >archaea_plasmid_pre20210723_names.list
grep '>' archaea_assembly_post20210723_complete.fna|sed 's/^>//'|grep 'plasmid' >archaea_plasmid_post20210723_names.list

grep '>' archaea_assembly_pre20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >archaea_genome_pre20210723_names.list
grep '>' archaea_assembly_post20210723_complete.fna|sed 's/^>//'|grep -v 'plasmid' >archaea_genome_post20210723_names.list

../bin/extrSeqByName.pl archaea_plasmid_pre20210723_names.list archaea_assembly_pre20210723_complete.fna archaea_plasmid_pre20210723_complete.fna
../bin/extrSeqByName.pl archaea_plasmid_post20210723_names.list archaea_assembly_post20210723_complete.fna archaea_plasmid_post20210723_complete.fna

../bin/extrSeqByName.pl archaea_genome_pre20210723_names.list archaea_assembly_pre20210723_complete.fna archaea_genome_pre20210723_complete.fna
../bin/extrSeqByName.pl archaea_genome_post20210723_names.list archaea_assembly_post20210723_complete.fna archaea_genome_post20210723_complete.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' archaea_plasmid_pre20210723_complete.fna >archaea_plasmid_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' archaea_plasmid_post20210723_complete.fna >archaea_plasmid_post20210723_complete_id.fna

perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' archaea_genome_pre20210723_complete.fna >archaea_genome_pre20210723_complete_id.fna
perl -ne 'chomp;if(/^>/){$_=(split/~/,$_)[0];print "$_\n";}else{print "$_\n";}' archaea_genome_post20210723_complete.fna >archaea_genome_post20210723_complete_id.fna

../bin/SeqLenCutoff.pl archaea_genome_post20210723_complete_id.fna archaea_genome_post20210723_complete_id 1500
