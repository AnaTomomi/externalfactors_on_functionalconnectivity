import sys, os
import numpy as np
import pandas as pd
import pickle
from scipy.stats import zscore
from scipy.io import loadmat, savemat

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_15days, get_pval

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H6'
task = 'nback'
strategy = sys.argv[1]#'24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = sys.argv[2]#'seitzman-set2'
thres = sys.argv[3]#'thr-10'
variable = sys.argv[4] #'global-eff'
lag_no = 16
###############################################################################


#load the data
if variable == 'global-eff':
    pc = loadmat(f'{path}/mri/conn_matrix/{task}/{strategy}/{variable}_{strategy}_{atlas_name}_{thres}')['effs']
else:
    pc = loadmat(f'{path}/mri/conn_matrix/{task}/{strategy}/{variable}_{strategy}_{atlas_name}_{thres}')['pcs']
net_num = pc.shape[1]

#Load real data
variables = ['total_sleep_duration','awake_time','restless_sleep', 'steps', 'inactive_time'] 
behav = get_behav_data_15days(f'{path}/behavioral',days=16)

#Select only the columns of interest for the hypothesis
selected_cols = [col for col in behav.columns if any(var in col for var in variables)]
behav = behav[selected_cols]
behav = zscore(behav) #z-score standardization

#compute the real correlation for each node
columns = list(behav.columns)
real_corr_values = np.zeros((len(variables),lag_no,net_num))  # move outside of loop
for lag in range(lag_no):
    sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
    for net in range(net_num):
        corrs = sub_behav.corrwith(pd.Series(pc[:,net],name=str(net)), method='spearman')
        real_corr_values[:,lag,net] = corrs.values
print('computed real correlations')

#Load surrogate correlations per network
fake_corr_dict = {}
for net in range(net_num):  # Adjust the range as needed
    filename = f'{path}/mri/permutation/H6/temp_fake_corr_values_{variable}_{strategy}_{atlas_name}_{thres}_net_{net}.pkl'

    if not os.path.exists(filename):
        print(f"File is missing for network_{net}: {filename}")
        fake_corr_dict[net] = None  # Setting value as None if file is missing
    else:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            fake_corr_dict[net] = data

pvals_dict = {}
for net in fake_corr_dict.keys():
    print(f'computing p-value for network: {str(net)}')
    pvals = get_pval(real_corr_values[:,:,net], fake_corr_dict[net])
    pvals_dict[net] = pvals
pvals_dict_strkeys = {f"net_{k}": v for k, v in pvals_dict.items()}
savemat(f'{savepath}/{variable}_{strategy}_{atlas_name}_{thres}.mat', pvals_dict_strkeys)