# collect and process VirSorter2 training data
#Download all VirSorter2 database from https://zenodo.org/api/records/4297575 as 4297575.zip, and upload it to server.
cd 4297575 
tar xzf non-refseq-genomes.tgz
find non-refseq-genomes -name "*.fna.gz" -exec zcat {} + > vs2_virus_train.fasta
gunzip nonviral-common-random-fragments.ftr.gz
../../bin/download_vs2_sequence.pl nonviral-common-random-fragments.ftr nonviral_genomes 32
find nonviral_genomes -name "*.fasta" -exec cat {} + > vs2_host_train.fasta

# collect and process VIBRANT training data
# Training sequence ID list, including prokaryotes.list and viruses.list were extracted from Supplementary Table 8. Normalized data used to train the neural network machine learning classifier (10.1186/s40168-020-00867-0)
mkdir vb_host
cat vb_host.list|while read i;do efetch -db nucleotide -format fasta -id $i > vb_host/$i.fasta;done
find vb_host -name "*.fasta" -exec cat {} + > vb_host_train.fasta

mkdir vb_virus
cat vb_virus.list|while read i;do efetch -db nucleotide -format fasta -id $i > vb_virus/$i.fasta;done
find vb_virus -name "*.fasta" -exec cat {} + > vb_virus_train.fasta

# collect and process DeepVirFinder training data
# DeepVirFinder and VirFinder share the same training dataset derived from NCBI RefSeq, as detailed in Additional file 2: Table S2 (10.1186/s40168-017-0283-5). Accordingly, we used the sequence IDs (dvf_host.list and dvf_virus.list) from this table to construct the DeepVirFinder training dataset.
mkdir dvf_host
cat dvf_host.list|while read i;do efetch -db nucleotide -format fasta -id $i > dvf_host/$i.fasta;done
find dvf_host -name "*.fasta" -exec cat {} + > dvf_host_train.fasta

mkdir dvf_virus
cat dvf_virus.list|while read i;do efetch -db nucleotide -format fasta -id $i > dvf_virus/$i.fasta;done
find dvf_virus -name "*.fasta" -exec cat {} + > dvf_virus_train.fasta

# collect and process geNomad training data
# The geNomad training data (genomad_supplementary_data_code.zip) were downloaded from https://zenodo.org/records/8049246.
unzip genomad_supplementary_data_code.zip
# split training data (reference_sequences.fna) to gn_prokaryote_train.fasta gn_plasmid_train.fasta gn_euk_train.fasta and gn_virus_train.fasta
python split_genomad_training_fasta_by_domain.py
cat gn_prokaryote_train.fasta gn_plasmid_train.fasta gn_euk_train.fasta > gn_host_train.fasta
# gn_virus_train.fasta

cat vs2_host_train.fasta vb_host_train.fasta dvf_host_train.fasta gn_host_train.fasta > vs2-vb-dvf-gn_host.raw.fasta
cat vs2_virus_train.fasta vb_virus_train.fasta dvf_virus_train.fasta gn_virus_train.fasta > vs2-vb-dvf-gn_virus.raw.fasta

# Removing dupes from within datasets
dedupe.sh -Xmx80G in=vs2-vb-dvf-gn_host.raw.fasta out=vs2-vb-dvf-gn_host.fasta ac=f
dedupe.sh -Xmx80G in=vs2-vb-dvf-gn_virus.raw.fasta out=vs2-vb-dvf-gn_virus.fasta ac=f
