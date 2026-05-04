import pandas as pd

def calc_contribution(df_results):
    df_results['MCC'] = df_results['MCC%'].astype(float)
    
    rules = ['vs2_score', 'vb_score', 'dvf_score', 'gn_score', 'add_score', 'rm_score']
    
    contrib = {r: [] for r in rules}
    
    for r in rules:
        for idx, row in df_results.iterrows():
            combo = row['Tool/Model'].split('+')
            if r in combo:
                combo_minus_r = '+'.join([x for x in combo if x != r])
                mcc_minus_r = df_results[df_results['Tool/Model'] == combo_minus_r]['MCC']
                if len(mcc_minus_r) == 0:
                    continue
                contrib[r].append(row['MCC'] - mcc_minus_r.values[0])
    
    avg_contrib = {r: sum(v)/len(v) for r,v in contrib.items()}
    print(avg_contrib)
    return 0
