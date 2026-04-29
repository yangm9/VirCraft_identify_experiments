import os
from Bio import SeqIO

# --- 配置路径 ---
ani_dir = "bacteria_genus_ani"
train_fasta = "fa/bacteria_genome_train.fasta"
output_fasta = "bacteria_genome_train_sub3390_longest.fasta"
target_count = 3390

def parse_id_from_path(path_str):
    """提取 ID: 'dir/ID.fasta' -> 'ID'"""
    return path_str.split('/')[-1].replace('.fasta', '')

def run_longest_subsampling():
    # 1. 扫描训练集：记录存在的 ID 及其长度
    print(f"正在扫描训练集长度信息: {train_fasta}...")
    id_to_len = {}
    for record in SeqIO.parse(train_fasta, "fasta"):
        # 记录 ID 到长度的映射
        id_to_len[record.id.split()[0]] = len(record.seq)
    
    train_whitelist = set(id_to_len.keys())
    print(f"白名单加载完成，共 {len(train_whitelist)} 条序列。")

    # 2. 读取 ANI 文件
    genus_files = [f for f in os.listdir(ani_dir) if f.endswith('_ani.tsv')]
    selected_ids = set()
    global_available_in_ani = set() 

    print(f"正在根据 {len(genus_files)} 个属的 ANI 结果提取最长代表...")
    
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
        
        if not genus_pool: continue
        
        # 记录该属在白名单中所有可用的 ID
        global_available_in_ani.update(genus_pool)
        
        # --- 核心改进：选该属内最长的序列 ---
        best_id = max(genus_pool, key=lambda x: id_to_len[x])
        selected_ids.add(best_id)

    print(f"各属最长代表筛选完成，初步获得: {len(selected_ids)} 条")

    # 3. 补齐到 3390 条 (依然遵循长度优先)
    if len(selected_ids) < target_count:
        gap = target_count - len(selected_ids)
        print(f"当前缺口 {gap} 条，正在按长度补齐...")
        
        # 候选池 A: ANI 中存在但未被选为代表的序列
        candidates_ani = list(global_available_in_ani - selected_ids)
        # 按长度降序排列
        candidates_ani.sort(key=lambda x: id_to_len[x], reverse=True)
        
        if len(candidates_ani) >= gap:
            selected_ids.update(candidates_ani[:gap])
        else:
            selected_ids.update(candidates_ani)
            # 候选池 B: 训练集中完全没出现在 ANI 里的序列
            gap = target_count - len(selected_ids)
            candidates_white = list(train_whitelist - selected_ids)
            candidates_white.sort(key=lambda x: id_to_len[x], reverse=True)
            selected_ids.update(candidates_white[:min(gap, len(candidates_white))])

    # 4. 最终提取并写入
    print(f"最终选定 ID 总数: {len(selected_ids)}")
    print("正在写入 Fasta...")
    
    final_count = 0
    with open(output_fasta, "w") as out_f:
        for record in SeqIO.parse(train_fasta, "fasta"):
            if record.id.split()[0] in selected_ids:
                SeqIO.write(record, out_f, "fasta")
                final_count += 1
                selected_ids.remove(record.id.split()[0]) # 提高效率
    
    print(f"成功写入: {final_count} 条序列至 {output_fasta}")

if __name__ == "__main__":
    if not os.path.exists(train_fasta):
        print(f"错误: 找不到文件 {train_fasta}")
    else:
        run_longest_subsampling()