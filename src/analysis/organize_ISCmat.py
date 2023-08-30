"""
This script organizes the time-series to be passed on to the ISCstats toolbox.
It also computes the ISC maps and tests for significance according to 
(Chen et al., 2016).

Chen et al., 2016. Untangling the relatedness among correlations, part I: 
nonparametric approaches to inter-subject correlation analysis at the group 
level. NeuroImage, 142, 248-259.

@author: trianaa1
"""

import glob, os, sys
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn.plotting import plot_glass_brain

from brainiak.isc import isc, compute_summary_statistic

from nltools.data import Brain_Data
from nltools.stats import isc, fdr, threshold
from nltools.mask import expand_mask, roi_to_brain


sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import list2mat, compute_groupmasks, compute_averagedROIts

###############################################################################
# Input variables: modify these accordingly

nii_path = '/m/cs/scratch/networks-pm/pm_denoise/'
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
vol_size = [91,109,91]
cuts = [47, 1018]
scrub = 'hard'
thr = 0.2 #scrubbing threshold FD>scrub_thr
percent = 0.05
task = 'movie'
n_per = 10000
###############################################################################

# 1. compute the group masks
group_atlas = compute_groupmasks(conn_path, fmriprep_path, task, vol_size, atlas_name)

# 2. compute the averaged-ROI timeseries
roi_ts_file = compute_averagedROIts(nii_path, conn_path, task, strategy, group_atlas)

# 3. cut away the washout parts
all_ts = loadmat(roi_ts_file)['rs_ts'][0]
all_ts = [pd.DataFrame(ts) for ts in all_ts]
all_ts = [df.loc[cuts[0]:cuts[1]] for df in all_ts]

# 4. scrub the timeseries according to the FD
subjects = ['sub-{0:02d}'.format(i) for i in range(1, 31)]

#First, we need to know what volumes will be scrubbed from all images
fds = []
for subject in subjects:    
    #Read the FD of the image
    confound = pd.read_csv(f'{fmriprep_path}{subject}/func/{subject}_task-movie_desc-confounds_timeseries.tsv', sep='\t')
    fd = confound['framewise_displacement'].loc[cuts[0]:cuts[1]]
    fd = fd.to_frame()
    fd.rename(columns={'framewise_displacement':subject}, inplace=True)
    fds.append(fd)
fds = pd.concat(fds, axis=1)
    
if scrub=='hard':
    idx = fds.index[fds.gt(thr).any(axis=1)].tolist()
else:
    fds = fds.where((fds > thr).mean(axis=1) <= percent)
    idx = fds.index[fds.isna().any(axis=1)].tolist()

#Now we scrub the volumes
all_ts = [df.drop(index=idx) for df in all_ts]
print(f'{len(idx)} vols scrubbed')


# 5. compute the ISC 
idc_mean = isc(all_ts, pairwise=True, summary_statistic='median')

# 6. compute ISC maps
n_trs = all_ts[0].shape[0]
n_rois = all_ts[0].shape[1]
n_sub = len(all_ts)
data =  np.empty((n_trs, n_sub, n_rois))
for i, df in enumerate(all_ts):
    data[:, i, :] = df.values

isc_r, isc_p = {}, {}
for roi in range(n_rois):
   idc = isc(data[:,:,roi], metric='median', method='circle_shift', n_bootstraps=n_per, return_bootstraps=True)
   isc_r[roi], isc_p[roi] = idc['isc'], idc['p']
   print(roi)

mask = Brain_Data(masked_atlas)
mask_x = expand_mask(mask)
isc_r_brain, isc_p_brain = roi_to_brain(pd.Series(isc_r), mask_x), roi_to_brain(pd.Series(isc_p), mask_x)
isc_nii = isc_r_brain.to_nifti()
plot_glass_brain(isc_nii, colorbar=True)

from brainiak.isc import isc
data_braniak = data.transpose(0, 2, 1)
isc_output = isc(data, pairwise=True, summary_statistic=None, tolerate_nans=True)


