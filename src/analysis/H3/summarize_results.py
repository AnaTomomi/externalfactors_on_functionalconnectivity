
import glob, os, sys
import numpy as np
import pandas as pd

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set2'
measure = 'reg-links' #'parti-coeff' 


#load atlas
if atlas_name=='seitzman-set1':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set1_info.xlsx')
    net_column = 'netName'
elif atlas_name=='seitzman-set2':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set2_info.xlsx')
    net_column = 'network'

#load the data
file = pd.read_excel(f'{path}/{measure}_{strategy}_{atlas_name}_BHcorrected.xlsx')

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

    # Drop the original 'index' column and rename '[x, y, z]' to 'index'
    melted_result.set_index('index', inplace=True)
else:
    file.set_index('node', inplace=True)
    columns = list(file.columns)
    
    melted_result = file.melt(id_vars=['index'], value_vars=columns, var_name='variable', 
                      value_name='p-value')
    melted_result = melted_result[melted_result['p-value'] != 0]