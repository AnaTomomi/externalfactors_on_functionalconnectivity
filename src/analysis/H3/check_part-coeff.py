#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 14:14:15 2023

@author: trianaa1
"""
import re
import glob
import numpy as np
import pandas as pd

import nibabel as nib

from nilearn.plotting import plot_glass_brain

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3'

atlas_info = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_seitzman-set1_info.xlsx')
atlas_info = atlas_info[atlas_info['netName'].isin(['DefaultMode', 'FrontoParietal', 'CinguloOpercular'])]
selected_rois = atlas_info.index.to_list()

files = sorted(glob.glob(path + f'/parti-coeff*.csv', recursive=True))
results = pd.DataFrame(columns=['Unnamed: 0', 't_values', 'p_values', 'r_squared', 'adj_r_squared',
                           'f_statistic', 'f_p_value', 'node'])

for file in files:
    node = re.search(r'node-(\d+)', file).group(1) if re.search(r'node-(\d+)', file) else None
    if int(node) in selected_rois:
        df = pd.read_csv(file)
        df = df.drop(0) #we don't care about the intercept
        significant = (df['p_values'] < 0.05).any()

        if significant:
            print(f'Significant result for {node}......')
            filtered_df = df[df['p_values'] < 0.05]
            filtered_df['node'] = node
            results = pd.concat([results, filtered_df])
            
results.rename(columns={'Unnamed: 0':'variable'}, inplace=True)

results.to_csv("/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3/parti-coeff_24HMP-8Phys-Spike_HPF_seitzman-set1_node-all.csv")

results_noteye = results.groupby('node').filter(lambda x: 'eye.resting' not in x['variable'].values)

# Plot
unique_variable = list(results['variable'].unique())
group_atlas = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/group_mask_seitzman-set1.nii'
atlas = nib.load(group_atlas)

for variable in unique_variable:
    df = results[results['variable']==variable]
    nodes = df['node'].unique().astype(int)
    selected_rois = atlas_info.loc[nodes]
    selected_rois = selected_rois['roi'].tolist()
    
    masked_result = np.round(atlas.get_fdata())
    mask = np.isin(masked_result, selected_rois, invert=True)
    masked_result[mask] = 0
    
    roi2plot = nib.Nifti1Image(masked_result, atlas.affine, atlas.header)
    plot_glass_brain(roi2plot, title=variable)
    
    print(variable, selected_rois)
    
    