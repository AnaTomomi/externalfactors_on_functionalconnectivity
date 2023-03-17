import glob, os
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker

from sklearn.linear_model import LinearRegression

###############################################################################
# Input variables: modify these accordingly

nii_path = '/m/cs/scratch/networks-pm/pm_denoise/'
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/rs-conn'
strategy = '24HMP-8Phys-Spike_HPF'
atlas_name = 'seitzman-set1'
vol_size = [91,109,91]

###############################################################################
# Helper function
def list2mat(a):
    b = np.empty((len(a),), dtype=object)
    for i in range(len(a)):
        b[i] = a[i]  
    return b

###############################################################################

#Make a list of files, subjects to preprocess
files = sorted(glob.glob(nii_path + f'/**/*resting_*{strategy}.nii', recursive=True))

#Clip and scrub the images
for file in files:
    head, tail = os.path.split(file)
    subject = tail[0:6]
    scrubbed_file = f'{conn_path}/scrubbed/{tail[:-4]}_scrubbed.nii'
    
    if not os.path.exists(scrubbed_file):
        #Read the image
        nii = nib.load(file)
    
        #discard the first 30 seconds of data. 30s*0.594TR = 50.50vols. Therefore, we need
        #to discard 51 vols, but we have already cut 5 in step 4. So, we need to cut 46 vols
        #and then get 10 minutes of the data (i.e. 1011vols*0.594TR=600.534 seg)
        cropped_nii = nii.slicer[:,:,:,46:1057]

        #Read the FD of the image
        confound = pd.read_csv(f'{fmriprep_path}{subject}/func/{subject}_task-resting_desc-confounds_timeseries.tsv', sep='\t')
        fd = confound['framewise_displacement'][51:1062]
        fd = fd.to_frame().reset_index()
    
        #detect FD>0.2 to scrub
        idx = fd[fd['framewise_displacement'].gt(0.2)].index.to_numpy()
        print(f'{len(idx)} vols scrubbed')
    
        #scrub
        mask = np.ones(len(fd),dtype=bool)
        mask[idx]=False
        data = cropped_nii.get_fdata()
        scrubbed = data[:,:,:,mask]
        scrubbed_nii = nib.Nifti1Image(scrubbed, nii.affine, nii.header)
        nib.save(scrubbed_nii,f'{conn_path}/scrubbed/{tail[:-4]}_scrubbed.nii')
        print(f'scrubbing for {scrubbed_file} done!')
    else:
        print(f'{scrubbed_file} already exists, no scrubbing done')
    
#Compute the group mask
group_mask_mult_name = f'{conn_path}/group_mask_mult.nii'
group_mask_sum_name = f'{conn_path}/group_mask_sum95.nii'
if not os.path.exists(group_mask_mult_name) or not os.path.exists(group_mask_sum_name):
    files = sorted(glob.glob(conn_path + "/scrubbed/*.nii*", recursive=True))
    group_mask_mult = np.ones(vol_size)
    group_mask_sum = np.zeros(vol_size)
    for file in files:
        head, tail = os.path.split(file)
        subject = tail[0:6]
        mask = nib.load(f'{fmriprep_path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii')
        data = mask.get_fdata()
        group_mask_mult = group_mask_mult*data
        group_mask_sum = group_mask_sum+data
    thr = np.amax(group_mask_sum)*0.95
    group_mask_sum[group_mask_sum<thr] = 0 #set values that are not in the 95% percentile of the mask to zero
    # i.e. if a voxel is in 95% of the cases, it stays
    group_mask_sum[group_mask_sum>0] = 1

    group_mask_nii = nib.Nifti1Image(group_mask_mult, mask.affine, mask.header)
    nib.save(group_mask_nii,group_mask_mult_name)
    group_mask_nii = nib.Nifti1Image(group_mask_sum, mask.affine, mask.header)
    nib.save(group_mask_nii,group_mask_sum_name)
    print(f'Group mask computed for {len(files)} files')
    
#Multiply the group mask by the atlas
if atlas_name=='seitzman-set1':
    atlas = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set1.nii'
elif atlas_name=='seitzman-set2':
    atlas = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set2.nii'
    
gmask = nib.load(group_mask_sum_name)
gmask_data = gmask.get_fdata()
atlas_nii = nib.load(atlas)
atlas_data = atlas_nii.get_fdata()
atlas_data = np.reshape(atlas_data, vol_size)

atlas_mask = gmask_data*atlas_data
atlas_mask_nii = nib.Nifti1Image(atlas_mask, atlas_nii.affine, atlas_nii.header)
masked_atlas = f'{conn_path}/group_mask_{atlas_name}.nii'
nib.save(atlas_mask_nii,masked_atlas)
print(f'Masked {atlas_name} atlas with group mask')

#Average ROI time series
masker = NiftiLabelsMasker(labels_img=masked_atlas, standardize=True)
files = sorted(glob.glob(conn_path + f'/scrubbed/*{strategy}*.nii*', recursive=True))
roi_ts_file = f'{conn_path}/averaged_roits_{strategy}_{atlas_name}.mat'
all_ts = []
for file in files:
    head, tail = os.path.split(file)
    print(f'Creating node time series for {file}')
    time_series = masker.fit_transform(file)
    all_ts.append(time_series)
    rs_ts = list2mat(all_ts)
savemat(roi_ts_file, {'rs_ts':rs_ts})

#Compute the adjacency matrices and apply Fisher transform
all_ts = [pd.DataFrame(ts) for ts in all_ts]
con = [ts.corr(method='pearson') for ts in all_ts]
for df in con:
    np.fill_diagonal(df.values,0) #set diagonal values to zero to avoid self-loops
fisher = [np.arctanh(matrix.values) for matrix in con]

#Compute mean FD
mean_fd = []
for file in files:
    head, tail = os.path.split(file)
    subject = tail[0:6]
    confound = pd.read_csv(f'{fmriprep_path}{subject}/func/{subject}_task-resting_desc-confounds_timeseries.tsv', sep='\t')
    fd = confound['framewise_displacement'][51:1062].mean()
    mean_fd.append(fd)
mean_fd = np.array(mean_fd).reshape(-1,1)

#Regress mean FD for all links
clf = LinearRegression(fit_intercept=True)
x = mean_fd

regressed = [np.zeros_like(matrix) for matrix in fisher]
idx = np.triu_indices(len(fisher[0]),1) #gets two lists of indexes, idx[0] = rows and idx[1] = columns
idx = np.stack((idx[0], idx[1]), axis=1)
for ind in range(len(idx)):
    i = idx[ind,0]
    j = idx[ind,1]
    y = []
    for matrix in fisher:
        y.append(matrix[i][j]) #organize link i-j for the different days (subjects)
    y = np.array(y)
    #Regress the mean FD from the links
    clf.fit(x,y)
    betas = clf.coef_
    regressed_links = y-np.dot(x,betas)-np.ones(len(y))*clf.intercept_
    for sub, link in enumerate(regressed_links):
        regressed[sub][i][j] = link #re-organize links into matrices
                
#Inverse Fisher
inv_fisher = [np.tanh(matrix) for matrix in regressed]
conn = list2mat(inv_fisher)

#Save the connectivity matrices
conn_file = f'{conn_path}/rs-adj_{strategy}_{atlas_name}.mat'
savemat(conn_file, {'conn':conn})