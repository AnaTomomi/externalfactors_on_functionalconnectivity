''' This file generates the first-level GLM analysis for the supplementary 
    analysis for pvt and nback tasks '''

import os, sys
import numpy as np
import pandas as pd
from glob import glob
import nibabel as nib

from nilearn.image import concat_imgs

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import make_first_level, make_designmat

path = '/m/cs/scratch/networks-pm/pm_preprocessed'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/supplementary'
task = 'pvt'
strategy = '24HMP-8Phys-Spike_HPF'


file_pattern = f'*task-{task}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii'
files = []

for root, _, files_in_dir in os.walk(path):
    matched_files = glob(os.path.join(root, file_pattern))
    files.extend(matched_files) 
files = sorted(files, key=lambda x: int(x.split("sub-")[1].split("/")[0]))

flms=[]
for file in files:
    print(file)
    design_matrix = make_designmat(file, path, task, strategy)
    flm = make_first_level(file, path, task, design_matrix)
    flms.append(flm)

firstLevel = concat_imgs(flms, ensure_ndim=4)
nib.save(firstLevel,f'{savepath}/{task}_glm-first_{strategy}.nii')
