"""
This script summarizes the significant results for global efficiency and participation
coefficients, organizing them and matching the results with the node coordinates for H5

"""
import os
import pandas as pd
import numpy as np
from scipy.io import loadmat

from utils import get_behav_data_15days
###############################################################################
# Change this!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H6'
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
task = 'nback'
variable = ["total_sleep_duration", "awake_time", "restless_sleep", "steps", "inactive_time"]
atlas_name = 'seitzman-set1'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
alpha = 0.05
lag_no = 16
###############################################################################

#Define the file to save
savefile = f'{path}/{strategy}_{atlas_name}_finaltable.xlsx'

#Standardize the atlas info
atlas_info = pd.read_excel(f'{atlas_path}/{task}/group_{atlas_name}_info.xlsx')
if atlas_name=='seitzman-set1':
    atlas_info.drop(columns=['radiusmm', 'netWorkbenchLabel','integrativePercent', 'Power', 'AnatomicalLabels'],inplace=True)
    atlas_info.rename(columns={'netName':'network'},inplace=True)
else:
    network_mapping = {0:'unassigned',1:'DefaultMode',2:'Visual',3:'FrontoParietal',
    4:'StriatalOrbitofrontalAmygdalar',5:'DorsalAttention',7:'VentralAttention',
    8:'Salience',9:'CinguloOpercular',10:'SomatomotorDorsal',11:'SomatomotorLateral',
    12:'Auditory',14:'MedialTemporalLobe',15:'ParietalMedial',16:'ParietoOccipital',
    22:'unassigned'}
    atlas_info['network'] = atlas_info['network'].replace(network_mapping)
    atlas_info.rename(columns={'gordon':'roi'},inplace=True)
    
#Load behavioral data
behav = get_behav_data_15days(f'{behav_path}/behavioral',days=16)
selected_cols = [col for col in behav.columns if any(var in col for var in variable)]
behav = behav[selected_cols]
columns = list(behav.columns)

#For global efficiency
measure = 'global-eff'

#compute the real correlation for the global efficiency
eff = loadmat(f'{atlas_path}/{task}/{strategy}/global-eff_{strategy}_{atlas_name}')['eff']
eff = pd.Series(eff.flatten(), name='eff')
real_corr_values = np.zeros((len(variable),lag_no))
for lag in range(0,lag_no):
    #Select only the columns for the lag
    sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
    corrs = sub_behav.corrwith(eff, method='spearman')
    real_corr_values[:,lag] = corrs.values #although lag0 is not informative yet
real_corr_values = pd.DataFrame(real_corr_values, index=variable, columns=[f'lag {i}' for i in range(real_corr_values.shape[1])])
real_corr_values.drop(columns=['lag 0'], inplace=True)

#now select the significant p-values
data = loadmat(f'{path}/{measure}_{strategy}_{atlas_name}.mat')['pvals']
df = pd.DataFrame(data, index=variable, columns=[f'lag {i}' for i in range(data.shape[1])])
df.drop(columns=['lag 0'], inplace=True)
results = df.reset_index().melt(id_vars="index",value_vars=df.columns,var_name="lag", 
                                value_name="p-value")
results = results.rename(columns={"index": "variable"})
results = results[results['p-value'] < alpha]
results = results.sort_values(by="variable")

results['lag_number'] = results['lag'].str.extract('(\d+)').astype(int)
results['correlation'] = results.apply(lambda row: real_corr_values.at[row['variable'], f'lag {row["lag_number"]}'], axis=1)
results.drop(columns=['lag_number'], inplace=True)

#Save the results
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)
del data
del results

#For participation coefficient
measure = 'parti-coeff'

#compute the real correlation for the participation coefficientes
pc = loadmat(f'{atlas_path}/{task}/{strategy}/parti-coeff_{strategy}_{atlas_name}')['pc']
node_num = pc.shape[1]
real_corr_values = np.zeros((len(variable),lag_no,node_num))  # move outside of loop
for lag in range(lag_no):
    sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
    for node in range(len(pc)):
        corrs = sub_behav.corrwith(pd.Series(pc[:,node],name=str(node)), method='spearman')
        real_corr_values[:,lag,node] = corrs.values
real_corr_values = [real_corr_values[:, :, i] for i in range(real_corr_values.shape[2])]
for i in range(len(real_corr_values)):
    real_corr_values[i] = pd.DataFrame(real_corr_values[i], index=variable, columns=[f'lag {j}' for j in range(real_corr_values[i].shape[1])])
    real_corr_values[i].drop(columns=['lag 0'], inplace=True)


#now select the significant p-values
data = loadmat(f'{path}/{measure}_{strategy}_{atlas_name}_BHcorrected.mat')['data_BH']
data = [data[:, :, i] for i in range(data.shape[2])]
for i in range(len(data)):
    data[i] = pd.DataFrame(data[i], index=variable, columns=[f'lag {j}' for j in range(data[i].shape[1])])
    data[i].drop(columns=['lag 0'], inplace=True)

#select the results
all_results = []
for df, real_corr_df in zip(data, real_corr_values):
    results = df.reset_index().melt(id_vars="index", value_vars=df.columns, var_name="lag", value_name="p-value")
    results = results.rename(columns={"index": "variable"})
    results = results[results['p-value'] < alpha]
    results = results.sort_values(by="variable")

    results['lag_number'] = results['lag'].str.extract('(\d+)').astype(int)
    if not results.empty:
        results['correlation'] = results.apply(lambda row: real_corr_df.loc[row['variable'], f'lag {row["lag_number"]}'], axis=1)
    results.drop(columns=['lag_number'], inplace=True)

    all_results.append(results)

#concatenate the non-empty dataframes vertically
non_empty_dfs = []
for idx, df in enumerate(all_results):
    if not df.empty:
        df['node'] = idx
        non_empty_dfs.append(df)
if len(non_empty_dfs)>0:
    final_df = pd.concat(non_empty_dfs, ignore_index=True)
    final_df = pd.merge(final_df, atlas_info, left_on='node', right_index=True, how='left')
    final_df = final_df.drop(columns=['node', 'roi'])
else:
    final_df = pd.DataFrame(columns=['variable', 'lag', 'p-value', 'correlation', 'x', 'y', 'z', 'network'])

#Save the results
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        final_df.to_excel(writer, sheet_name=measure, index=False)
else:
    final_df.to_excel(savefile, sheet_name=measure, index=False)