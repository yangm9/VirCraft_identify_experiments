# 01 Prepare ftp links
wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/viral/assembly_summary.txt -O viral_assembly_summary.txt
awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date < 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' viral_assembly_summary.txt > viral_assembly_summary_pre20210723.refseq.txt
awk -F"\t" '{print $20}' viral_assembly_summary_pre20210723.refseq.txt > viral_assembly_summary_pre20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' viral_assembly_summary_pre20210723_ftplinks.txt > viral_assembly_summary_pre20210723_ftplinks.txt1
mv viral_assembly_summary_pre20210723_ftplinks.txt1 viral_assembly_summary_pre20210723_ftplinks.txt

awk -F'\t' '{
    split($15, d, "-");
    date = d[1] d[2] d[3];
    if (date >= 20210724 && ($12=="Complete Genome" || $12=="Chromosome")) print
}' viral_assembly_summary.txt > viral_assembly_summary_post20210723.refseq.txt
awk -F"\t" '{print $20}' viral_assembly_summary_post20210723.refseq.txt > viral_assembly_summary_post20210723_ftplinks.txt
awk 'BEGIN{FS=OFS="/"; filesuffix="genomic.fna.gz"} {
    ftpdir=$0;
    asm=$10;
    file=asm"_"filesuffix;
    print ftpdir, file
}' viral_assembly_summary_post20210723_ftplinks.txt > viral_assembly_summary_post20210723_ftplinks.txt1
mv viral_assembly_summary_post20210723_ftplinks.txt1 viral_assembly_summary_post20210723_ftplinks.txt

# 02 Download refseqs
mkdir viral_assembly_pre20210723
cd viral_assembly_pre20210723
parallel -j 64 wget < ../viral_assembly_summary_pre20210723_ftplinks.txt
cd -
mkdir viral_assembly_post20210723
cd viral_assembly_post20210723
parallel -j 64 wget < ../viral_assembly_summary_post20210723_ftplinks.txt
cd -

# 并行处理，加快速度
find viral_assembly_pre20210723 -name "*.gz" -type f | parallel zcat {} >> viral_assembly_pre20210723_complete.fna
find viral_assembly_post20210723 -name "*.gz" -type f | parallel zcat {} >> viral_assembly_post20210723_complete.fna
