import pandas as pd
from scipy.io import loadmat

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'
hypothesis = 'H7'
measure = 'parti-coeff'

def convert_array_to_dfs(array, mapping, variables):
    """
    Convert a numpy array of shape (n, 16, m) to a list of m DataFrames of shape (n, 16).

    Parameters:
    array (np.ndarray): Input numpy array of shape (n, 16, m).
    mapping (dict): Mapping of indices to DataFrame names.
    variables (list): List of variable names for DataFrame indices.

    Returns:
    list: List of m DataFrames.
    """
    n, _, m = array.shape
    dataframes = []

    for i in range(m):
        df = pd.DataFrame(array[:, :, i], columns=[f"lag_{j}" for j in range(16)], index=variables)
        df.name = mapping.get(i, f"DataFrame_{i}")
        dataframes.append(df)

    return dataframes

if measure == 'parti-coeff':
    name = 'pcs'
else:
    name = 'effs'
    
if hypothesis=='H5':
    network_mapping = {0: 'default mode',1: 'fronto parietal',2: 'cingulo opercular', 3: 'somatomotor'}
    variables = ["total_sleep_duration", "awake_time", "restless_sleep"]
if hypothesis=='H6':
    network_mapping = {0: 'default mode',1: 'fronto parietal',2: 'somatomotor'}
    variables = ["total_sleep_duration", "awake_time", "restless_sleep", "steps", "inactive_time"]
if hypothesis=='H7':
    network_mapping = {0: 'default mode',1: 'fronto parietal',2: 'cingulo opercular'}
    variables = ['total_sleep_duration','awake_time','restless_sleep','pa_mean','pa_std', 'na_mean',
     'stress_mean','pain_mean','mean_respiratory_rate_brpm', 'min_respiratory_rate_brpm',
     'max_respiratory_rate_brpm','mean_prv_rmssd_ms', 'min_prv_rmssd_ms','max_prv_rmssd_ms']

main = loadmat(f'{path}/{hypothesis}/{measure}_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-10_BHcorrected.mat')['data_BH']
main[main>0.05] = 0
main[main!=0] = 1

twenty = loadmat(f'{path}/{hypothesis}/{measure}_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-20_BHcorrected.mat')['data_BH']
twenty[twenty>0.05] = 0
twenty[twenty!=0] = 1

thirty = loadmat(f'{path}/{hypothesis}/{measure}_24HMP-8Phys-Spike_HPF_seitzman-set1_thr-30_BHcorrected.mat')['data_BH']
thirty[thirty>0.05] = 0
thirty[thirty!=0] = 1

glo_sig = loadmat(f'{path}/{hypothesis}/{measure}_24HMP-8Phys-4GSR-Spike_HPF_seitzman-set1_thr-10_BHcorrected.mat')['data_BH']
glo_sig[glo_sig>0.05] = 0
glo_sig[glo_sig!=0] = 1

parcel = loadmat(f'{path}/{hypothesis}/{measure}_24HMP-8Phys-Spike_HPF_seitzman-set2_thr-10_BHcorrected.mat')['data_BH']
parcel[parcel>0.05] = 0
parcel[parcel!=0] = 1

stab_thres = main+twenty+thirty+glo_sig+parcel
stab_thres = convert_array_to_dfs(stab_thres,network_mapping,variables)
