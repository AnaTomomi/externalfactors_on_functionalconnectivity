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
from nltools.stats import isc, fdr, threshold
from nltools.mask import expand_mask, roi_to_brain

from sklearn.metrics import pairwise_distances

from nilearn.plotting import plot_glass_brain

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data_movie, nearest_neighbors, anna_karenina
###############################################################################
# Input variables: modify these accordingly
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/'

savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H4_movie'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
scrub = 'soft'
thr = 0.2 #scrubbing threshold FD>scrub_thr
percent = 0.1
task = 'movie'
n_per = 10000
compute_isc =True
compute_mantel=True
###############################################################################

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
else:
    with open(idc_result_file, 'r') as f:
        isc_result = json.load(f)
        isc_r = isc_result[0]
        isc_p = isc_result[1]

mask = Brain_Data(group_atlas)
mask_x = expand_mask(mask)
isc_r_brain, isc_p_brain = roi_to_brain(pd.Series(isc_r), mask_x), roi_to_brain(pd.Series(isc_p), mask_x)
thr_fdr = fdr(isc_p_brain.data)
result = threshold(isc_r_brain, isc_p_brain, thr=thr_fdr).to_nifti()
#plot_glass_brain(result, colorbar=True)

# 2. Load the behavioral data
behav = get_behav_data_movie(behav_path, lag=1)

normalized_data = (behav - behav.mean()) / behav.std() #normalize by z-score
normalized_data.dropna(axis=1, inplace=True) #discard those values with no variation at all

nn = nearest_neighbors(normalized_data) #compute the educlidean distance
nn = Adjacency(nn, matrix_type='similarity')
ak = anna_karenina(normalized_data) #compute the Anna Karenina distance
ak = Adjacency(ak, matrix_type='similarity')

# 3. Compute the Mantel tests
mantel_nn_file = f'{savepath}/mantel-nn_{strategy}_{atlas_name}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.json'
mantel_ak_file= f'{savepath}/mantel-ak_{strategy}_{atlas_name}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.json'

if atlas_name=='seitzman-set1':
    atlas_info = pd.read_excel('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/300MNI_Power.xlsx')
    atlas_info = atlas_info[atlas_info['netName'].isin(['DefaultMode', 'FrontoParietal', 'Salience'])]
    selected_rois = atlas_info.roi.to_frame()
else:
    atlas_info = pd.read_excel('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman-gordon.xlsx')


if compute_mantel==True:
    brain_data = np.array([df.values for df in all_ts])
    brain_data = brain_data[:, :, selected_rois.index.to_list()]
    n_rois = brain_data.shape[2]
    
    brain_sim = []
    for node in range(n_rois):
        brain_sim.append(Adjacency(1 - pairwise_distances(brain_data[:, :, node], metric='correlation'), matrix_type='similarity'))
    brain_sim = Adjacency(brain_sim)

    isrsa_nn_r, isrsa_nn_p = {}, {}
    isrsa_annak_r, isrsa_annak_p = {}, {}
    for node in range(len(brain_sim)):
        if node==0:
            print("Doing node {} of {}...".format(node+1, len(brain_sim)), end =" ")
        else:
            print("{}..".format(node+1), end = " ")
        stats_nn = brain_sim[node].similarity(nn, metric='spearman', n_permute=n_per, n_jobs=-1 )
        isrsa_nn_r[node] = stats_nn['correlation']
        isrsa_nn_p[node] = stats_nn['p']
    
        stats_annak = brain_sim[node].similarity(ak, metric='spearman', n_permute=n_per, n_jobs=-1 )
        isrsa_annak_r[node] = stats_annak['correlation']
        isrsa_annak_p[node] = stats_annak['p']
        
    mantel_nn_result = [isrsa_nn_r, isrsa_nn_p]
    with open(mantel_nn_file, 'w') as f:
        json.dump(mantel_nn_result, f)
        
    mantel_ak_result = [isrsa_annak_r, isrsa_annak_p]
    with open(mantel_ak_file, 'w') as f:
        json.dump(mantel_ak_result, f)
else:
    with open(mantel_nn_file, 'r') as f:
        mantel_nn_result = json.load(f)
        isrsa_nn_r = mantel_nn_result[0]
        isrsa_nn_p = mantel_nn_result[1]
    with open(mantel_ak_file, 'r') as f:
        mantel_ak_result = json.load(f)
        isrsa_ak_r = mantel_ak_result[0]
        isrsa_ak_p = mantel_ak_result[1]

'''isrsa_nn_r_brain = roi_to_brain(pd.Series(isrsa_nn_r), expand_mask(mask))
isrsa_nn_p_brain = roi_to_brain(pd.Series(isrsa_nn_p), expand_mask(mask))

isrsa_annak_r_brain = roi_to_brain(pd.Series(isrsa_annak_r), expand_mask(mask))
isrsa_annak_p_brain = roi_to_brain(pd.Series(isrsa_annak_p), expand_mask(mask))

fdr_thr = fdr(pd.Series(isrsa_nn_p).values)
print(f'FDR Threshold: {fdr_thr}')'''

#view_img(threshold(isrsa_nn_r_brain, isrsa_nn_p_brain, thr=fdr_thr).to_nifti())