''' This file generates the beta series for the connectivity analysis
    of the task-fMRI data'''

import os, sys
import numpy as np
import pandas as pd
from glob import glob
import nibabel as nib

from nilearn.image import concat_imgs
from nilearn.glm.first_level import FirstLevelModel

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import make_first_level, make_designmat, lss_transformer

path = '/m/cs/scratch/networks-pm/pm_preprocessed'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/supplementary'
task = 'nback'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'


file_pattern = f'*task-{task}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii'
files = []

for root, _, files_in_dir in os.walk(path):
    matched_files = glob(os.path.join(root, file_pattern))
    files.extend(matched_files) 
files = sorted(files, key=lambda x: int(x.split("sub-")[1].split("/")[0]))


for file in files:
    subject = file.split('/')[-3]
    print(f'computing b-series for {subject}')
    nii = nib.load(file)
    if subject == 'sub-25' and task=='nback':
        #there is a cut in the nback mask for subject 25, so we will use the resting-state mask
        mask = f'{path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    else:
        mask = f'{path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    
    #Define some parameters
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
        
    events = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_events.tsv', sep='\t')
    if task == 'pvt':
        events.rename(columns={"response_time":"modulation"},inplace=True)
        events = events[['onset','trial_type','duration','modulation']]
        events.fillna(0.01, inplace=True)
    else:
        events = events[['onset','trial_type','duration']]



# Loop through the trials of interest and transform the DataFrame for LSS
lss_beta_maps = {cond: [] for cond in events["trial_type"].unique()}
lss_design_matrices = []

for i_trial in range(events.shape[0]):
    lss_events, trial_condition = lss_transformer(events, i_trial)

    # Compute and collect beta maps
    lss_glm = FirstLevelModel(t_r=tr, slice_time_ref=0, hrf_model=hrf_model, 
                          drift_model='cosine', high_pass=0.1, smoothing_fwhm=6,
                          mask_img=mask, noise_model='ar1', standardize=False, n_jobs=-1, 
                          minimize_memory=False, verbose=True,subject_label=subject)
    lss_glm.fit(file, lss_events)

    # We will save the design matrices across trials to show them later
    lss_design_matrices.append(lss_glm.design_matrices_[0])

    beta_map = lss_glm.compute_contrast(trial_condition,output_type="effect_size",)

    # Drop the trial number from the condition name to get the original name
    condition_name = trial_condition.split("__")[0]
    lss_beta_maps[condition_name].append(beta_map)

# We can concatenate the lists of 3D maps into a single 4D beta series for
# each condition, if we want
lss_beta_maps = {
    name: concat_imgs(maps) for name, maps in lss_beta_maps.items()
}