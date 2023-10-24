import sys, os
import numpy as np
import pandas as pd
import pickle
from scipy.io import loadmat, savemat

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_15days, get_pval

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H7'
task = 'rs'
strategy = sys.argv[1]#'24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = sys.argv[2]#'seitzman-set2'
lag_no = 16
###############################################################################

if atlas_name=='seitzman-set1':
    node_num = 293
else:
    node_num = 384

#load global efficiency data
pc = loadmat(f'{path}/mri/conn_matrix/{task}/{strategy}/parti-coeff_{strategy}_{atlas_name}')['pc']
node_num = pc.shape[1]

#Load real data
variables = ['total_sleep_duration','awake_time','restless_sleep','pa_mean','pa_std', 
             'na_mean','stress_mean','pain_mean','mean_respiratory_rate_brpm', 
             'min_respiratory_rate_brpm','max_respiratory_rate_brpm','mean_prv_rmssd_ms',
             'min_prv_rmssd_ms','max_prv_rmssd_ms','std_prv_rmssd_ms'] 
behav = get_behav_data_15days(f'{path}/behavioral',days=16)

#Select only the columns of interest for the hypothesis
selected_cols = [col for col in behav.columns if any(var in col for var in variables)]
behav = behav[selected_cols]

#compute the real correlation for each node
columns = list(behav.columns)
real_corr_values = np.zeros((len(variables),lag_no,node_num))  # move outside of loop
for lag in range(lag_no):
    sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
    for node in range(len(pc)):
        corrs = sub_behav.corrwith(pd.Series(pc[:,node],name=str(node)), method='spearman')
        real_corr_values[:,lag,node] = corrs.values
print('computed real correlations')

#Load surrogate correlations per node
fake_corr_dict = {}
for node in range(node_num):  # Adjust the range as needed
    filename = f'{path}/mri/permutation/H7/temp_fake_corr_values_{strategy}_{atlas_name}_node_{node}.pkl'

    if not os.path.exists(filename):
        print(f"File is missing for node_{node}: {filename}")
        fake_corr_dict[node] = None  # Setting value as None if file is missing
    else:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            fake_corr_dict[node] = data

pvals_dict = {}
for node in fake_corr_dict.keys():
    print(f'computing p-value for node: {str(node)}')
    pvals = get_pval(real_corr_values[:,:,node], fake_corr_dict[node])
    pvals_dict[node] = pvals
pvals_dict_strkeys = {f"node_{k}": v for k, v in pvals_dict.items()}
savemat(f'{savepath}/parti-coeff_{strategy}_{atlas_name}.mat', pvals_dict_strkeys)