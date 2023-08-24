"""
This script organizes the time-series to be passed on to the ISCstats toolbox

@author: trianaa1
"""

import glob, os, sys
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker

from sklearn.linear_model import LinearRegression

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import compute_groupmasks, list2mat

###############################################################################
# Input variables: modify these accordingly

nii_path = '/m/cs/scratch/networks-pm/pm_denoise/'
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = 'seitzman-set1'
vol_size = [91,109,91]
cuts = [47, 1018]
scrub = 'hard'
thr = 0.2
percent = 0.1 
task = 'movie'

###############################################################################

files = sorted(glob.glob(nii_path + f'/**/*movie_*{strategy}.nii', recursive=True))

#Scrub the images

#First, we need to know what volumes will be scrubbed from all images
fds = []
for file in files:
    head, tail = os.path.split(file)
    subject = tail[0:6]
    
    #Read the FD of the image
    confound = pd.read_csv(f'{fmriprep_path}{subject}/func/{subject}_task-movie_desc-confounds_timeseries.tsv', sep='\t')
    fd = confound['framewise_displacement'].loc[cuts[0]:cuts[1]]
    fd = fd.to_frame()
    fd.rename(columns={'framewise_displacement':subject}, inplace=True)
    fds.append(fd)
fds = pd.concat(fds, axis=1)
fds.reset_index(inplace=True)
fds.drop(["index"], axis=1, inplace=True)
    
if scrub=='hard':
    idx = fds.index[fds.gt(thr).any(axis=1)].tolist()
else:
    fds = fds.where((fds > thr).mean(axis=1) <= percent)
    idx = fds.index[fds.isna().any(axis=1)].tolist()

#Now we scrub the volumes
for file in files:
    head, tail = os.path.split(file)
    subject = tail[0:6]
    if scrub=='hard':
        scrubbed_file = f'{conn_path}/{strategy}/{tail[:-4]}_scrubbed-{scrub}_{str(thr)}.nii'
    else:
        scrubbed_file = f'{conn_path}/{strategy}/{tail[:-4]}_scrubbed-{scrub}_{str(thr)}-{str(percent)}.nii'
    
    if not os.path.exists(scrubbed_file):
        #Read the image
        nii = nib.load(file)
        cropped_nii = nii.slicer[:,:,:,cuts[0]:cuts[1]+1]
    
        #scrub
        mask = np.ones(cropped_nii.shape[3],dtype=bool)
        mask[idx]=False
        data = cropped_nii.get_fdata()
        scrubbed = data[:,:,:,mask]
        scrubbed_nii = nib.Nifti1Image(scrubbed, nii.affine, nii.header)
        nib.save(scrubbed_nii,scrubbed_file)
        print(f'scrubbing for {scrubbed_file} done!')
    else:
        print(f'{scrubbed_file} already exists, no scrubbing done')

#Compute the group masks
masked_atlas = compute_groupmasks(conn_path, fmriprep_path, task, strategy, vol_size, atlas_name)

#Compute the averaged ROI-ts
masker = NiftiLabelsMasker(labels_img=masked_atlas, standardize=True)
files = sorted(glob.glob(conn_path + f'/{strategy}/*{strategy}*.nii*', recursive=True))
roi_ts_file = f'{conn_path}/{strategy}/averaged_roits_{strategy}_{atlas_name}_scrubbed-{scrub}_{str(thr)}-{str(percent)}.mat'
all_ts = []
if not os.path.exists(roi_ts_file):
    for file in files:
        head, tail = os.path.split(file)
        print(f'Creating node time series for {file}')
        time_series = masker.fit_transform(file)
        all_ts.append(time_series)
    rs_ts = list2mat(all_ts)
    savemat(roi_ts_file, {'rs_ts':rs_ts})
