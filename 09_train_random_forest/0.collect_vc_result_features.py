#!/usr/bin/env python3

import os
import sys
import shutil

def collect_and_standardize(base_dir):
    input_dir = f'{base_dir}/08_run_vircraft'
    output_dir = f'{base_dir}/09_train_random_forest/0.data'
    
    datasets = ['train', 'val', 'test']
    target_file = 'candidate_viral_ctgs.qual.tsv'

    print('Start to extract and normalize the feature tables')

    # Make output directory
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    missing_count = 0

    for ds in datasets:
        ds_path = os.path.join(input_dir, ds)

        if not os.path.exists(ds_path):
            print(f'Directory does not exist: {ds_path}')
            continue

        print(f'\nScan directory: {ds_path}')

        for sub_dir in os.listdir(ds_path):
            if not sub_dir.endswith('_identify'):
                continue

            source_path = os.path.join(
                ds_path,
                sub_dir,
                'work_files',
                target_file
            )

            if not os.path.exists(source_path):
                print(f'Can not find: {source_path}')
                missing_count += 1
                continue

            label = 'positive' if 'positive' in sub_dir else 'negative'

            gradient = ''
            for part in sub_dir.split('_'):
                if 'k' in part:
                    gradient = part
                    break

            if gradient == '':
                gradient = 'unknown'

            safe_subdir = sub_dir.replace('/', '_')

            base_name = f'{label}_{ds}_{gradient}_viral_ctgs.qual.tsv'
            dest_path = os.path.join(output_dir, base_name)

            shutil.copy2(source_path, dest_path)
            print(f'{os.path.basename(dest_path)}')
            count += 1

    print('\nSummary completed')
    print(f'Successfully extracted: {count} files')
    print(f'Missing file: {missing_count}')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        collect_and_standardize(sys.argv[1])
    else:
        print(f'Usage: python {sys.argv[0]} ..')
