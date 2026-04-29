import os
from Bio import SeqIO

# --- 配置路径 ---
ani_dir = "bacteria_genus_ani"
train_fasta = "fa/bacteria_genome_train.fasta"
output_fasta = "bacteria_genome_train_sub1540_longest.fasta"

def parse_id_from_path(path_str):
    return path_str.split('/')[-1].replace('.fasta', '')

def run_longest_sampling():
    # 1. 预扫描训练集：建立 ID 到 长度 的映射，并存入白名单
    print(f"正在扫描训练集长度信息: {train_fasta}...")
    id_to_len = {}
    for record in SeqIO.parse(train_fasta, "fasta"):
        id_to_len[record.id.split()[0]] = len(record.seq)
    
    train_whitelist = set(id_to_len.keys())
    print(f"白名单加载完成，共 {len(train_whitelist)} 条序列。")

    # 2. 遍历 ANI 文件夹，每个属选最长的一个
    genus_files = [f for f in os.listdir(ani_dir) if f.endswith('_ani.tsv')]
    selected_ids = set()
    
    print(f"开始从 {len(genus_files)} 个属中提取最长代表...")
    
    for filename in genus_files:
        genus_pool = set()
        filepath = os.path.join(ani_dir, filename)
        
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 2: continue
                id1 = parse_id_from_path(parts[0])
                id2 = parse_id_from_path(parts[1])
                
                if id1 in train_whitelist: genus_pool.add(id1)
                if id2 in train_whitelist: genus_pool.add(id2)
        
        if genus_pool:
            # --- 核心修改：按长度排序，选最长的 ---
            best_id = max(genus_pool, key=lambda x: id_to_len[x])
            selected_ids.add(best_id)

    print(f"属级最长代表筛选完成，共选定 {len(selected_ids)} 条。")

    # 3. 写入最终文件
    print("正在写入 Fasta...")
    final_count = 0
    with open(output_fasta, "w") as out_f:
        # 为了提高效率，重新扫一遍 Fasta 提取选中的 ID
        for record in SeqIO.parse(train_fasta, "fasta"):
            rid = record.id.split()[0]
            if rid in selected_ids:
                SeqIO.write(record, out_f, "fasta")
                final_count += 1
                selected_ids.remove(rid)
    
    print(f"\n成功！最终写入: {final_count} 条，文件: {output_fasta}")

if __name__ == "__main__":
    if not os.path.exists(train_fasta):
        print(f"错误: 找不到输入文件 {train_fasta}")
    else:
        run_longest_sampling()