import os
import pandas as pd

from nilearn.input_data import NiftiLabelsMasker

path = '/m/cs/scratch/networks-pm/pm_denoise/' 
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/roi-ts'
atlas = 'seitzman-set2'

if atlas=='brainnetome':
    atlas_img = '/m/cs/scratch/networks/trianaa1/Atlas/Brainnetome/Brainnetome/BNA-maxprob-thr25-2mm.nii.gz'
elif atlas=='shen':
    atlas_img = '/m/cs/scratch/networks/trianaa1/Atlas/Shen/shen_2mm_268_parcellation.nii.gz'
elif atlas=='seitzman-set1':
    atlas_img = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set1.nii'
elif atlas=='seitzman-set2':
    atlas_img = '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set2.nii'

#Prepare the Atlas (mask) that will be used to calculate the averaged ROI time-series
masker = NiftiLabelsMasker(labels_img=atlas_img, standardize=True) #z-scored

#Read/Make the time series
files = []
for root, dirs, file_names in os.walk(path):
    for file in file_names:
        if file.endswith('_HPF_smooth-6mm.nii'):
            files.append(f'{path}{file[0:6]}/{file}')
            
#Compute the ROI-ts
for file in files:
    head, tail = os.path.split(file)
    outfile = f'{savepath}/{tail[:-4]}_{atlas}.csv'
    if os.path.exists(outfile):
        print(f'Node time series file for {file} already exists!')
    else:
        print(f'Creating node time series for {file} in {outfile}')
        time_series = masker.fit_transform(file)
        pd.DataFrame(time_series).to_csv(outfile, index=False, header=False)