"""
This script summarizes the significant results for global efficiency, participation
coefficients, and selected links, organizing them and matching the results with
the node coordinates for H1

"""
import os
import pandas as pd

###############################################################################
# Change this!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H1'
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
task = 'pvt'
atlas_name = 'seitzman-set1'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
thres = ['thr-10', 'thr-20', 'thr-30']
alpha = 0.05
###############################################################################

#Define the file to save
savefile = f'{path}/{strategy}_{atlas_name}_finaltable.xlsx'
cols = ['total_sleep_duration','awake_time','restless_sleep']
network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'cingulo opercular', 4: 'somatomotor'}

#For global efficiency
measure = 'global-eff'
all_results=[]
for thr in thres:
    pc = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}.csv')
    pc.rename(columns={'Unnamed: 0':'variable'}, inplace=True)
    pc['variable'] = pc['variable'].str.replace(r'\d+$', '')

    data = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}_BHcorrected.xlsx')
    data = data.melt(id_vars=['net'], value_vars=cols,var_name='variable', value_name='p')
    data.sort_values(by=['net'], ascending=True, inplace=True)
    data = data[data['p']<alpha]

    results = pd.merge(data, pc, on=['net', 'variable'], how='left')
    results = results[['net', 'variable', 'standardized_betas', 'p']]
    results.rename(columns={'net':'network','variable':'external factor', 
                        'standardized_betas':'beta', 'p':'p-value'},inplace=True)
    results['beta'] = results['beta'].round(decimals=2)
    results.loc[:,'network'] = results['network'].map(network_mapping)
    results.loc[:, 'external factor'] = results['external factor'].str.replace('_', ' ')
    results['threshold'] = int(thr[-2:])/100
    all_results.append(results)
results = pd.concat(all_results)

if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)
del data
del results

#For participation coefficient
measure='parti-coeff'
all_results=[]
for thr in thres:
    pc = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}.csv')
    pc.rename(columns={'Unnamed: 0':'variable'}, inplace=True)
    pc['variable'] = pc['variable'].str.replace(r'\d+$', '')

    data = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_{thr}_BHcorrected.xlsx')
    data = data.melt(id_vars=['net'], value_vars=cols, var_name='variable', value_name='p')
    data.sort_values(by=['net'], ascending=True, inplace=True)
    data = data[data['p']<alpha]

    results = pd.merge(data, pc, on=['net', 'variable'], how='left')
    results = results[['net', 'variable', 'standardized_betas', 'p']]
    results.rename(columns={'net':'network','variable':'external factor', 
                        'standardized_betas':'beta', 'p':'p-value'},inplace=True)
    results['beta'] = results['beta'].round(decimals=2)
    results.loc[:,'network'] = results['network'].map(network_mapping)
    results.loc[:, 'external factor'] = results['external factor'].str.replace('_', ' ')
    results['threshold'] = int(thr[-2:])/100
    all_results.append(results)
results = pd.concat(all_results)

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
results = results[['variable', 'standardized_betas', 'p-value', 'x_from', 
                   'y_from', 'z_from', 'net_from', 'x_to', 'y_to', 'z_to', 
                   'net_to']]
results.rename(columns={'variable':'external factor', 'standardized_betas':'beta',
                        'net_from':'network_from','net_to':'network_to'},inplace=True)
results['beta'] = results['beta'].round(decimals=2)
results.loc[:, 'external factor'] = results['external factor'].str.replace('_', ' ')
if atlas_name == 'seitzman-set2':
    results['network_from'] = results['network_from'].replace({1:'default mode',3:'fronto parietal',9:'cingulo opercular',10:'somatomotor', 11:'somatomotor'})
    results['network_to'] = results['network_to'].replace({1:'default mode',3:'fronto parietal',9:'cingulo opercular',10:'somatomotor', 11:'somatomotor'})
results.loc[:,'network_from'] = results['network_from'].str.replace(r'([a-z])([A-Z])', r'\1 \2').str.lower()
results['network_from'] = results['network_from'].replace({'somatomotor dorsal': 'somatomotor', 
                                                           'somatomotor lateral': 'somatomotor'})
results.loc[:,'network_to'] = results['network_to'].str.replace(r'([a-z])([A-Z])', r'\1 \2').str.lower()
results['network_to'] = results['network_to'].replace({'somatomotor dorsal': 'somatomotor', 
                                                       'somatomotor lateral': 'somatomotor'})  
    
if os.path.exists(savefile):
    with pd.ExcelWriter(savefile, engine='openpyxl', mode='a') as writer:
        results.to_excel(writer, sheet_name=measure, index=False)
else:
    results.to_excel(savefile, sheet_name=measure, index=False)