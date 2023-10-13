"""
Created on Tue Oct 10 21:35:27 2023

@author: trianaa1
"""
import sys
import numpy as np
import pandas as pd
import pickle
from scipy.io import loadmat, savemat
import concurrent.futures

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_15days, get_pval

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H5'
task = 'pvt'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
lag_no = 16

#load global efficiency data
pc = loadmat(f'{path}/mri/conn_matrix/{task}/{strategy}/parti-coeff_{strategy}_{atlas_name}')['pc']

#Load real data
variables = ['total_sleep_duration','awake_time','restless_sleep'] 
behav = get_behav_data_15days(f'{path}/behavioral',days=16)

#Select only the columns of interest for the hypothesis
selected_cols = [col for col in behav.columns if any(var in col for var in variables)]
behav = behav[selected_cols]

#Load surrogate data
with open(f'{path}/behavioral/surrogate_behav_data.pkl', 'rb') as file:
    surrogate_data = pickle.load(file)
    
#compute the real correlation for each node
columns = list(behav.columns)
real_corr_values = np.zeros((len(variables),lag_no,len(pc)))  # move outside of loop
for lag in range(lag_no):
    sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
    for node in range(len(pc)):
        corrs = sub_behav.corrwith(pd.Series(pc[:,node],name=str(node)), method='spearman')
        real_corr_values[:,lag,node] = corrs.values

#compute fake correlations
def compute_fake_corr(node):
    fake_corr_values = np.zeros((len(variables), lag_no, len(surrogate_data)))
    sub_lagged_dfs = [[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")] for lag in range(lag_no)]
    
    for i, df in enumerate(surrogate_data):
        print(i)
        lagged_df = df[selected_cols]
        for lag in range(lag_no):
            sub_lagged_df = lagged_df[sub_lagged_dfs[lag]]
            corrs = sub_lagged_df.corrwith(pd.Series(pc[:, node], name=str(node)), method='spearman')
            fake_corr_values[:, lag, i] = corrs.values
    
    return fake_corr_values

with concurrent.futures.ProcessPoolExecutor() as executor:
    fake_corr_list = list(executor.map(compute_fake_corr, range(2)))


pvals_list = []
for node in range(0,len(fake_corr_list)):
    pvals = get_pval(real_corr_values, fake_corr_values)
    pvals_list.append(pvals)
pvals_dict = {'{}'.format(i): arr for i, arr in enumerate(pvals_list)}
savemat(f'{savepath}/parti-coeff_{strategy}_{atlas_name}.mat', pvals_dict)