#!/usr/bin/env python3

import os
import sys
import argparse
import pandas as pd
import networkx as nx
from sklearn.model_selection import train_test_split
from Bio import SeqIO

############################################
# 参数
############################################

parser = argparse.ArgumentParser(
    description="ANI-based clustering + cluster-aware split (8:1:1)"
)

parser.add_argument("--ani", required=True,
                    help="fastANI output file (tsv)")
parser.add_argument("--fasta_dir", required=True,
                    help="Directory containing split genome fasta files")
parser.add_argument("--ani_cutoff", type=float, default=95.0)
parser.add_argument("--af_cutoff", type=float, default=0.85)
parser.add_argument("--out_prefix", default="viral")

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

# 添加所有节点（防止孤立节点丢失）
for file in os.listdir(args.fasta_dir):
    if file.endswith(".fasta") or file.endswith(".fa"):
        G.add_node(file)

# 添加边
for _, row in filtered.iterrows():
    q = os.path.basename(row["query"])
    r = os.path.basename(row["ref"])
    G.add_edge(q, r)

clusters = list(nx.connected_components(G))

print(f"Total clusters: {len(clusters)}")

############################################
# Step4: cluster-aware split
############################################

cluster_ids = list(range(len(clusters)))

train_c, temp_c = train_test_split(
    cluster_ids, test_size=0.2, random_state=42)

val_c, test_c = train_test_split(
    temp_c, test_size=0.5, random_state=42)

def get_genomes(cluster_subset):
    genomes = []
    for cid in cluster_subset:
        genomes.extend(list(clusters[cid]))
    return genomes

train_genomes = get_genomes(train_c)
val_genomes   = get_genomes(val_c)
test_genomes  = get_genomes(test_c)

print("Train genomes:", len(train_genomes))
print("Val genomes:", len(val_genomes))
print("Test genomes:", len(test_genomes))

############################################
# Step5: 合并 fasta
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