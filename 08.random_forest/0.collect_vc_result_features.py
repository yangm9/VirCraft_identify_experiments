#!/usr/bin/env python3
import os
import shutil

def collect_and_standardize():
    # ===== 固定路径 =====
    base_dir = "/backup/yangming/VIRPHA230501MV/vc_test/mock_data/2024-GB-Benchmarking_bioinformatic_virus/5-3.identify_rm_training_by_len"
    output_dir = f"{base_dir}/machine_learning/four_tools_by_len_260407_parameter_set_5/0.data"
    
    datasets = ['train', 'val', 'test']
    target_file = "candidate_viral_ctgs.qual.tsv"

    print("🚀 开始提取并标准化特征表格...")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    missing_count = 0

    for ds in datasets:
        ds_path = os.path.join(base_dir, ds)

        if not os.path.exists(ds_path):
            print(f"⚠️ 目录不存在: {ds_path}")
            continue

        print(f"\n📂 扫描目录: {ds_path}")

        for sub_dir in os.listdir(ds_path):
            if not sub_dir.endswith('_identify'):
                continue

            source_path = os.path.join(
                ds_path,
                sub_dir,
                "work_files",
                target_file
            )

            if not os.path.exists(source_path):
                print(f"  ❌ 未找到: {source_path}")
                missing_count += 1
                continue

            # ===== 1️⃣ label =====
            label = "positive" if "positive" in sub_dir else "negative"

            # ===== 2️⃣ gradient =====
            gradient = ""
            for part in sub_dir.split('_'):
                if 'k' in part:
                    gradient = part
                    break

            if gradient == "":
                gradient = "unknown"

            # ===== 3️⃣ 防冲突命名（推荐：带来源目录）=====
            safe_subdir = sub_dir.replace("/", "_")

            base_name = f"{label}_{ds}_{gradient}_viral_ctgs.qual.tsv"
            dest_path = os.path.join(output_dir, base_name)

            # ===== 5️⃣ 执行复制 =====
            shutil.copy2(source_path, dest_path)
            print(f"  ✅ {os.path.basename(dest_path)}")
            count += 1

    print("\n✨ 汇总完成")
    print(f"✔ 成功提取: {count} 个文件")
    print(f"❌ 缺失文件: {missing_count} 个")

if __name__ == "__main__":
    collect_and_standardize()
