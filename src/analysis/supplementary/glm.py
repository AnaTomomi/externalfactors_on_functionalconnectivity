import os
import numpy as np
import pandas as pd
from glob import glob
import nibabel as nib

from nilearn.glm.first_level.design_matrix import make_first_level_design_matrix
from nilearn.glm.first_level import FirstLevelModel

path = '/m/cs/scratch/networks-pm/pm_denoise'
events_path = '/m/cs/scratch/networks-pm/pm_preprocessed'
task = 'pvt'
strategy = '24HMP-8Phys-Spike_HPF'


file_pattern = f'*task-{task}_SGdetrend_{strategy}_smooth-6mm.nii'
files = []

for root, _, files_in_dir in os.walk(path):
    matched_files = glob(os.path.join(root, file_pattern))
    files.extend(matched_files)
files = sorted(files, key=lambda x: int(x.split("sub-")[1].split("/")[0]))

flms=[]
for file in files:
    print(file)
    design_matrix = make_designmat(file, events_path, task)
    flm = make_first_level(file, events_path, task, design_matrix)
    flms.append(flm)

def make_designmat(file, events_path, task):
    nii = nib.load(file)
    subject = file.split('/')[-2]
    
    # Make the regression matrix (convolved with the HRF)
    print("Creating the design matrix")
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
    n_vols = nii.header["dim"][4]
    frame_times = np.arange(n_vols) * tr
    
    if task == 'pvt':
        events = pd.read_csv(f'{events_path}/{subject}/func/{subject}_task-{task}_events.tsv', sep='\t')
        events.rename(columns={"response_time":"modulation"},inplace=True)
        events = events[['onset','trial_type','duration','modulation']]
        events.fillna(0.01, inplace=True)
        design_matrix = make_first_level_design_matrix(frame_times, events, hrf_model=hrf_model, drift_model=None)
    else:
        events = pd.read_csv(f'{events_path}/{subject}/func/{subject}_task-{task}_blocks.tsv', sep='\t')
        events = events[['onset','trial_type','duration']]
        design_matrix = make_first_level_design_matrix(frame_times, events, hrf_model=hrf_model, drift_model=None)
        
    design_matrix = design_matrix.reset_index()
    dm = {'dm': design_matrix.values}    
    return dm

def make_first_level(file, events_path, task, design_matrix):
    nii = nib.load(file)
    subject = file.split('/')[-2]
    
    if subject == 'sub-25' and task=='nback':
        #there is a cut in the nback mask for subject 25, so we will use the resting-state mask
        mask = f'{events_path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    else:
        mask = f'{events_path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
    
    # First-level model
    flm = FirstLevelModel(t_r=tr, slice_time_ref=0, hrf_model=hrf_model, drift_model=None,
                          mask_img=mask, noise_model='ar1', standardize=False, n_jobs=1, 
                          minimize_memory=False, verbose=True)
    print(f'fit the model for {subject}')
    flm.fit(run_imgs=nii, design_matrices=design_matrix)
    
    if task == 'pvt':
        ok = flm.compute_contrast('OK', stat_type='t', output_type='z_score')
        lapse = flm.compute_contrast('lapse', stat_type='t', output_type='z_score')
        nib.save(ok, f'{savepath}/{subject}_task-{task}_SGdetrend_{strategy}_smooth-6mm_flm_log_ok.nii.gz')
        nib.save(lapse, f'{savepath}/{subject}_task-{task}_SGdetrend_{strategy}_smooth-6mm_flm_log_lapse.nii.gz')
    else:
        oneback = flm.compute_contrast('oneback', stat_type='t', output_type='z_score')
        twoback = flm.compute_contrast('twoback', stat_type='t', output_type='z_score')
        one-twoback = flm.compute_contrast('twoback'-'oneback', stat_type='t', output_type='z_score')
    return flm