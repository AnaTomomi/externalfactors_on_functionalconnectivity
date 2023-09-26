
import glob, os, sys
import numpy as np
import pandas as pd

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set2'
measure = 'parti-coeff' #'parti-coeff' 


#load atlas
if atlas_name=='seitzman-set1':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set1_info.xlsx')
    net_column = 'netName'
elif atlas_name=='seitzman-set2':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set2_info.xlsx')
    net_column = 'network'
    network_mapping = {0: 'unlabeled', 1: 'DMN', 2: 'Visual', 3:'Frontoparietal',
                       4:'Strialtal Orbitofrontal Amygdalar', 5: 'Dorsal Attention', 7:'Ventral Attention',
                       8:'Salience', 9:'Cingulo Opercular', 10: 'Somatosensor Dorsal',
                       11:'Somatosensor Lateral', 12:'Auditory', 14:'Medital Temporal Lobe',
                       15:'Parietal Medial', 16:'Parietooccipital', 22:'Unknown'}
    atlas['network'] = atlas['network'].replace(network_mapping)

#load the data
file = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_BHcorrected.xlsx')
coeff_data = pd.read_csv(f'{path}/{measure}_{strategy}_{atlas_name}.csv')
coeff_data['X'] = coeff_data['X'].str.replace(r'\d+$', '', regex=True)

if measure == 'parti-coeff':
    file.reset_index(inplace=True)

    #Produce the table
    columns = list(file.columns)[2:]
    melted_result = file.melt(id_vars=['index'], value_vars=columns, var_name='variable', 
                      value_name='p-value')
    melted_result = melted_result[melted_result['p-value'] != 0]

    #Cross relate with the atlas info
    melted_result['[x, y, z]'] = melted_result['index'].apply(lambda idx: [atlas.loc[idx, 'x'], atlas.loc[idx, 'y'], atlas.loc[idx, 'z']])
    melted_result['network'] = melted_result['index'].apply(lambda idx: atlas.loc[idx, net_column])
    
    #Include the info about standard betas and confidence intervals
    melted_result['standardized_betas'] = None
    melted_result['CI_lower'] = None
    melted_result['CI_upper'] = None
    
    for index, row in melted_result.iterrows():
        node = coeff_data.loc[(coeff_data['node'] == row['index'] + 1) & (coeff_data['X'] == row['variable']),:]
        if not node.empty:
            melted_result.at[index, 'standardized_betas'] = node['standardized_betas'].values[0]
            melted_result.at[index, 'CI_lower'] = node['CI_lower'].values[0]
            melted_result.at[index, 'CI_upper'] = node['CI_upper'].values[0]

    # Drop the original 'index' column and rename '[x, y, z]' to 'index'
    melted_result.set_index('index', inplace=True)
else:
    file.set_index('node', inplace=True)
    columns = list(file.columns)
    
    melted_result = file.melt(id_vars=['index'], value_vars=columns, var_name='variable', 
                      value_name='p-value')
    melted_result = melted_result[melted_result['p-value'] != 0]