import sys
import pandas as pd
import nibabel as nib

from nilearn.image import concat_imgs
from nilearn.glm.first_level import FirstLevelModel

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import  lss_transformer, get_confounds

path = '/m/cs/scratch/networks-pm/pm_preprocessed'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
task = sys.argv[2]#'nback'
strategy = sys.argv[3]#'24HMP-8Phys-Spike_HPF'
subject = sys.argv[1]#'sub-01'


#Defint the file and mask
file = f'{path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii'
nii = nib.load(file)
if subject == 'sub-25' and task=='nback':
    #there is a cut in the nback mask for subject 25, so we will use the resting-state mask
    mask = f'{path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
else:
    mask = f'{path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
print(f'files loaded: {file}')
print(strategy)

#Define some GLM parameters
hrf_model = 'glover'
tr = nii.header["pixdim"][4]

#Load the events file
events = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_events.tsv', sep='\t')
if task == 'pvt':
    events.rename(columns={"response_time":"modulation"},inplace=True)
    events = events[['onset','trial_type','duration','modulation']]
    #The contrast for the PVT is "OK" + "lapse" as we have RT for both events. 
    #Therefore, to compute the beta series, we need all events in ORDER so that the
    #when we compute the correlations, the time series of evetns are in order. 
    #Otherwise, we would have correlations of 1 or 2 betas for lapses. 
    #Consequently, the lapse trial_type changes for "OK"
    events.loc[events['trial_type'] == 'lapse', 'trial_type'] = 'OK'
    events.fillna(0.01, inplace=True)
else:
    events = events[['onset','trial_type','duration']]
print('events loaded')

#Load the confounds
confounds = get_confounds(file, task, strategy)
print('confounds loaded')

# Loop through the trials of interest and transform the DataFrame for LSS
lss_beta_maps = {cond: [] for cond in events["trial_type"].unique()}

for i_trial in range(events.shape[0]):
    type_event = events.loc[i_trial].at['trial_type']
    if (type_event=='oneback' or type_event=='twoback' or type_event=='OK'):  
        lss_events, trial_condition = lss_transformer(events, i_trial)

        # Compute and collect beta maps
        lss_glm = FirstLevelModel(t_r=tr, slice_time_ref=0, hrf_model=hrf_model, 
                          drift_model='cosine', high_pass=0.1, smoothing_fwhm=6,
                          mask_img=mask, noise_model='ar1', standardize=False, n_jobs=-1, 
                          minimize_memory=False, verbose=True,subject_label=subject)
        lss_glm.fit(file, lss_events, confounds)

        beta_map = lss_glm.compute_contrast(trial_condition,output_type="effect_size",)

        # Drop the trial number from the condition name to get the original name
        condition_name = trial_condition.split("__")[0]
        lss_beta_maps[condition_name].append(beta_map)
        print(f'beta map for {type_event}__{i_trial} computed')

# We can concatenate the lists of 3D maps into a single 4D beta series for each condition, if we want
lss_beta_maps = {name: maps for name, maps in lss_beta_maps.items() if maps}
lss_beta_maps = {name: concat_imgs(maps) for name, maps in lss_beta_maps.items()}
print('beta maps concatenated')

for key in lss_beta_maps.keys():
    nib.save(lss_beta_maps[key], f'{savepath}/{task}/{strategy}/{subject}_task-{task}_{strategy}_betaseries-{key}.nii')
        