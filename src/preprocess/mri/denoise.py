from sys import argv
import pandas as pd
import nibabel as nib
from nilearn.image import clean_img, smooth_img

subject = argv[1]
task = argv[2]
strategy = argv[3]

nii = f'/m/cs/scratch/networks-pm/pm_denoise/{subject}/{subject}_task-{task}_SGdetrend.nii'
confound = f'/m/cs/scratch/networks-pm/pm_denoise/{subject}/{subject}_task-{task}_detrended-confounds.csv'
out = f'/m/cs/scratch/networks-pm/pm_denoise/{subject}/{subject}_task-{task}_SGdetrend_{strategy}_HPF.nii'
smooth = f'/m/cs/scratch/networks-pm/pm_denoise/{subject}/{subject}_task-{task}_SGdetrend_{strategy}_HPF_smooth-6mm.nii'

tr = 0.594
hpf = 0.01

conf = pd.read_csv(confound,header=None)
conf = conf.values
clean = clean_img(nii, detrend=False, standardize=False, high_pass=0.01, confounds=conf, t_r=tr)
nib.save(clean,out)

smoothed = smooth_img(out,6)
nib.save(smoothed,smooth)