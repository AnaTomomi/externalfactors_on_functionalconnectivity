"""
Utility functions that serve for creating the final tables and visualizations
of the data

@author: trianaa1
"""
import numpy as np
import pandas as pd

import netplotbrain as npb

from matplotlib.colors import LinearSegmentedColormap

def lags_to_table(data, real_corr_values, variables, network_mapping, alpha, thr):
    ''' This function organizes the correlation values and p-values 

    Parameters
    ----------
    data: numpy array, corrected p-values of shape (variables, lags, networks)
    real_corr_values: list of dataframes, correlation values based on the real data
                      Each dataframe's shape should be (variables,lags)
    variables: list of strings, the names of the variables for each hypothesis
    network_mapping: dict, keys should be the network number in which the results were
                     computed. The values are the names of the networks
    alpha: float, threshold for corrected p-values
    thr: str, network threshold

    Returns
    -------
    final_df: dataframe, listing the significant results with their correlation and p-values

    '''
    data = [data[:, :, i] for i in range(data.shape[2])]
    for i in range(len(data)):
        data[i] = pd.DataFrame(data[i], index=variables, columns=[f'lag {j}' for j in range(data[i].shape[1])])
        data[i].drop(columns=['lag 0'], inplace=True)

    #select the results
    all_results = []
    for df, real_corr_df in zip(data, real_corr_values):
        results = df.reset_index().melt(id_vars="index", value_vars=df.columns, var_name="lag", value_name="p-value")
        results = results.rename(columns={"index": "variable"})
        results = results[results['p-value'] < alpha]
        results = results.sort_values(by="variable")

        results['lag'] = results['lag'].str.extract('(\d+)').astype(int)
        if not results.empty:
            results['correlation'] = results.apply(lambda row: real_corr_df.loc[row['variable'], f'lag {row["lag"]}'], axis=1)

        all_results.append(results)

    #merge the results of all networks into one table
    non_empty_dfs = []
    for idx, df in enumerate(all_results):
        if not df.empty:
            df['network'] = idx+1 #networks are mapped according to MATLAB indexes
            non_empty_dfs.append(df)
            
    if len(non_empty_dfs)>0:
        final_df = pd.concat(non_empty_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=['network','external factor','lag','rho','p-value'])

    final_df.rename(columns={'variable':'external factor','correlation':'rho'},inplace=True)
    final_df.loc[:, 'external factor'] = final_df['external factor'].str.replace('_', ' ')
    final_df.loc[:,'network'] = final_df['network'].map(network_mapping)
    final_df = final_df[['network', 'external factor', 'lag', 'rho', 'p-value']]
    final_df['rho'] = final_df['rho'].round(decimals=2)
    final_df['p-value'] = final_df['p-value'].round(decimals=3)
    final_df['threshold'] = int(thr[-2:])/100
    
    return final_df

def format_data(data, variables):
    ''' This function formats the data depending on the variables. It makes a 
    list of numpy arrays into a list of dataframes, where each df has the 
    name of the variables (rows) and lags (columns)

    Parameters
    ----------
    data : list, with dataframes of the significant links once FDR corrected
    variables : list, of variable (external factors) names.

    Returns
    -------
    data: list, of dataframes with the FDR corrected data

    '''
    data = [data[:, :, i] for i in range(data.shape[2])]
    for i in range(len(data)):
        data[i] = pd.DataFrame(data[i], index=variables, columns=[f'lag {j}' for j in range(data[i].shape[1])])
        data[i].drop(columns=['lag 0'], inplace=True)
    return data

