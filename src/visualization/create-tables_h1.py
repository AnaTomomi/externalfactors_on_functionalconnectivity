"""
This script summarizes the significant results for global efficiency, participation
coefficients, and selected links, organizing them and matching the results with
the node coordinates for H1

"""
import os
import pandas as pd
import numpy as np

###############################################################################
# Change this!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H1'
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
task = 'pvt'
atlas_name = 'seitzman-set1'
strategy = '24HMP-8Phys-Spike_HPF'
alpha = 0.05
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

#For global efficiency
measure = 'global-eff'
data = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}.csv')
results = data[data['p_values'] < alpha][['Unnamed: 0', 'p_values', 'standardized_betas']]
results.columns = ['variable', 'p-value', 'standardized beta']
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)
del data
del results

#For participation coefficient
measure='parti-coeff'
pc = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}.csv')
pc['Unnamed: 0'] = pc['Unnamed: 0'].str.replace(r'\d+$', '')

data = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_BHcorrected.xlsx')
data = pd.concat([data, atlas_info], axis=1)
melted_data = pd.melt(data, id_vars=['x', 'y', 'z', 'network','node'],value_vars=data.columns[1:-5],
                      var_name='variable', value_name='p-value')
results = melted_data[melted_data['p-value'] < alpha].reset_index(drop=True)
results = pd.merge(results, pc[['node', 'Unnamed: 0', 'standardized_betas']], 
                  left_on=['node', 'variable'], right_on=['node', 'Unnamed: 0'], 
                  how='left')
results.drop(columns=['node', 'Unnamed: 0'],inplace=True)
results = results.sort_values(by=['x', 'y', 'z']).reset_index(drop=True)
results = results[['variable', 'standardized_betas', 'p-value', 'x', 'y', 'z', 'network']]
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)
del data
del results
    
#For links
measure='reg-links'
links = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}.csv')
links['Unnamed: 0'] = links['Unnamed: 0'].str.replace(r'\d+$', '')

data = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_BHcorrected.xlsx')   
melted_data = pd.melt(data, id_vars=['x_from', 'y_from', 'z_from', 'net_from',
                                     'x_to', 'y_to', 'z_to', 'net_to', 'link'],
                      value_vars=data.columns[1:4],
                      var_name='variable', value_name='p-value')
results = melted_data[melted_data['p-value'] < alpha].reset_index(drop=True)
results = pd.merge(results, links[['link', 'Unnamed: 0', 'standardized_betas']], 
                  left_on=['link', 'variable'], right_on=['link', 'Unnamed: 0'], 
                  how='left')
results.drop(columns=['link', 'Unnamed: 0'],inplace=True)
results = results[['variable', 'standardized_betas', 'p-value', 'x_from', 
                   'y_from', 'z_from', 'net_from', 'x_to', 'y_to', 'z_to', 'net_to']]

if atlas_name == 'seitzman-set2':
    results['net_from'] = results['net_from'].replace(network_mapping)
    results['net_to'] = results['net_to'].replace(network_mapping)
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)