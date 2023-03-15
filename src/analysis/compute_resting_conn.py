import glob, os
import numpy as np
import pandas as pd
from scipy.io import savemat

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure

###############################################################################
# Input variables: modify these accordingly

nii_path = '/m/cs/scratch/networks-pm/pm_denoise/'
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/rs-conn'
atlas_name = 'seitzman-set1'
vol_size = [91,109,91]

###############################################################################

#Make a list of files, subjects to preprocess
files = glob.glob(nii_path + "/**/*resting_*HPF.nii", recursive=True)

#Clip and scrub the images
for file in files:
    head, tail = os.path.split(file)
    subject = tail[0:6]
    scrubbed_file = f'{conn_path}/intermediate-files/scrubbed/{tail[:-4]}_scrubbed.nii'
    
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
        nib.save(scrubbed_nii,f'{conn_path}/intermediate-files/scrubbed/{tail[:-4]}_scrubbed.nii')
        print(f'scrubbing for {scrubbed_file} done!')
    else:
        print(f'{scrubbed_file} already exists, no scrubbing done')
    
#Compute the group mask
group_mask_name = f'{conn_path}/intermediate-files/group_mask.nii'
if not os.path.exists(group_mask_name):
    files = glob.glob(conn_path + "/intermediate-files/scrubbed/*.nii*", recursive=True)
    group_mask = np.ones(vol_size)
    for file in files:
        head, tail = os.path.split(file)
        subject = tail[0:6]
        mask = nib.load(f'{fmriprep_path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii')
        data = mask.get_fdata()
        group_mask = group_mask*data

    group_mask_nii = nib.Nifti1Image(group_mask, mask.affine, mask.header)
    nib.save(group_mask_nii,group_mask_name)
    print(f'Group mask computed for {len(files)} files')
    
#Multiply the group mask by the atlas
if atlas_name=='seitzman-set1':
    atlas = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set1.nii'
elif atlas_name=='seitzman-set2':
    atlas = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set2.nii'
    
gmask = nib.load(group_mask_name)
gmask_data = gmask.get_fdata()
atlas_nii = nib.load(atlas)
atlas_data = atlas_nii.get_fdata()
atlas_data = np.reshape(atlas_data, vol_size)

atlas_mask = gmask_data*atlas_data
atlas_mask_nii = nib.Nifti1Image(atlas_mask, atlas_nii.affine, atlas_nii.header)
masked_atlas = f'{conn_path}/intermediate-files/group_mask_{atlas_name}.nii'
nib.save(atlas_mask_nii,masked_atlas)
print(f'Masked {atlas_name} atlas with group mask')

#Average ROI time series
masker = NiftiLabelsMasker(labels_img=masked_atlas, standardize=True)
files = glob.glob(conn_path + "/intermediate-files/scrubbed/*.nii*", recursive=True)
for file in files:
    head, tail = os.path.split(file)
    outfile = f'{conn_path}/roi-ts/{tail[:-4]}_{atlas_name}.csv'
    if os.path.exists(outfile):
        print(f'Node time series file for {file} already exists!')
    else:
        print(f'Creating node time series for {file} in {outfile}')
        time_series = masker.fit_transform(file)
        pd.DataFrame(time_series).to_csv(outfile, index=False, header=False)

#Compute the adjacency matrices and apply Fisher transform

#Regress mean FD

#Inverse Fisher

#Save the connectivity matrices