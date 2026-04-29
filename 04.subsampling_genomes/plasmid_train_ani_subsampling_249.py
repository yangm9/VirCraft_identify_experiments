import os
import pandas as pd
import networkx as nx
import random
from Bio import SeqIO

# --- 配置 ---
bacteria_ani = "bacteria_plasmid_ani.tsv"
archaea_ani = "archaea_plasmid_ani.tsv"
bacteria_fasta = "bacteria_plasmid_train.fasta"
archaea_fasta = "archaea_plasmid_train.fasta"
output_fasta = "plasmid_train_sub249.fasta"

target_count = 249
ani_cutoff = 95.0
af_cutoff = 0.85

def parse_id(path_str):
    # 兼容你之前的路径格式，提取文件名作为 ID
    return os.path.basename(path_str).replace('.fasta', '').replace('.fa', '')

def run_plasmid_subsampling():
    # 1. 加载所有原始序列并记录长度 (用于选最长的代表)
    print("正在扫描原始 Fasta 文件...")
    id_to_record = {}
    for f in [bacteria_fasta, archaea_fasta]:
        if os.path.exists(f):
            for record in SeqIO.parse(f, "fasta"):
                # 记录 ID 到 record 的映射
                rid = record.id.split()[0]
                id_to_record[rid] = record
        else:
            print(f"警告: 找不到文件 {f}")

    all_ids = set(id_to_record.keys())
    print(f"原始质粒总数: {len(all_ids)}")

    # 2. 构建相似性图
    G = nx.Graph()
    G.add_nodes_from(all_ids)

    print("读取 ANI 文件并构建聚类图...")
    for ani_file in [bacteria_ani, archaea_ani]:
        if not os.path.exists(ani_file):
            continue
        df = pd.read_csv(ani_file, sep="\t", header=None)
        df.columns = ["query", "ref", "ani", "matched", "total"]
        df["af"] = df["matched"] / df["total"]
        
        # 过滤
        filtered = df[(df["ani"] >= ani_cutoff) & (df["af"] >= af_cutoff)]
        
        for _, row in filtered.iterrows():
            u = parse_id(row["query"])
            v = parse_id(row["ref"])
            if u in all_ids and v in all_ids:
                G.add_edge(u, v)

    # 3. 簇内选代表 (选每个簇中最长的一个)
    clusters = list(nx.connected_components(G))
    print(f"聚类完成，共得到 {len(clusters)} 个簇。")
    
    representatives = []
    for cluster in clusters:
        # 在簇内找长度最长的 ID
        best_id = max(cluster, key=lambda x: len(id_to_record[x].seq))
        representatives.append(best_id)

    print(f"去冗余后剩余代表序列: {len(representatives)} 条")

    # 4. 二次下采样到 249 条
    if len(representatives) > target_count:
        print(f"正在从代表序列中随机抽取 {target_count} 条以对齐比例...")
        final_selected = random.sample(representatives, target_count)
    else:
        final_selected = representatives
        print(f"警告: 即使去冗余后也只有 {len(final_selected)} 条，不足 {target_count}。")

    # 5. 写入文件
    print(f"正在写入 {output_fasta}...")
    with open(output_fasta, "w") as out_f:
        for rid in final_selected:
            SeqIO.write(id_to_record[rid], out_f, "fasta")
    
    print("任务完成！")

if __name__ == "__main__":
    run_plasmid_subsampling()