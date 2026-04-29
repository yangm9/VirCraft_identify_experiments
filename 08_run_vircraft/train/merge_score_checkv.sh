# 遍历 sample.list 中的每一个样本
while read -r sample; do
    CHECKV_FILE="${sample}_identify/work_files/checkv_all/quality_summary.tsv"
    QUAL_FILE="${sample}_identify/work_files/all_quality_summary.tsv"
    if [ -f "$CHECKV_FILE" ]; then
        # 使用 sed 将第一行的 contig_id 替换为 Contig
        # '1s' 表示只针对第一行进行操作
        sed '1s/contig_id/Contig/' "$CHECKV_FILE" > "$QUAL_FILE"
        echo "Generated: $QUAL_FILE"
    else
        echo "Skip: $CHECKV_FILE not found"
fi
done < sample.list
#!/bin/bash

# 遍历 sample.list
while read -r sample; do
    # 定义工作目录路径
    WORK_DIR="${sample}_identify/work_files"
    
    # 检查必要的输入文件是否存在
    # 注意：这里假设你的 quality_summary.tsv 已经在 work_files 目录下，或者你已经将其重命名为 all_quality_summary.tsv
    FILE1="${WORK_DIR}/all_quality_summary.tsv"
    FILE2="${WORK_DIR}/candidate_viral_ctgs.info.tsv"
    echo $FILE2
    OUTPUT="${WORK_DIR}/all_viral_ctgs.info.qual.tsv"

    if [ -f "$FILE1" ] && [ -f "$FILE2" ]; then
        echo "Processing $sample ..."
        
        # 切换到工作目录执行，或者直接使用绝对路径
        # 根据你提供的用法：linkTab.py <table1> <table2> <type> <corner> <output>
        # 这里使用 left join，以 score 表为主表或 quality 表为主表取决于你的分析需求
        linkTab.py "$FILE1" "$FILE2" left Contig "$OUTPUT"
        
    else
        echo "Warning: Missing input files for $sample in $WORK_DIR"
    fi
done < sample.list
