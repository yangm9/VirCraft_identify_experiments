#!/bin/bash

# 定义需要处理的数据集类型
DATASETS=("train" "val" "test")

# 基础软件路径（根据你的环境调整）
MINIMAP2="/data_backup/software/tools/minimap2-2.30_x64-linux/minimap2"
CONDA_BASE="/backup/software/miniconda3/etc/profile.d/conda.sh"

source $CONDA_BASE

for TYPE in "${DATASETS[@]}"; do
    echo "-----------------------------------"
    echo "Processing: $TYPE"
    echo "-----------------------------------"

    # 定义当前处理的文件前缀名
    # 假设你的原始文件命名规则是: archaea_plasmid_train.phigaro.fasta
    INPUT_FASTA="archaea_plasmid_${TYPE}.phigaro.fasta"
    WORK_DIR="archaea_plasmid_${TYPE}_phageboost"
    
    # 1. 创建并进入目录
    mkdir -p ${WORK_DIR}/splited
    
    # 2. 清洗 Header (冒号转下划线)
    # 注意：这里假设原始 fasta 在当前目录的上一级或同级，请确保路径正确
    sed 's/:/_/g' ${INPUT_FASTA} > ${WORK_DIR}/${INPUT_FASTA}
    
    cd ${WORK_DIR}

    # 3. 分割 Fasta
    conda activate VC-General
    faidx --split-files ${INPUT_FASTA}
    
    # 4. 整理文件
    mv *.fasta splited/
    mv splited/${INPUT_FASTA} . # 把处理后的总文件挪回当前目录
    
    # 5. 运行 PhageBoost
    cd splited
    conda activate VC-PhageBoost
    # 仅处理分割出来的单个 contig 文件，排除总文件
    ls *.fasta | grep -v "${INPUT_FASTA}" | parallel -j 16 "PhageBoost -f {} -o {}_pb"
    
    # 6. 回到工作目录并合并结果
    cd ..
    cat splited/*_pb/*.fasta > ${TYPE}.pb-calls.fasta
    
    # 7. 比对与格式转换 (Mapping)
    conda activate VC-General # 确保包含 samtools 和 bedtools
    $MINIMAP2 -x asm5 -a --secondary=no -o ${TYPE}.aln.sam ${INPUT_FASTA} ${TYPE}.pb-calls.fasta
    samtools view -Sb ${TYPE}.aln.sam > ${TYPE}.aln.bam
    bamToBed -i ${TYPE}.aln.bam > ${TYPE}.aln.bed
    sort -k1,1 -k2,2n ${TYPE}.aln.bed > ${TYPE}.aln.sorted.bed
    
    # 8. 生成基因组索引和范围文件
    samtools faidx ${INPUT_FASTA}
    awk -v OFS='\t' '{print $1,$2}' ${INPUT_FASTA}.fai | sort > ${TYPE}_genomeFile.txt
    
    # 9. 提取反选区域 (Complement)
    bedtools complement -i ${TYPE}.aln.sorted.bed -g ${TYPE}_genomeFile.txt > ${TYPE}.complement.bed
    
    # 10. 提取最终 Fasta 并保存到上级目录
    bedtools getfasta -fi ${INPUT_FASTA} -bed ${TYPE}.complement.bed -fo ../archaea_plasmid_${TYPE}.phigaro.phageboost.fasta
    
    # 返回起始目录处理下一个数据集
    cd ..
    
    echo "Finished processing $TYPE"
done

echo "All tasks completed!"
