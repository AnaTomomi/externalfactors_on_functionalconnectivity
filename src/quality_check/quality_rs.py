#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 15:55:48 2023

@author: trianaa1
"""
import numpy as np
import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt

###############################################################################

conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'

strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'

data = loadmat(f'{conn_path}/{strategy}/reg-adj_{strategy}_{atlas_name}.mat')['conn'][0]
data = [pd.DataFrame(array) for array in data]

for i in range(len(data)):
    df = data[i]
    np_array = df.to_numpy()  # Convert DataFrame to numpy array
    upper_triangle = np.triu(np_array)  # Extract upper triangular part
    lower_triangle = upper_triangle.T  # Transpose to get lower triangular part
    symmetric_matrix = upper_triangle + lower_triangle - np.diag(np.diag(upper_triangle))
    data[i] = pd.DataFrame(symmetric_matrix)
    
fig, axes = plt.subplots(5, 6, figsize=(15, 12))
axes = axes.flatten()

for i, (df, ax) in enumerate(zip(data, axes)):
    # Convert DataFrame to NumPy array for plotting
    np_array = df.to_numpy()
    limit = max(np.min(np_array),np.max(np_array))
    # Create the heatmap for each DataFrame
    cax = ax.imshow(np_array, cmap='bwr', aspect='equal', vmin=-limit, vmax=limit)
    
    # Optional: Add title, colorbar etc.
    ax.set_title(f"session {i+1}")
    fig.colorbar(cax, ax=ax, orientation='vertical')

# Remove any remaining empty subplots
for ax in axes[len(data):]:
    ax.axis('off')

plt.tight_layout()
plt.savefig(f'{savepath}/quality_rs.pdf', dpi=300)