def plot_connectome_struct(df):
    ''' This function takes the organized information in tables and outputs the 
    needed parameters to plot the links in the plot_connectome function

    Parameters
    ----------
    df : pandas dataframe with the significant links that were generated from 
    running the create-tables_hX.py script

    Returns
    -------
    adjancency_matrix: array, adjacency matrix generated for the significant nodes
    node_coords: dict, node coordinates in x, y, and z for the included nodes
    node_colors: dict, node colors for the node_coords

    '''
    coord_to_id = {}
    coord_to_color = {}
    count = 0

    # Define the color mapping
    color_map = {'default mode': '#984ea3', 'somatomotor': '#f781bf', 
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
    
    return adjacency_matrix, node_coords, node_colors

def get_nodes_edges(factor_links):
    ''' This function takes the input factor_links (from the fnial tables) and
    creates two dataframes, one containing the nodes and one containing the edges.
    These will be used to plot the brain connections using netplotbrain.

    Parameters
    ----------
    factor_links : pandas dataframe with the significant links that were generated from
    running the visualize_tables.py script

    Returns
    -------
    nodes: dataframe, with the nodes and their coordinates
    edges: dataframe, with the edges and weights

    '''
    #colormapping
    color_mapping = {'default mode': 'fuchsia', 'cingulo opercular': 'cyan', 'fronto parietal': 'limegreen', 'somatomotor':'yellow'}
    
    #create the nodes and edges dataframe for netplotbrain
    nodes_from = factor_links[["x_from", "y_from", "z_from", "network_from"]].rename(columns={"x_from": "x", "y_from": "y", "z_from": "z", "network_from": "community"})
    nodes_to = factor_links[["x_to", "y_to", "z_to", "network_to"]].rename(columns={"x_to": "x", "y_to": "y", "z_to": "z", "network_to": "community"})
    nodes = pd.concat([nodes_from, nodes_to]).drop_duplicates().reset_index(drop=True)
    nodes['color'] = nodes['community'].map(color_mapping)
    
    edges = pd.DataFrame(columns=["i", "j", "weight"])
    for index, row in factor_links.iterrows():
        node_from = row[["x_from", "y_from", "z_from", "network_from"]].values
        node_to = row[["x_to", "y_to", "z_to", "network_to"]].values
        i = nodes[(nodes["x"] == node_from[0]) & (nodes["y"] == node_from[1]) & 
                  (nodes["z"] == node_from[2]) & (nodes["community"] == node_from[3])].index[0]
        j = nodes[(nodes["x"] == node_to[0]) & (nodes["y"] == node_to[1]) & 
                  (nodes["z"] == node_to[2]) & (nodes["community"] == node_to[3])].index[0]
        edges = edges.append({"i": i, "j": j, "weight": row["beta"]}, ignore_index=True)
    return nodes, edges

def plot_connectome(fig, external_factors, links, X):
    #general plotting settings
    colors = ['#4daf4a', '#984ea3', '#f781bf', '#ffff33']
    cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
    views=['L','S','R','P']
    
    for i, factor in enumerate(external_factors):
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        #plot 
        for j in range(4):
            ax = fig.add_subplot(X, 4, i*4+j+1, projection='3d')
            npb.plot(template='MNI152NLin2009cAsym',
                         template_style='glass', template_glass_maxalpha=0.05,
                         nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='community',
                         edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                         view=views[j], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
            
    return ax

def get_nodes_from_atlas(atlas_path, atlas_name, net):
    atlas_info = pd.read_excel(f'{atlas_path}/pvt/group_{atlas_name}_info.xlsx')
    if atlas_name=='seitzman-set1':
        atlas_info.drop(columns=['roi', 'radiusmm', 'integrativePercent', 'netWorkbenchLabel',
                           'Power', 'AnatomicalLabels'], inplace=True)
        atlas_info.rename(columns={'netName':'community'},inplace=True)
        mapping = {'SomatomotorDorsal':'somatomotor', 'SomatomotorLateral':'somatomotor',
                   'CinguloOpercular': 'cingulo opercular', 'DefaultMode':'default mode',
                   'FrontoParietal':'fronto parietal'}
        atlas_info['community'] = atlas_info['community'].replace(mapping)
    else:
        atlas_info.drop(columns=['gordon'], inplace=True)
        atlas_info.rename(columns={'network':'community'},inplace=True)
        mapping = {10:'somatomotor', 11:'somatomotor',
                   9: 'cingulo opercular', 1:'default mode',
                   3:'fronto parietal'}
        atlas_info['community'] = atlas_info['community'].replace(mapping)
        
    atlas_info = atlas_info[atlas_info.community == net]
    
    return atlas_info
        