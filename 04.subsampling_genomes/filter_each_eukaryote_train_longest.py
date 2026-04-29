import os
from Bio import SeqIO

def filter_single_category(input_file, output_file, target_count):
    if not os.path.exists(input_file):
        print(f"跳过：找不到输入文件 {input_file}")
        return
        
    print(f"正在处理 {input_file} ...")
    
    # 1. 读取所有序列
    records = list(SeqIO.parse(input_file, "fasta"))
    
    # 2. 按长度从大到小排序 (key=len)
    records.sort(key=lambda x: len(x.seq), reverse=True)
    
    # 3. 选取前 N 条最长的
    selected = records[:target_count]
    
    # 4. 写入新文件
    with open(output_file, "w") as f:
        SeqIO.write(selected, f, "fasta")
    
    print(f"完成！从 {len(records)} 条中选出了 {len(selected)} 条最长序列。")
    print(f"保存至: {output_file}\n")

if __name__ == "__main__":
    # 任务 1: 真菌 (Fungi) - 目标约 150 条 (对应 2% 占比)
    filter_single_category(
        input_file="fungi_genome_train.fasta", 
        output_file="fungi_genome_train_sub150_longest.fasta", 
        target_count=150
    )
    
    # 任务 2: 原生生物 (Protist) - 目标约 250 条 (对应 5% 占比)
    filter_single_category(
        input_file="protist_genome_train.fasta", 
        output_file="protist_genome_train_sub250_longest.fasta", 
        target_count=250
    )