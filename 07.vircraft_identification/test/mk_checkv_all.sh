#!/bin/bash

# 定义基础路径（方便后续修改）
FASTA_BASE="/backup/yangming/VIRPHA230501MV/vc_test/mock_data/2024-GB-Benchmarking_bioinformatic_virus/4-2.fragment_rm_training/2.subsampling/test/"
IDENTIFY_BASE="/backup/yangming/VIRPHA230501MV/vc_test/mock_data/2024-GB-Benchmarking_bioinformatic_virus/5-3.identify_rm_training_by_len/test/"
CHECKV_DB="/data_backup/database/checkvDB/checkv-db-v1.5"

# 遍历 sample.list 中的每一行
while read -r sample; do
    # 检查样本对应的目录是否存在
    TARGET_DIR="${IDENTIFY_BASE}/${sample}_identify/shell"
    if [ -d "$TARGET_DIR" ]; then
        SCRIPT_NAME="${TARGET_DIR}/${sample}_checkv_ctg.sh"
    # 写入脚本内容
        cat <<EOF > "$SCRIPT_NAME"
source "/backup/software/miniconda3/etc/profile.d/conda.sh" && conda activate && conda activate VC-CheckV && export PATH="/home/yangming/.vc/bin:\$PATH"
checkv end_to_end ${FASTA_BASE}/${sample}.fasta ${IDENTIFY_BASE}/${sample}_identify/work_files/checkv_all -d ${CHECKV_DB} -t 32
EOF
    # 赋予执行权限
        chmod +x "$SCRIPT_NAME"
        echo "Successfully generated: $SCRIPT_NAME"
    else
        echo "Warning: Directory $TARGET_DIR does not exist, skipping $sample."
    fi
done < sample.list
