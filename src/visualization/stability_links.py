import pandas as pd

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/'
hypothesis = 'H2'
meas = 'parti-coeff'

main = pd.read_excel(f'{path}/{hypothesis}/24HMP-8Phys-Spike_HPF_seitzman-set1_finaltable.xlsx', sheet_name='reg-links')
other = pd.read_excel(f'{path}/{hypothesis}/24HMP-8Phys-4GSR-Spike_HPF_seitzman-set1_finaltable.xlsx', sheet_name='reg-links')

#Link stability
def edge_repr(row):
    node_from = (row['x_from'], row['y_from'], row['z_from'])
    node_to = (row['x_to'], row['y_to'], row['z_to'])
    return frozenset((node_from, node_to))

# Apply the function to each row and create sets of edges for both DataFrames
main_edges = set(main.apply(edge_repr, axis=1))
other_edges = set(other.apply(edge_repr, axis=1))

# Find the intersection (common edges)
common_edges = main_edges.intersection(other_edges)

# Convert the frozensets back to list of dicts to create a DataFrame
common_edges_list = [
    {'x_from': list(edge)[0][0], 'y_from': list(edge)[0][1], 'z_from': list(edge)[0][2],
     'x_to': list(edge)[1][0], 'y_to': list(edge)[1][1], 'z_to': list(edge)[1][2]}
    if len(edge) == 2 else
    {'x_from': list(edge)[0][0], 'y_from': list(edge)[0][1], 'z_from': list(edge)[0][2],
     'x_to': list(edge)[0][0], 'y_to': list(edge)[0][1], 'z_to': list(edge)[0][2]}
    for edge in common_edges
]

common_edges_df = pd.DataFrame(common_edges_list)

#global efficiency or participation coefficient stability

if hypothesis=='H1':
    network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'cingulo opercular', 4: 'somatomotor'}
if hypothesis=='H2':
    network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'somatomotor'}
if hypothesis=='H3':
    network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'cingulo opercular'}


main_p = pd.read_excel(f'{path}/{hypothesis}/{meas}_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-10_BHcorrected.xlsx')
main2_p = pd.read_excel(f'{path}/{hypothesis}/{meas}_24HMP-8Phys-Spike_HPF_seitzman-set2_thr-10_BHcorrected.xlsx')
other_p = pd.read_excel(f'{path}/{hypothesis}/{meas}_24HMP-8Phys-4GSR-Spike_HPF_seitzman-set1_thr-10_BHcorrected.xlsx')

def find_significant_p_values_mapped(df_list, threshold=0.05):
    results = []
    for i, df in enumerate(df_list):
        df_name = f"DataFrame_{i+1}"
        for col in df.columns:
            for idx, p_value in df[col].iteritems():
                if p_value < threshold:
                    mapped_index = network_mapping.get(idx+1, f"Index {idx}") #matlab-python index thingy
                    result = {"DataFrame": df_name, "Column": col, "Network": mapped_index, "P-Value": p_value}
                    # Get the corresponding p-values from the other dataframes
                    for j, other_df in enumerate(df_list):
                        if i != j:
                            other_df_name = f"DataFrame_{j+1}"
                            other_p_value = other_df.at[idx, col]
                            result[f"P-Value_{other_df_name}"] = other_p_value
                    results.append(result)
    return results

# Find significant p-values with network mapping
dataframes = [main_p, main2_p, other_p]
significant_p_values_mapped = find_significant_p_values_mapped(dataframes)
