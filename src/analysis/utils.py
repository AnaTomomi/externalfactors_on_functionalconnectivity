''' Helper functions to compute connectivity matrices 

author: trianaa1
'''

import glob, os
import numpy as np
from scipy.io import savemat, loadmat

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker

from sklearn.linear_model import LinearRegression


def list2mat(a):
    ''' converts lists of numpy arrays to formats that can be saved in 
    .mat files
    
    Parameters
    ----------
    a: list
    
    Returns
    -------
    b: numpy array
    '''
    
    b = np.empty((len(a),), dtype=object)
    for i in range(len(a)):
        b[i] = a[i]  
    return b


def compute_groupmasks(conn_path, fmriprep_path, task, vol_size, atlas_name):
    files = sorted(glob.glob(fmriprep_path + f'/**/func/*{task}_*mask.nii', recursive=True))
    
    group_mask_mult_name = f'{conn_path}/group_mask_mult.nii'
    group_mask_sum_name = f'{conn_path}/group_mask_sum95.nii'
    if not os.path.exists(group_mask_mult_name) or not os.path.exists(group_mask_sum_name):
        group_mask_mult = np.ones(vol_size)
        group_mask_sum = np.zeros(vol_size)
        for file in files:
            head, tail = os.path.split(file)
            subject = tail[0:6]
            if subject=='sub-09' and task =='resting':
                # sub-09 mask had a big cut in the frontal, superior part. Thus, the sub-09 was denoised with the PVT brain mask
                mask = nib.load(f'{fmriprep_path}/{subject}/func/{subject}_task-pvt_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii')
            elif subject=='sub-25' and task =='nback':
                # sub-25 mask had a big cut in the superior part. Thus, the sub-25 was denoised with the resting brain mask
                mask = nib.load(f'{fmriprep_path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii')
            else:
                mask = nib.load(f'{fmriprep_path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii')                
            
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

    masked_atlas = f'{conn_path}/group_mask_{atlas_name}.nii'

    if not os.path.exists(masked_atlas):
        gmask = nib.load(group_mask_mult_name)
        gmask_data = gmask.get_fdata()
        atlas_nii = nib.load(atlas)
        atlas_data = atlas_nii.get_fdata()
        atlas_data = np.reshape(atlas_data, vol_size)

        atlas_mask = gmask_data*atlas_data
        atlas_mask_nii = nib.Nifti1Image(atlas_mask, atlas_nii.affine, atlas_nii.header)
        
        nib.save(atlas_mask_nii,masked_atlas)
        print(f'Masked {atlas_name} atlas with group mask')
    return masked_atlas

def compute_averagedROIts(nii_path, conn_path, task, strategy, group_atlas):
    ''' computes the averaged-ROI timeseries based on a selected atlas. The 
    computations are done for all subjects in a folder.
    
    Parameters
    ----------
    nii_path: folder path to where the denoised files are
    conn_path: folder path to where the computations will be stored
    strategy: denoised strategy
    group_atlas: file path to the group mask multiplied by the selected atlas.
                 It should be a nii file
    
    Returns
    -------
    roi_ts_file: string with the path to the file containing the averaged-ROI 
                 time series for all subjects
    '''
    
    files = sorted(glob.glob(nii_path + f'/**/*{task}_*{strategy}.nii', recursive=True))
    atlas_name = os.path.basename(group_atlas).split('_')[-1].split('.nii')[0]
    roi_ts_file = f'{conn_path}/{strategy}/averaged_roits_{strategy}_{atlas_name}.mat'
    
    masker = NiftiLabelsMasker(labels_img=group_atlas, standardize=True)
    
    if not os.path.exists(roi_ts_file):
        all_ts = []
        if not os.path.exists(roi_ts_file):
            for file in files:
                head, tail = os.path.split(file)
                print(f'Creating node time series for {file}')
                time_series = masker.fit_transform(file)
                all_ts.append(time_series)
            rs_ts = list2mat(all_ts)
            savemat(roi_ts_file, {'rs_ts':rs_ts})
    return roi_ts_file
    
#TODO: def scrub_averagedROIts():