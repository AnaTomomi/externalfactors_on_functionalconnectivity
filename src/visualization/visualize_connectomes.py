"""
Created on Mon Oct 30 17:11:31 2023

@author: trianaa1
"""
import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from nilearn import plotting

###############################################################################
# Change only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
###############################################################################

h1 = pd.read_excel(f'{path}/H1/{strategy}_{atlas_name}_finaltable.xlsx',sheet_name='reg-links')
h2 = pd.read_excel(f'{path}/H2/{strategy}_{atlas_name}_finaltable.xlsx',sheet_name='reg-links')

colors = ['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0',
          '#92c5de','#4393c3','#2166ac','#053061']
custom_cmap = ListedColormap(colors)

df = h2.copy()

coord_to_id = {}
coord_to_color = {}
count = 0

# Define the color mapping
color_map = {'default mode': '#4daf4a', 'somatomotor': '#984ea3', 
             'cingulo opercular': '#a65628', 'fronto parietal': '#000000'}

# Iterate over all the unique node coordinates, assign an ID and color
for _, row in df[['x_from', 'y_from', 'z_from', 'network_from']].drop_duplicates().iterrows():
    coord_tuple = (row['x_from'], row['y_from'], row['z_from'])
    coord_to_id[coord_tuple] = count
    coord_to_color[coord_tuple] = color_map[row['network_from']]
    count += 1

for _, row in df[['x_to', 'y_to', 'z_to', 'network_to']].drop_duplicates().iterrows():
    coord_tuple = (row['x_to'], row['y_to'], row['z_to'])
    if coord_tuple not in coord_to_id:
        coord_to_id[coord_tuple] = count
        coord_to_color[coord_tuple] = color_map[row['network_to']]
        count += 1

# Create an adjacency matrix of zeros
n_nodes = len(coord_to_id)
adjacency_matrix = np.zeros((n_nodes, n_nodes))

# Fill in the adjacency matrix using the data in the dataframe
for index, row in df.iterrows():
    from_id = coord_to_id[(row['x_from'], row['y_from'], row['z_from'])]
    to_id = coord_to_id[(row['x_to'], row['y_to'], row['z_to'])]
    # Using standardized_betas as connection strengths, modify as necessary
    adjacency_matrix[from_id, to_id] = row['beta']
    adjacency_matrix[to_id, from_id] = row['beta']

# Extract the node coordinates and node colors from the dictionaries
node_coords = [list(coord) for coord in coord_to_id.keys()]
node_colors = [coord_to_color[coord] for coord in coord_to_id.keys()]

# Plot the connectome
plotting.plot_connectome(adjacency_matrix, node_coords, node_size=70, node_color=node_colors,
                         edge_vmin=-1, edge_vmax=1,edge_cmap=custom_cmap, colorbar=True)