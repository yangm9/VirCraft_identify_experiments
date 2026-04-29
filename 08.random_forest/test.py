import os
import pandas as pd

SCORE_DIR = "1.score"

# ===== 读取数据 =====
dfs = []
for f in os.listdir(SCORE_DIR):
    if not f.endswith(".tsv"):
        continue

    df = pd.read_csv(os.path.join(SCORE_DIR, f), sep="\t")

    if f.startswith("positive"):
        df["label"] = 1
    elif f.startswith("negative"):
        df["label"] = 0
    else:
        continue

    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# ===== 定义高分误判 =====
high_score_fp = df[
    (df["total_score"] >= 5) &   # 你可以调这个阈值
    (df["label"] == 0)
]

print(f"🔥 高分误判数量: {len(high_score_fp)}")

# ===== 看各个规则平均贡献 =====
cols = ["vs2_score", "vb_score", "dvf_score", "gn_score", "add_score", "rm_score"]

print("\n📊 平均分贡献（误判样本）:")
print(high_score_fp[cols].mean())

print("\n📊 平均分贡献（真实病毒）:")
print(df[df["label"] == 1][cols].mean())

# ===== 对比差异 =====
print("\n📊 差异（误判 - 真阳性）:")
print(high_score_fp[cols].mean() - df[df["label"] == 1][cols].mean())

# ===== 查看典型错误样本 =====
print("\n🔬 示例错误样本:")
print(high_score_fp[
    ["total_score", "vs2_score", "vb_score", "dvf_score", "gn_score", "add_score", "rm_score"]
].head(10))