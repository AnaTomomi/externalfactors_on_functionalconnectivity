"""
Utility functions that serve for creating the final tables and visualizations
of the data

@author: trianaa1
"""
import numpy as np
import pandas as pd

def lags_to_table(data, real_corr_values, variables, network_mapping, alpha, thr):
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