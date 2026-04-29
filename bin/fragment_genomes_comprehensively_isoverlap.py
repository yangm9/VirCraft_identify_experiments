#!/usr/bin/env python3
import sys
import random
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def fragment_logic(min_len, max_len, input_fasta, seed, stride, mode):
    random.seed(seed)
    
    try:
        for record in SeqIO.parse(input_fasta, "fasta"):
            seq_len = len(record.seq)
            if seq_len < min_len:
                continue

            start = 0
            # 模式 1: Sliding (滑动窗口，允许重叠)
            if mode == "sliding":
                while start + min_len <= seq_len:
                    current_max = min(max_len, seq_len - start)
                    if current_max < min_len: break
                    
                    frag_len = random.randint(min_len, current_max)
                    end = start + frag_len
                    
                    yield record.seq[start:end], start, end, record.id
                    start += stride

            # 模式 2: Unique (断点切割，绝对不重叠，类似 Alex Reynolds 逻辑)
            elif mode == "unique":
                while start <= seq_len - min_len:
                    # 确保剩余长度能切出一个合法片段
                    current_max = min(max_len, seq_len - start)
                    frag_len = random.randint(min_len, current_max)
                    end = start + frag_len
                    
                    yield record.seq[start:end], start, end, record.id
                    # 强制步进等于当前片段长度，保证不重叠
                    start = end

    except Exception as e:
        sys.stderr.write(f"Error processing: {str(e)}\n")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python3 fragment_genomes_master.py <min_len> <max_len> <input_fasta> <seed> <mode> [stride]")
        print("Modes: 'sliding' (needs stride) or 'unique' (no overlap)")
        sys.exit(1)

    m_len = int(sys.argv[1])
    x_len = int(sys.argv[2])
    f_in  = sys.argv[3]
    s_val = int(sys.argv[4])
    mode_val = sys.argv[5].lower()
    
    # 逻辑处理：如果是 unique 模式，忽略 stride；如果是 sliding 模式，默认 stride=min_len
    if mode_val == "sliding":
        stride_val = int(sys.argv[6]) if len(sys.argv) == 7 else m_len
    else:
        stride_val = 0 # Unique 模式下不使用此变量

    # 执行并标准 Fasta 输出
    for sub_seq, start, end, ori_id in fragment_logic(m_len, x_len, f_in, s_val, stride_val, mode_val):
        new_id = f"{ori_id}_frag_{start}_{end}"
        rec = SeqRecord(sub_seq, id=new_id, description="")
        sys.stdout.write(rec.format("fasta"))