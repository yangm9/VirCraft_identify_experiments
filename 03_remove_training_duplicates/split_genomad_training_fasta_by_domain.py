import os

#Parse reference_clusters.tsv and build a mapping: genome_id -> category (euk, virus, plasmid, chromosome)
def parse_clusters(cluster_file):
    genome_to_type = {}
    with open(cluster_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            cluster_name = parts[0]
            genome_list = parts[3]
            # 类型由 cluster_name 前缀决定
            if cluster_name.startswith('euk_'):
                category = 'euk'
            elif cluster_name.startswith('virus_'):
                category = 'virus'
            elif cluster_name.startswith('plasmid_'):
                category = 'plasmid'
            elif cluster_name.startswith('chromosome_'):
                category = 'chromosome'
            else:
                continue
            genomes = genome_list.split(',')
            for genome in genomes:
                genome_to_type[genome] = category
    return genome_to_type

#Split FASTA into 4 files based on genome category.
def split_fasta(fasta_file, genome_to_type):
    output_files = {
        'euk': open('gn_euk_train.fasta', 'w'),
        'virus': open('gn_virus_train.fasta', 'w'),
        'plasmid': open('gn_plasmid_train.fasta', 'w'),
        'chromosome': open('gn_prokaryote_train.fasta', 'w'),
    }
    current_header = None
    current_seq_lines = []
    def write_record():
        if not current_header:
            return
        # 提取序列ID（>后第一个字段）
        seq_id = current_header[1:].split()[0]
        category = genome_to_type.get(seq_id)
        if category:
            output_files[category].write(current_header)
            output_files[category].write(''.join(current_seq_lines))
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                # 写入上一条记录
                write_record()

                current_header = line
                current_seq_lines = []
            else:
                current_seq_lines.append(line)
        # 写入最后一条
        write_record()
    for fh in output_files.values():
        fh.close()

if __name__ == '__main__':
    cluster_file = 'genomad_supplementary_data_code/reference_sequences/reference_clusters.tsv'
    fasta_file = 'genomad_supplementary_data_code/reference_sequences/reference_sequences.fna'
    genome_to_type = parse_clusters(cluster_file)
    split_fasta(fasta_file, genome_to_type)
    print('Finished splitting FASTA file.')
