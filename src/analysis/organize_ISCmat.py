"""
This script computes the averaged-ROI ts for the movie data. It also performs 
the scrubbing and saves the matrices. 

@author: trianaa1
"""

import sys
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat

#from brainiak.isc import isc, compute_summary_statistic

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import list2mat, compute_groupmasks, compute_averagedROIts

###############################################################################
# Input variables: modify these accordingly

nii_path = '/m/cs/scratch/networks-pm/pm_denoise/'
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = 'seitzman-set1'
vol_size = [91,109,91]
cuts = [47, 1018]
scrub = 'soft'
thr = 0.2 #scrubbing threshold FD>scrub_thr
percent = 0.1
task = 'movie'
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

scrubbed = [df.values for df in all_ts]
scrubbed = list2mat(scrubbed)
scrubbed_file = f'{conn_path}/{strategy}/scrubbed_{strategy}_{atlas_name}_scrub-{scrub}_thr-{str(thr)}_per-{str(percent)}.mat'
savemat(scrubbed_file, {'scrubbed':scrubbed})