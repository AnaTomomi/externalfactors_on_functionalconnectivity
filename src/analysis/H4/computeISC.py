"""
This script computes the ISC maps and tests for significance according to 
(Chen et al., 2016). It also performs the Mantel tests for 

Chen et al., 2016. Untangling the relatedness among correlations, part I: 
nonparametric approaches to inter-subject correlation analysis at the group 
level. NeuroImage, 142, 248-259.

@author: trianaa1
"""
import sys
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat
import json

from nltools.data import Brain_Data, Adjacency
from nltools.stats import isc, fdr, threshold, holm_bonf
from nltools.mask import expand_mask, roi_to_brain

from sklearn.metrics import pairwise_distances

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_movie, nearest_neighbors, anna_karenina
###############################################################################
# Input variables: modify these accordingly
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/'

savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H4'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = sys.argv[1]
scrub = sys.argv[2]
thr = 0.2 #scrubbing threshold FD>scrub_thr
percent = sys.argv[5]
task = 'movie'
variable = sys.argv[3]
specific = sys.argv[4]
n_per = 10000
compute_isc =False
compute_mantel=True
##############################################################################

#Load the data
group_atlas = f'{conn_path}/group_mask_{atlas_name}.nii'
all_ts = loadmat(f'{conn_path}/{strategy}/scrubbed_{strategy}_{atlas_name}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.mat')['scrubbed'][0]
all_ts = [pd.DataFrame(matrix) for matrix in all_ts]

# 0. Organize the data as TRs x subjects x ROIs
n_trs = all_ts[0].shape[0]
n_rois = all_ts[0].shape[1]
n_sub = len(all_ts)
data =  np.empty((n_trs, n_sub, n_rois))
for i, df in enumerate(all_ts):
    data[:, i, :] = df.values

# 1. compute ISC maps
idc_result_file = f'{savepath}/idc_{strategy}_{atlas_name}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.json'
if compute_isc==True:
    isc_r, isc_p = {}, {}
    for roi in range(n_rois):
        idc = isc(data[:,:,roi], metric='median', method='bootstrap', n_bootstraps=n_per, return_bootstraps=True)
        isc_r[roi], isc_p[roi] = idc['isc'], idc['p']
        print(roi)

    isc_result = [isc_r, isc_p]
    with open(idc_result_file, 'w') as f:
        json.dump(isc_result, f)

# 2.bt Load the behavioral data
behav = get_behav_data_movie(behav_path, variable, lag=1)
if specific != 'all':
    behav = behav[[specific]]

nn = nearest_neighbors(behav) #compute the educlidean distance
nn = Adjacency(nn, matrix_type='similarity')
ak = anna_karenina(behav) #compute the Anna Karenina distance
ak = Adjacency(ak, matrix_type='similarity')

# 3. Compute the Mantel tests
mantel_nn_file = f'{savepath}/mantel-nn_{strategy}_{atlas_name}_{variable}-{specific}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.json'
mantel_ak_file= f'{savepath}/mantel-ak_{strategy}_{atlas_name}_{variable}-{specific}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.json'

# Select only for the pre-registered rois
if atlas_name=='seitzman-set1':
    atlas_info = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_seitzman-set1_info.xlsx')
    atlas_info = atlas_info[atlas_info['netName'].isin(['DefaultMode', 'FrontoParietal', 'Salience'])]
else:
    atlas_info = pd.read_excel('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_seitzman-set2_info.xlsx')
    atlas_info = atlas_info[atlas_info['network'].isin([1,3,8])]
    
selected_rois = atlas_info.index.to_frame()
selected_rois = selected_rois.index.to_list()

if compute_mantel==True:
    brain_data = np.array([df.values for df in all_ts])
    brain_data = brain_data[:, :, selected_rois]
    n_rois = brain_data.shape[2]
    
    brain_sim = []
    for node in range(n_rois):
        brain_sim.append(Adjacency(1 - pairwise_distances(brain_data[:, :, node], metric='correlation'), matrix_type='similarity'))
    brain_sim = Adjacency(brain_sim)

    isrsa_nn_r, isrsa_nn_p = {}, {}
    isrsa_ak_r, isrsa_ak_p = {}, {}
    for node in range(len(brain_sim)):
        if node==0:
            print("Doing node {} of {}...".format(node+1, len(brain_sim)), end =" ")
        else:
            print("{}..".format(node+1), end = " ")
        cur_roi = selected_rois[node] #just for saving purposes
        stats_nn = brain_sim[node].similarity(nn, metric='spearman', n_permute=n_per, n_jobs=-1 )
        isrsa_nn_r[cur_roi] = stats_nn['correlation']
        isrsa_nn_p[cur_roi] = stats_nn['p']
    
        stats_ak = brain_sim[node].similarity(ak, metric='spearman', n_permute=n_per, n_jobs=-1 )
        isrsa_ak_r[cur_roi] = stats_ak['correlation']
        isrsa_ak_p[cur_roi] = stats_ak['p']
        
    mantel_nn_result = [isrsa_nn_r, isrsa_nn_p]
    with open(mantel_nn_file, 'w') as f:
        json.dump(mantel_nn_result, f)
        
    mantel_ak_result = [isrsa_ak_r, isrsa_ak_p]
    with open(mantel_ak_file, 'w') as f:
        json.dump(mantel_ak_result, f)

fdr_nn_thr = fdr(pd.Series(isrsa_nn_p).values)
print(f'\n FDR NN Threshold: {fdr_nn_thr}')
print(min(isrsa_nn_p.values()))
fdr_ak_thr = fdr(pd.Series(isrsa_ak_p).values)
print(f'FDR AK Threshold: {fdr_ak_thr}')
print(min(isrsa_ak_p.values()))
