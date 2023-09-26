
import glob, os, sys
import numpy as np
import pandas as pd

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
measure = 'reg-links' #'parti-coeff' 

#load atlas
if atlas_name=='seitzman-set1':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set1_info.xlsx')
    net_column = 'netName'
elif atlas_name=='seitzman-set2':
    atlas = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set2_info.xlsx')
    net_column = 'network'
    network_mapping = {0: 'unlabeled', 1: 'DefaultMode', 2: 'Visual', 3:'FrontoParietal',
                       4:'Strialtal Orbitofrontal Amygdalar', 5: 'Dorsal Attention', 7:'Ventral Attention',
                       8:'Salience', 9:'CinguloOpercular', 10: 'Somatosensor Dorsal',
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
    
    melted_result['betas'] = None
    for index, row in melted_result.iterrows():
        node = coeff_data.loc[(coeff_data['node'] == row['index'] + 1) & (coeff_data['X'] == row['variable']),:]
        if not node.empty:
            melted_result.at[index, 'betas'] = node['standardized_betas'].values[0]
    melted_result.set_index('index', inplace=True)
    
else:
    columns = list(file.columns)[1:17]
    
    selected_rows = file[(file[columns] != 0).any(axis=1)] #select only the significant values
    selected_rows['row'] = selected_rows['row']-1 #adjust MATLAB indexes to python indexes
    selected_rows['column'] = selected_rows['column']-1 #adjust MATLAB indexes to python indexes

    selected_networks = ['DefaultMode', 'FrontoParietal', 'CinguloOpercular']
    selected_rois = atlas[atlas['netName'].isin(selected_networks)]
    selected_rois.reset_index(inplace=True)
    
    selected_rows['row_coor'], selected_rows['col_coor'] = None, None
    for index, row in selected_rows.iterrows():
        roi_number = row['row'] # Find the number of roi in selected_rows[row]
        matching_roi = selected_rois.loc[roi_number] # Find the x, y, z values in selected_rois that match the number in the index
        if not matching_roi.empty:
            x = matching_roi['x']
            y = matching_roi['y']
            z = matching_roi['z']
            netname = matching_roi['netName']
        xyz_string = f"[{x}, {y}, {z}]"
        selected_rows.at[index, 'row_coor'] = xyz_string #replace the node with its coordinates
        selected_rows.at[index, 'row_net'] = netname # Write the netName in the column selected_rows[row_net]
        
        roi_number = row['column'] # Find the number of roi in selected_rows[row]
        matching_roi = selected_rois.loc[roi_number] # Find the x, y, z values in selected_rois that match the number in the index
        if not matching_roi.empty:
            x = matching_roi['x']
            y = matching_roi['y']
            z = matching_roi['z']
            netname = matching_roi['netName']
        xyz_string = f"[{x}, {y}, {z}]"
        selected_rows.at[index, 'col_coor'] = xyz_string #replace the node with its coordinates
        selected_rows.at[index, 'col_net'] = netname # Write the netName in the column selected_rows[row_net]
        
    
    table = pd.DataFrame(columns=selected_rows.columns) # Initialize an empty DataFrame to store the expanded rows

    for _, row in selected_rows.iterrows():
        non_zero_columns = [col for col in columns if row[col] != 0] 
    
        if non_zero_columns: # If there are non-zero elements in the row, create multiple rows for each non-zero column
            for col in non_zero_columns:
                new_row = row.copy()
                new_row['variable'] = col
                table = table.append(new_row, ignore_index=True)
    
    #Filling in the p-values
    table['p-value'] = table.apply(lambda row: row[row['variable']], axis=1)
    table.drop(columns=columns, inplace=True)
    
    #Fill in the standardized_betas
    table['betas'] = np.nan
    for index, row in table.iterrows():
        link = coeff_data.loc[(coeff_data['link'] == row['link']) & (coeff_data['X'] == row['variable']),:]
        if not link.empty:
            table.at[index, 'betas'] = link['standardized_betas'].values[0]
    
    table.drop(columns=['link'], inplace=True)