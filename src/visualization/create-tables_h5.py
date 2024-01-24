"""
This script summarizes the significant results for global efficiency and participation
coefficients, organizing them and matching the results with the node coordinates for H5

"""
import os, sys
import pandas as pd
from scipy.io import loadmat


sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import compute_real_corr

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/visualization')
from visual_utils import lags_to_table

###############################################################################
# Change this!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H5'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
task = 'pvt'
variables = ["total_sleep_duration", "awake_time", "restless_sleep"]
atlas_name = 'seitzman-set1'
strategy = '24HMP-8Phys-Spike_HPF'
thres = ['thr-10', 'thr-20', 'thr-30']
alpha = 0.05
lag_no = 16
###############################################################################

#Define the file to save
savefile = f'{path}/{strategy}_{atlas_name}_finaltable.xlsx'
network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'cingulo opercular', 4: 'somatomotor'}
    
#For global efficiency
measure = 'global-eff'
if measure == 'parti-coeff':
    name = 'pcs'
else:
    name = 'effs'
    
#compute the real correlation for the participation coefficientes
df_to_save = []
for thr in thres:
    #Compute the correlation values
    pc = loadmat(f'{behav_path}/mri/conn_matrix/{task}/{strategy}/{measure}_{strategy}_{atlas_name}_{thr}')[name]
    real_corr_values = compute_real_corr(behav_path, variables, pc, lag_no)

    #now select the significant p-values
    data = loadmat(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}_BHcorrected.mat')['data_BH']
    final_df = lags_to_table(data, real_corr_values, variables, network_mapping, alpha, thr)
    df_to_save.append(final_df)

df_to_save = pd.concat(df_to_save)

if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        df_to_save.to_excel(writer, sheet_name=measure, index=False)
else:
    df_to_save.to_excel(savefile, sheet_name=measure, index=False)
    
#For participation coefficient
measure = 'parti-coeff'
if measure == 'parti-coeff':
    name = 'pcs'
else:
    name = 'effs'
    
#compute the real correlation for the participation coefficientes
df_to_save = []
for thr in thres:
    #Compute the correlation values
    pc = loadmat(f'{behav_path}/mri/conn_matrix/{task}/{strategy}/{measure}_{strategy}_{atlas_name}_{thr}')[name]
    real_corr_values = compute_real_corr(behav_path, variables, pc, lag_no)

    #now select the significant p-values
    data = loadmat(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}_BHcorrected.mat')['data_BH']
    final_df = lags_to_table(data, real_corr_values, variables, network_mapping, alpha, thr)
    df_to_save.append(final_df)

df_to_save = pd.concat(df_to_save)

if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        df_to_save.to_excel(writer, sheet_name=measure, index=False)
else:
    df_to_save.to_excel(savefile, sheet_name=measure, index=False)