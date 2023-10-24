import sys, os 
import numpy as np
import pandas as pd
import pickle
from scipy.io import loadmat, savemat
import concurrent.futures

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_15days

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/permutation/H5'
task = 'pvt'
strategy = sys.argv[1]
atlas_name = sys.argv[2]
lag_no = 16
node = sys.argv[3]
###############################################################################

#Transform node to number format
node = int(node)

#load global efficiency data
pc = loadmat(f'{path}/mri/conn_matrix/{task}/{strategy}/parti-coeff_{strategy}_{atlas_name}')['pc']
node_num = pc.shape[1]
print('PC loaded!')

#Load real data
variables = ['total_sleep_duration','awake_time','restless_sleep']
behav = get_behav_data_15days(f'{path}/behavioral',days=16)

#Select only the columns of interest for the hypothesis
selected_cols = [col for col in behav.columns if any(var in col for var in variables)]
behav = behav[selected_cols]

#Load surrogate data
with open(f'{path}/behavioral/surrogate_behav_data.pkl', 'rb') as file:
    surrogate_data = pickle.load(file)
print('surrogate data loaded')
    
#compute fake correlations
columns = list(behav.columns)
filename = f'{savepath}/temp_fake_corr_values_{strategy}_{atlas_name}_node_{node}.pkl'
print(f'fake corr for {filename}')

fake_corr_values = np.zeros((len(variables), lag_no, len(surrogate_data)))
sub_lagged_dfs = [[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")] for lag in range(lag_no)]

for i, df in enumerate(surrogate_data):
    lagged_df = df[selected_cols]
    for lag in range(lag_no):
        print(f'permu {i},lag {lag}')
        sub_lagged_df = lagged_df[sub_lagged_dfs[lag]]
        corrs = sub_lagged_df.corrwith(pd.Series(pc[:, node], name=str(node)), method='spearman')
        fake_corr_values[:, lag, i] = corrs.values
        
with open(filename, 'wb') as file:
    pickle.dump(fake_corr_values, file)
print(f'{filename} saved!')