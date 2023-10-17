''' This file generates the first-level GLM analysis for the supplementary 
    analysis for pvt and nback tasks '''

import os, sys
import numpy as np
import pandas as pd
from glob import glob
import nibabel as nib

from nilearn.glm.first_level.design_matrix import make_first_level_design_matrix
from nilearn.image import concat_imgs

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import make_first_level, get_confounds

path = '/m/cs/scratch/networks-pm/pm_preprocessed'
thres_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/cognitive'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/supplementary'
task = 'nback'
strategy = '24HMP-8Phys-Spike_HPF'


file_pattern = f'*task-{task}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii'
files = []

for root, _, files_in_dir in os.walk(path):
    matched_files = glob(os.path.join(root, file_pattern))
    files.extend(matched_files) 
files = sorted(files, key=lambda x: int(x.split("sub-")[1].split("/")[0]))

flms=[]
for i, file in enumerate(files):
    print(file)
    nii = nib.load(file)
    subject = file.split('/')[-3]
    
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
    n_vols = nii.header["dim"][4]
    frame_times = np.arange(n_vols) * tr
    
    confounds = get_confounds(file, task, strategy)
    confound_names = list(confounds.columns)
    events = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_blocks.tsv', sep='\t')
    events = events[['onset','trial_type','duration']]
    adaptative_thres = pd.read_excel(f'{thres_path}/sub-01_day-scandays_device-presentation_thresholds.xlsx')
    adaptative_thres = adaptative_thres[adaptative_thres['session']==i+1]
    adaptative_thres.reset_index(inplace=True)
    
    events['aud_thres'] = None
    events['vis_thres'] = None
    oneback_counter = 0
    twoback_counter = 0
    for idx, row in events.iterrows():
        if row['trial_type'] == 'oneback':
            # Assigning the respective aud and vis thresholds for oneback
            events.at[idx, 'aud_thres'] = adaptative_thres.loc[oneback_counter, 'one_aud']
            events.at[idx, 'vis_thres'] = adaptative_thres.loc[oneback_counter, 'one_vis']
            # Increasing the oneback counter
            oneback_counter += 1
            
        elif row['trial_type'] == 'twoback':
            # Assigning the respective aud and vis thresholds for twoback
            events.at[idx, 'aud_thres'] = adaptative_thres.loc[twoback_counter, 'two_aud']
            events.at[idx, 'vis_thres'] = adaptative_thres.loc[twoback_counter, 'two_vis']
            # Increasing the twoback counter
            twoback_counter += 1
    events['aud_thres'] = pd.to_numeric(events['aud_thres'], errors='ignore')
    events['vis_thres'] = pd.to_numeric(events['vis_thres'], errors='ignore')
    
    design_matrix = make_first_level_design_matrix(frame_times, events, hrf_model=hrf_model, 
                                                   drift_model='cosine', high_pass=0.01, 
                                                   add_regs=confounds, add_reg_names=confound_names)
    
    flm = make_first_level(file, path, task, design_matrix)
    flms.append(flm)

firstLevel = concat_imgs(flms, ensure_ndim=4)
nib.save(firstLevel,f'{savepath}/{task}_glm-first_{strategy}.nii')
