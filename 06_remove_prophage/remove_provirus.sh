#!/bin/bash

# Master control script: Integrated phigaro + phageboost pipeline
# All phigaro steps will be executed (ignore commented out sections in original)

# Define data types and categories
CATEGORIES=("archaea_genome" "archaea_plasmid" "bacteria_genome" "bacteria_plasmid")
DATASETS=("train" "val" "test")

# Software paths
PHIGARO_THREADS=32
PHAGEBOOST_THREADS=16

source $CONDA_BASE

# Function: Run phigaro pipeline for all categories and datasets
run_phigaro() {
    local category=$1
    local type=$2
    
    echo "[Phigaro] Processing: $category - $type"
    
    # Create symbolic link if needed
    if [ ! -f ${category}_${type}.fasta ]; then
        ln -s ../2-2.subsampling_rm_training/1.tran_val_test/${category}_${type}.fasta
    fi
    
    # Run phigaro for all cases
    phigaro -f ${category}_${type}.fasta -e bed -o ${category}_${type}_phigaro -t $PHIGARO_THREADS -d
    
    # Index fasta file
    samtools faidx ${category}_${type}.fasta
    
    # Create genomeFile
    awk -v OFS='\t' '{print $1,$2}' ${category}_${type}.fasta.fai | sort > ${category}_${type}_phigaro_genomeFile.txt
    
    # Sort bed file by genomeFile
    bedtools sort -faidx ${category}_${type}_phigaro_genomeFile.txt \
        -i ${category}_${type}_phigaro/${category}_${type}.phigaro.bed \
        > ${category}_${type}.phigaro_sorted.bed
    
    # Create bed file of non-prophage regions
    bedtools complement -i ${category}_${type}.phigaro_sorted.bed \
        -g ${category}_${type}_phigaro_genomeFile.txt \
        > ${category}_${type}_phigaro_bedtools_complement.bed
    
    # Extract non-prophage sequences
    bedtools getfasta -fi ${category}_${type}.fasta \
        -bed ${category}_${type}_phigaro_bedtools_complement.bed \
        -fo ${category}_${type}.phigaro.fasta
    
    echo "[Phigaro] Completed: $category - $type\n"
}

# Function: Run phageboost pipeline
run_phageboost() {
    local category=$1
    local type=$2
    
    echo "[PhageBoost] Processing: $category - $type"
    
    INPUT_FASTA="${category}_${type}.phigaro.fasta"
    WORK_DIR="${category}_${type}_phageboost"
    
    # Set thread count based on original script
    # bacteria_genome uses 128, others use 16 or 32
    local threads=$PHAGEBOOST_THREADS
    if [[ "$category" == "bacteria_genome" ]]; then
        threads=128
    fi
    
    # Create and enter working directory
    mkdir -p ${WORK_DIR}/splited
    
    # Clean headers (replace colon with underscore)
    sed 's/:/_/g' ${INPUT_FASTA} > ${WORK_DIR}/${INPUT_FASTA}
    
    cd ${WORK_DIR}
    
    # Split fasta file
    faidx --split-files ${INPUT_FASTA}
    
    # Organize files
    mv *.fasta splited/
    mv splited/${INPUT_FASTA} . 2>/dev/null || true
    
    # Run PhageBoost on individual contigs
    cd splited
    ls *.fasta 2>/dev/null | grep -v "${INPUT_FASTA}" | parallel -j $threads "PhageBoost -f {} -o {}_pb"
    
    # Merge results
    cd ..
    if ls splited/*_pb/*.fasta 1>/dev/null 2>&1; then
        cat splited/*_pb/*.fasta > ${type}.pb-calls.fasta
    else
        echo "[PhageBoost] WARNING: No PhageBoost output files found"
        touch ${type}.pb-calls.fasta
    fi
    
    # Mapping and format conversion
    minimap2 -x asm5 -a --secondary=no -o ${type}.aln.sam ${INPUT_FASTA} ${type}.pb-calls.fasta
    samtools view -Sb ${type}.aln.sam > ${type}.aln.bam
    bamToBed -i ${type}.aln.bam > ${type}.aln.bed
    sort -k1,1 -k2,2n ${type}.aln.bed > ${type}.aln.sorted.bed
    
    # Generate genome index
    samtools faidx ${INPUT_FASTA}
    awk -v OFS='\t' '{print $1,$2}' ${INPUT_FASTA}.fai | sort > ${type}_genomeFile.txt
    
    # Extract complement regions
    bedtools complement -i ${type}.aln.sorted.bed -g ${type}_genomeFile.txt > ${type}.complement.bed
    
    # Extract final fasta and save to parent directory
    bedtools getfasta -fi ${INPUT_FASTA} -bed ${type}.complement.bed \
        -fo ../${category}_${type}.phigaro.phageboost.fasta
    
    cd ..
    
    echo "[PhageBoost] Completed: $category - $type\n"
}

# Main pipeline

echo "Starting complete pipeline"
echo "All phigaro steps will be executed"

# Option to skip phigaro (if already completed)
# Usage: ./main_script.sh skip_phigaro
SKIP_PHIGARO=${1:-false}

for category in "${CATEGORIES[@]}"; do
    for type in "${DATASETS[@]}"; do
        if [ "$SKIP_PHIGARO" != "skip_phigaro" ]; then
            run_phigaro "$category" "$type"
        fi
        run_phageboost "$category" "$type"
    done
done

echo "All tasks completed!"
