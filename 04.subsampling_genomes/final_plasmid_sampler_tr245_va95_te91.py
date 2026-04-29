import os
import random
import pandas as pd
import networkx as nx
from Bio import SeqIO

# --- 配置参数 ---
tasks = {
    "train": {"fasta": "bacteria_plasmid_train.fasta", "target": 249, "out": "plasmid_train_sub249.fasta"},
    "val":   {"fasta": "bacteria_plasmid_val.fasta",   "target": 95,  "out": "plasmid_val_sub95.fasta"},
    "test":  {"fasta": "bacteria_plasmid_test.fasta",  "target": 91,  "out": "plasmid_test_sub91.fasta"}
}

ani_files = ["bacteria_plasmid_ani.tsv", "archaea_plasmid_ani.tsv"]
ani_cutoff = 95.0
af_cutoff = 0.85

def parse_id(path_str):
    return os.path.basename(path_str).replace('.fasta', '').replace('.fa', '')

def process_set(set_name, config):
    print(f"\n--- 正在处理 {set_name.upper()} 集合 ---")
    
    # 1. 加载当前集合的 Fasta
    if not os.path.exists(config["fasta"]):
        print(f"跳过: 找不到 {config['fasta']}")
        return

    records = {rec.id.split()[0]: rec for rec in SeqIO.parse(config["fasta"], "fasta")}
    current_ids = set(records.keys())
    print(f"原始序列总数: {len(current_ids)}")

    # 2. 构建聚类图
    G = nx.Graph()
    G.add_nodes_from(current_ids)

    for ani_f in ani_files:
        if not os.path.exists(ani_f): continue
        df = pd.read_csv(ani_f, sep="\t", header=None)
        df.columns = ["query", "ref", "ani", "m", "t"]
        df["af"] = df["m"] / df["t"]
        
        # 过滤属于当前集合且满足 ANI 条件的边
        filtered = df[(df["ani"] >= ani_cutoff) & (df["af"] >= af_cutoff)]
        for _, row in filtered.iterrows():
            u, v = parse_id(row["query"]), parse_id(row["ref"])
            if u in current_ids and v in current_ids:
                G.add_edge(u, v)

    # 3. 簇内选最长
    clusters = list(nx.connected_components(G))
    representatives = []
    for cluster in clusters:
        best_id = max(cluster, key=lambda x: len(records[x].seq))
        representatives.append(best_id)
    
    print(f"去冗余后代表数: {len(representatives)}")

    # 4. 抽稀到目标条数
    if len(representatives) > config["target"]:
        final_ids = random.sample(representatives, config["target"])
    else:
        final_ids = representatives
        print(f"警告: 代表数不足 {config['target']}，已全量保留。")

    # 5. 写入
    with open(config["out"], "w") as out_f:
        for rid in final_ids:
            SeqIO.write(records[rid], out_f, "fasta")
    print(f"结果已保存至: {config['out']} (共 {len(final_ids)} 条)")

if __name__ == "__main__":
    # 同时也尝试加载古菌质粒（如果存在的话，合并逻辑）
    # 这里默认你当前目录下的 fasta 只包含细菌，
    # 如果有古菌质粒 train/val/test，请手动 cat 到对应文件后再运行。
    for s_name, s_conf in tasks.items():
        process_set(s_name, s_conf)