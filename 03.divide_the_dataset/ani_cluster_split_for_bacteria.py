#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import networkx as nx
from sklearn.model_selection import train_test_split
from Bio import SeqIO
from collections import defaultdict

############################################
# 参数
############################################

parser = argparse.ArgumentParser(
    description="ANI-based clustering + cluster-aware split + representative genome selection"
)

parser.add_argument("--ani", required=True,
                    help="fastANI output file (tsv)")
parser.add_argument("--fasta_dir", required=True,
                    help="Directory containing split genome fasta files")
parser.add_argument("--ani_cutoff", type=float, default=95.0)
parser.add_argument("--af_cutoff", type=float, default=0.85)
parser.add_argument("--out_prefix", default="dataset")

args = parser.parse_args()

############################################
# Step1: 读取 ANI
############################################

print("Reading ANI file...")
df = pd.read_csv(args.ani, sep="\t", header=None)
df.columns = ["query", "ref", "ani", "frag_matched", "frag_total"]
df["af"] = df["frag_matched"] / df["frag_total"]

############################################
# Step2: 过滤
############################################

print("Filtering by ANI and AF...")
filtered = df[
    (df["ani"] >= args.ani_cutoff) &
    (df["af"] >= args.af_cutoff)
]

############################################
# Step3: 构建图 + 聚类
############################################

print("Building graph...")

G = nx.Graph()

genome_lengths = {}

# 添加所有节点 + 计算 genome 长度
for file in os.listdir(args.fasta_dir):
    if file.endswith(".fasta") or file.endswith(".fa"):
        G.add_node(file)

        total_len = 0
        path = os.path.join(args.fasta_dir, file)
        for record in SeqIO.parse(path, "fasta"):
            total_len += len(record.seq)

        genome_lengths[file] = total_len

print(f"Total genomes: {len(genome_lengths)}")

# 添加边
for _, row in filtered.iterrows():
    q = os.path.basename(row["query"])
    r = os.path.basename(row["ref"])
    if q in genome_lengths and r in genome_lengths:
        G.add_edge(q, r)

clusters = list(nx.connected_components(G))
print(f"Total species-level clusters: {len(clusters)}")

############################################
# Step4: cluster-aware split
############################################

cluster_ids = list(range(len(clusters)))

train_c, temp_c = train_test_split(
    cluster_ids, test_size=0.2, random_state=42)

val_c, test_c = train_test_split(
    temp_c, test_size=0.5, random_state=42)

print(f"Train clusters: {len(train_c)}")
print(f"Val clusters: {len(val_c)}")
print(f"Test clusters: {len(test_c)}")

############################################
# Step5: 每个 split 内选 representative
############################################

def select_representatives(cluster_subset, split_name):
    reps = []
    cluster_sizes = []

    for cid in cluster_subset:
        cluster = clusters[cid]
        cluster_sizes.append(len(cluster))

        # 选最长 genome 作为代表
        rep = max(cluster, key=lambda x: genome_lengths.get(x, 0))
        reps.append(rep)

    print(f"{split_name} genomes (representatives): {len(reps)}")
    print(f"{split_name} avg cluster size: {sum(cluster_sizes)/len(cluster_sizes):.2f}")
    print(f"{split_name} max cluster size: {max(cluster_sizes)}")

    return reps


train_genomes = select_representatives(train_c, "Train")
val_genomes   = select_representatives(val_c, "Val")
test_genomes  = select_representatives(test_c, "Test")

############################################
# Step6: 输出 representative mapping
############################################

print("Writing cluster → representative mapping...")

with open(f"{args.out_prefix}_cluster_mapping.tsv", "w") as out_map:
    out_map.write("cluster_id\tsplit\trepresentative\tcluster_size\n")

    for cid in train_c:
        cluster = clusters[cid]
        rep = max(cluster, key=lambda x: genome_lengths.get(x, 0))
        out_map.write(f"{cid}\ttrain\t{rep}\t{len(cluster)}\n")

    for cid in val_c:
        cluster = clusters[cid]
        rep = max(cluster, key=lambda x: genome_lengths.get(x, 0))
        out_map.write(f"{cid}\tval\t{rep}\t{len(cluster)}\n")

    for cid in test_c:
        cluster = clusters[cid]
        rep = max(cluster, key=lambda x: genome_lengths.get(x, 0))
        out_map.write(f"{cid}\ttest\t{rep}\t{len(cluster)}\n")

############################################
# Step7: 合并 FASTA
############################################

def merge_fasta(genome_list, output_file):
    with open(output_file, "w") as out_handle:
        for genome_file in genome_list:
            path = os.path.join(args.fasta_dir, genome_file)
            for record in SeqIO.parse(path, "fasta"):
                SeqIO.write(record, out_handle, "fasta")

print("Writing FASTA files...")

merge_fasta(train_genomes, f"{args.out_prefix}_train.fasta")
merge_fasta(val_genomes,   f"{args.out_prefix}_val.fasta")
merge_fasta(test_genomes,  f"{args.out_prefix}_test.fasta")

print("Done.")