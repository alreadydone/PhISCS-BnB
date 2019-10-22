import pandas as pd
from glob import glob
from collections import defaultdict

kk_all = defaultdict(lambda: 0)
kk_mwm = defaultdict(lambda: 0)

def get_counter(file):
    df = pd.read_csv(file)
    df = df[['hash', 'method', 'n_flips', 'runtime']]
    counter = 0
    for _, df_group in df.groupby("hash"):
        k = df_group['n_flips'].values[0]
        kk_all[k] += 1
        mydict = pd.Series(df_group.runtime.values, index=df_group.method).to_dict()
        if mydict['PhISCS_I_'] > mydict['BnB_SemiDynamicLPBounding_None_True_Gurobi_-1_True_True']:
            counter += 1
            kk_mwm[k] += 1
    return counter

# file = "/data/frashidi/Phylogeny_BnB/reports/Farid2/cmp_algs_3,33,2_10-19-20-20-23.csv"
# print(get_counter(file))
# exit()

for file in glob('/data/frashidi/Phylogeny_BnB/reports/Farid2/cmp*'):
    get_counter(file)

print(sorted(kk_all.items() ,  key=lambda x: x[0]))
print()
print(sorted(kk_mwm.items() ,  key=lambda x: x[0]))
