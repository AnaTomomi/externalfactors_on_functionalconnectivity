''' Helper functions to compute connectivity matrices 

author: trianaa1
'''

import glob, os, re
import pandas as pd
import numpy as np
import math
from scipy.io import savemat, loadmat
from scipy.spatial.distance import euclidean
from scipy.stats import gaussian_kde
from scipy.stats import zscore
from scipy.interpolate import interp1d

import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn.glm.first_level.design_matrix import make_first_level_design_matrix
from nilearn.glm.first_level import FirstLevelModel

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
    ''' computes the group mask according to the individual masks.
    
    Parameters
    ----------
    conn_path: folder path to where the computations will be stored
    fmriprep_path: folder path to where the output from fmriprep is stored
    task: 'pvt', 'resting', 'nback', or 'movie'
    vol_size: size of the voxels in the nii file. Usually [91,109,91] for 2mm
    atlas_name: name of the atlas to be used
    
    Returns
    -------
    masked_atlas: string with the path to the file containing the group masked atlas
    '''
    files = sorted(glob.glob(fmriprep_path + f'/**/func/*{task}_*mask.nii', recursive=True))
    
    group_mask_mult_name = f'{conn_path}/group_mask_mult.nii'
    group_mask_sum_name = f'{conn_path}/group_mask_sum95.nii'
    if not os.path.exists(group_mask_mult_name) or not os.path.exists(group_mask_sum_name):
        group_mask_mult = np.ones(vol_size)
        group_mask_sum = np.zeros(vol_size)
        for file in files:
            head, tail = os.path.split(file)
            subject = tail[0:6]
            if subject=='sub-25' and task =='nback':
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
    
    masker = NiftiLabelsMasker(labels_img=group_atlas, standardize='zscore_sample')
    
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
    
def get_behav_data_movie(behav_path, variable, lag):
    ''' selects the behavioral data for specific days before the scanner (lag). 
    In this case, only behavioral scores that are related to H4 in the 
    paper are selected. 
    
    Parameters
    ----------
    behav_path: folder path to where the behavioral data files are
    lag: number of days before the scanner to select
    
    Returns
    -------
    filtered_behav: DataFrame with the selected information
    '''
    if variable == 'sleep':    
        behav = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-oura.csv'))
        behav = behav[['date','total_sleep_duration', 'awake_time','restless_sleep',
                  'sleep_efficiency','sleep_latency']] #as defined in the paper
        behav['date'] = pd.to_datetime(behav['date'], format='%d-%m-%Y')
    elif variable=='mood':
        behav = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-smartphone_sensor-ema.csv'))
        behav = behav[['date','pa_mean', 'pa_median', 'pa_min', 'pa_max', 'pa_std', 'na_mean',
                   'na_median', 'na_min', 'na_max', 'na_std', 'stress_mean',
                   'stress_median', 'stress_min', 'stress_max', 'stress_std', 'pain_mean',
                   'pain_median', 'pain_min', 'pain_max', 'pain_std']]
        behav['date'] = pd.to_datetime(behav['date'], format='%Y-%m-%d')
    else:
        behav = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-embraceplus.csv'))
        behav = behav[['date','mean_respiratory_rate_brpm', 'min_respiratory_rate_brpm',
                     'max_respiratory_rate_brpm','median_respiratory_rate_brpm',
                     'std_respiratory_rate_brpm','mean_prv_rmssd_ms', 'min_prv_rmssd_ms', 
                     'max_prv_rmssd_ms','median_prv_rmssd_ms','std_prv_rmssd_ms']]
        behav['date'] = pd.to_datetime(behav['date']).dt.tz_convert(None)  # Remove timezone information
        behav['date'] = behav['date'].dt.date  # Keep only the date part
        behav['date'] = pd.to_datetime(behav['date'], format='%Y-%m-%d')
    
    #fill in the nans with the mean 
    behav.fillna(round(behav.mean(numeric_only=True)), inplace=True)
    cols = [col for col in list(behav.columns) if col != 'date']
    normalized_data = behav[cols]
    
    normalized_data = (normalized_data - normalized_data.mean()) / normalized_data.std() #normalize by z-score
    #normalized_data = (filtered_behav-np.min(filtered_behav))/(np.max(filtered_behav)-np.min(filtered_behav))
    normalized_data.dropna(axis=1, inplace=True) #discard those values with no variation at all
    normalized_data['date'] = behav['date']
    behav = normalized_data

    #select the days
    scan_days = pd.read_csv(os.path.join(f'{behav_path.rsplit("/", 2)[0]}/mri','sub-01_day-all_device-mri.csv'), header=0)
    scan_days = scan_days[['date']]
    scan_days['date'] = pd.to_datetime(scan_days['date'], format='%d/%m/%y')
    if variable =='sleep': 
        lag = lag-1 # to match the oura way of storing the data
    scan_days['date'] = scan_days['date'] - pd.Timedelta(days=lag)

    #select the days
    filtered_behav = behav[behav['date'].isin(scan_days['date'])]
    filtered_behav.drop(columns=['date'], inplace=True)
    
    return filtered_behav

def nearest_neighbors(data):
    ''' computes the simmilarity matrix in a matrix between pairs of observations
    based on the nearest neighbors model (Euclidean distance).
    
    Parameters
    ----------
    data: DataFrame (N_subjects x N_variables)
    lag: number of days before the scanner to select
    
    Returns
    -------
    nn_scaled: simmilarity matrix (n_sub x n_sub)
    '''
    n_sub = len(data)
    nn = np.zeros((n_sub, n_sub))
    for i in range(n_sub):
        for j in range(n_sub):
            if i < j:
                dist_ij = abs(euclidean(data.iloc[i,:].values, data.iloc[j,:].values))
                nn[i,j] = dist_ij
                nn[j,i] = dist_ij
    nn = nn/np.max(nn)
    nn = 1-nn
    return nn

def anna_karenina(data):
    ''' computes the simmilarity matrix in a matrix between pairs of observations
    based on the anna karenina model.
    
    Parameters
    ----------
    data: DataFrame (N_subjects x N_variables)
    lag: number of days before the scanner to select
    
    Returns
    -------
    ak_scaled: simmilarity matrix (n_sub x n_sub)
    '''
    n_sub = len(data)
    ak = np.zeros((n_sub, n_sub))
    for i in range(n_sub):
        for j in range(n_sub):
            if i < j:
                dist_ij = np.linalg.norm((data.iloc[i,:].values + data.iloc[j,:].values)/2) #calculate distance between i and j
                ak[i,j] = dist_ij
                ak[j,i] = dist_ij

    ak = ak/np.max(ak)
    ak = 1-ak
    return ak

def get_behav_data_tasks(behav_path, lag):
    ''' selects the behavioral data for specific days before the scanner (lag). 
    In this case, only behavioral scores that are relaated to H1 and H2 in the 
    paper are selected. 
    
    Parameters
    ----------
    behav_path: folder path to where the behavioral data files are
    lag: number of days before the scanner to select
    
    Returns
    -------
    filtered_behav: DataFrame with the selected information
    '''
    
    behav = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-oura.csv'))
    behav = behav[['date','total_sleep_duration', 'awake_time','restless_sleep',
              'sleep_efficiency','sleep_latency', 'Steps', 'Inactive Time']] #as defined in the paper
    behav['date'] = pd.to_datetime(behav['date'], format='%d-%m-%Y')
    
    #fill in the nans with the mean 
    behav.fillna(round(behav.mean(numeric_only=True)), inplace=True)

    #select the days
    scan_days = pd.read_csv(os.path.join(f'{behav_path.rsplit("/", 2)[0]}/mri','sub-01_day-all_device-mri.csv'), header=0)
    scan_days = scan_days[['date']]
    scan_days['date'] = pd.to_datetime(scan_days['date'], format='%d/%m/%y')
    
    scan_days_activity = (scan_days['date'] - pd.Timedelta(days=lag)).to_frame()
    lag = lag-1 # to match the oura way of storing the data for the sleep
    scan_days_sleep = (scan_days['date'] - pd.Timedelta(days=lag)).to_frame()

    #select the days
    activity_behav = behav[behav['date'].isin(scan_days_activity['date'])]
    activity_behav = activity_behav[['Steps', 'Inactive Time']]
    
    sleep_behav = behav[behav['date'].isin(scan_days_sleep['date'])]
    sleep_behav = sleep_behav[['total_sleep_duration', 'awake_time','restless_sleep',
                               'sleep_efficiency','sleep_latency']]
    
    filtered_behav = pd.concat([sleep_behav.reset_index(drop=True), activity_behav.reset_index(drop=True)], axis=1,ignore_index=True)
    filtered_behav.rename(columns={0: "total_sleep_duration", 1: "awake_time", 2:"restless_sleep",
                                   3: "sleep_efficiency", 4: "sleep_latency", 5:"steps", 6:"inactive_time"}, inplace=True)
    
    return filtered_behav

def get_behav_data(behav_path):
    ''' selects the behavioral data that are relaated to H1, H2, and H3 in the 
    paper are selected. 
    
    Parameters
    ----------
    behav_path: folder path to where the behavioral data files are
    
    Returns
    -------
    behav: DataFrame with the selected information according to the scanner days
    '''
    sleep = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-oura.csv'))
    sleep = sleep[['date','total_sleep_duration', 'awake_time','restless_sleep',
                  'sleep_efficiency','sleep_latency', 'Steps','Inactive Time']] #as defined in the paper
    sleep.rename(columns={'Steps':'steps', 'Inactive Time':'inactive_time'},inplace=True)
    sleep['date'] = pd.to_datetime(sleep['date'], format='%d-%m-%Y')
    sleep.set_index('date', inplace=True)
    
    mood = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-smartphone_sensor-ema.csv'))
    mood = mood[['date','pa_mean', 'pa_median', 'pa_min', 'pa_max', 'pa_std', 'na_mean',
                   'na_median', 'na_min', 'na_max', 'na_std', 'stress_mean',
                   'stress_median', 'stress_min', 'stress_max', 'stress_std', 'pain_mean',
                   'pain_median', 'pain_min', 'pain_max', 'pain_std']]
    mood['date'] = pd.to_datetime(mood['date'], format='%Y-%m-%d')
    mood.set_index('date', inplace=True)
    
    phys = pd.read_csv(os.path.join(behav_path, 'sub-01_day-all_device-embraceplus.csv'))
    phys = phys[['date','mean_respiratory_rate_brpm', 'min_respiratory_rate_brpm',
                     'max_respiratory_rate_brpm','median_respiratory_rate_brpm',
                     'std_respiratory_rate_brpm','mean_prv_rmssd_ms', 'min_prv_rmssd_ms', 
                     'max_prv_rmssd_ms','median_prv_rmssd_ms','std_prv_rmssd_ms']]
    phys['date'] = pd.to_datetime(phys['date']).dt.tz_convert(None)  # Remove timezone information
    phys['date'] = phys['date'].dt.date  # Keep only the date part
    phys['date'] = pd.to_datetime(phys['date'], format='%Y-%m-%d')
    phys.set_index('date', inplace=True)
    
    behav = pd.concat([sleep, mood, phys], axis=1)
    
    #fill in the nans with the mean 
    behav.fillna(round(behav.mean(numeric_only=True)), inplace=True)
    
    return behav

def get_behav_data_15days(behav_path, days=16, behav=None):
    ''' selects the behavioral data for specific days before the scanner (lag). 
    In this case, behavioral scores that are related to H1, H2, and H3 in the 
    paper are selected. 
    
    Parameters
    ----------
    behav_path: folder path to where the behavioral data files are
    behav: behavioral data in dataframe
    lag: number of days before the scanner to select
    
    Returns
    -------
    filtered_behav: DataFrame with the selected information according to the scanner days
    '''
    if behav is None:
        behav = get_behav_data(behav_path)
        behav = zscore(behav)
    else:
        behav = behav.copy()

    #select the days
    scan_days = pd.read_csv(os.path.join(f'{behav_path.rsplit("/", 2)[0]}/mri','sub-01_day-all_device-mri.csv'), header=0)
    scan_days = scan_days[['date']]
    scan_days['date'] = pd.to_datetime(scan_days['date'], format='%d/%m/%y')
    
    # Create lag variables
    columns = list(behav.columns)
    
    # Adjusting the sleep columns first
    sleep_cols = ['total_sleep_duration','awake_time','restless_sleep','sleep_efficiency', 'sleep_latency']
    behav[sleep_cols] = behav[sleep_cols].shift(-1).fillna(behav[sleep_cols].mean())

    new_columns = {}
    for lag in range(days):  
        for col in columns:
            new_columns[f"{col}{lag}"] = behav[col].shift(lag)

    # Adding the new columns to the DataFrame at once
    behav = pd.concat([behav, pd.DataFrame(new_columns)], axis=1)

    # Merge dataframes
    merged_df = pd.merge(scan_days, behav, left_on="date", right_on="date", how="left")

    # Keep only relevant columns
    final_cols = ['date'] + [f"{col}{i}" for i in range(days) for col in columns]
    filtered_behav = merged_df[final_cols]
    
    return filtered_behav

def make_designmat(file, path, task, strategy):
    nii = nib.load(file)
    subject = file.split('/')[-3]
    
    # Make the regression matrix (convolved with the HRF)
    print("Creating the design matrix")
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
    n_vols = nii.header["dim"][4]
    frame_times = np.arange(n_vols) * tr
    
    if task == 'pvt':
        events = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_events.tsv', sep='\t')
        events.rename(columns={"response_time":"modulation"},inplace=True)
        events = events[['onset','trial_type','duration','modulation']]
        events.fillna(0.01, inplace=True)
    else:
        events = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_blocks.tsv', sep='\t')
        events = events[['onset','trial_type','duration']]
        
    confounds = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_desc-confounds_timeseries.tsv', sep='\t')
    hr_rr = loadmat(f'{path}/{subject}/func/{subject}_task-{task}_device-biopac_downsampledcut.mat')
    hr_rr = hr_rr['downsampled_cut'].T
    confounds[['heart_rate', 'respiration_rate']] = hr_rr
        
    hmp = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z','trans_x_derivative1','trans_y_derivative1',
               'trans_z_derivative1','trans_x_power2','trans_y_power2','trans_z_power2','trans_x_derivative1_power2',
               'trans_y_derivative1_power2','trans_z_derivative1_power2','rot_x_derivative1','rot_y_derivative1',
               'rot_z_derivative1','rot_x_power2','rot_y_power2','rot_z_power2','rot_x_derivative1_power2',
               'rot_y_derivative1_power2','rot_z_derivative1_power2']
    phys = ['csf','csf_derivative1','csf_power2','csf_derivative1_power2','white_matter','white_matter_derivative1',
                'white_matter_power2','white_matter_derivative1_power2','heart_rate', 'respiration_rate']
    gs = ['global_signal','global_signal_derivative1','global_signal_derivative1_power2','global_signal_power2']
    motion = [s for s in list(confounds.columns) if "motion_outlier" in s]
        
    if strategy=='24HMP-8Phys-Spike_HPF':
        confound_names = hmp+phys+motion
    elif strategy=='24HMP-8Phys-4GSR-Spike_HPF':
        confound_names = hmp+phys+gs+motion
    else:
        raise ValueError('Strategy not found!')
        
    confounds = confounds[confound_names]
    confounds.fillna(0, inplace=True)
    design_matrix = make_first_level_design_matrix(frame_times, events, hrf_model=hrf_model, 
                                                   drift_model='cosine', high_pass=0.01, 
                                                   add_regs=confounds, add_reg_names=confound_names)        
    return design_matrix

def make_first_level(file, path, task, design_matrix):
    nii = nib.load(file)
    subject = file.split('/')[-3]
    
    if subject == 'sub-25' and task=='nback':
        #there is a cut in the nback mask for subject 25, so we will use the resting-state mask
        mask = f'{path}/{subject}/func/{subject}_task-resting_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    else:
        mask = f'{path}/{subject}/func/{subject}_task-{task}_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii'
    
    hrf_model = 'glover'
    tr = nii.header["pixdim"][4]
    
    # First-level model
    flm = FirstLevelModel(t_r=tr, slice_time_ref=0, hrf_model=hrf_model, 
                          drift_model='cosine', high_pass=0.1, smoothing_fwhm=6,
                          mask_img=mask, noise_model='ar1', standardize=False, n_jobs=-1, 
                          minimize_memory=False, verbose=True,subject_label=subject)
    print(f'fit the model for {subject}')
    flm.fit(run_imgs=nii, design_matrices=design_matrix)
    
    if task == 'pvt':
        if 'lapse' in design_matrix.columns:
            ok_lapse = flm.compute_contrast('OK+lapse', stat_type='t', output_type='z_score')
        else:
            ok_lapse = flm.compute_contrast('OK', stat_type='t', output_type='z_score')
        return ok_lapse
    else:
        one_twoback = flm.compute_contrast('twoback-oneback', stat_type='t', output_type='z_score')
        return one_twoback

def lss_transformer(df, row_number):
    """Label one trial for one LSS model. As taken from nilearn
    https://nilearn.github.io/dev/auto_examples/07_advanced/plot_beta_series.html#sphx-glr-auto-examples-07-advanced-plot-beta-series-py

    Parameters
    ----------
    df : pandas.DataFrame
        BIDS-compliant events file information.
    row_number : int
        Row number in the DataFrame.
        This indexes the trial that will be isolated.

    Returns
    -------
    df : pandas.DataFrame
        Update events information, with the select trial's trial type isolated.
    trial_name : str
        Name of the isolated trial's trial type.
    """
    df = df.copy()

    # Determine which number trial it is *within the condition*
    trial_condition = df.loc[row_number, "trial_type"]
    trial_type_series = df["trial_type"]
    trial_type_series = trial_type_series.loc[
        trial_type_series == trial_condition
    ]
    trial_type_list = trial_type_series.index.tolist()
    trial_number = trial_type_list.index(row_number)

    # We use a unique delimiter here (``__``) that shouldn't be in the
    # original condition names.
    # Technically, all you need is for the requested trial to have a unique
    # 'trial_type' *within* the dataframe, rather than across models.
    # However, we may want to have meaningful 'trial_type's (e.g., 'Left_001')
    # across models, so that you could track individual trials across models.
    trial_name = f"{trial_condition}__{trial_number:03d}"
    df.loc[row_number, "trial_type"] = trial_name
    return df, trial_name

def get_confounds(file, task, strategy):  
    ''' fetch the confounds file generated by fmriprep based on the name of the file
    

    Parameters
    ----------
    file : str, name of the nii file
    task: str, name of the task to process
    strategy: str, denoise strategy to be applied

    Returns
    -------
    confounds: DataFrame, with the selected confounds'''
    
    subject = file.split('/')[-3]
    match = re.search(r'(/m/cs/scratch/networks-pm/pm_preprocessed/sub-\w+/func/)', file)
    path = match.group(1)
    
    confounds = pd.read_csv(f'{path}/{subject}_task-{task}_desc-confounds_timeseries.tsv', sep='\t')
    hr_rr = loadmat(f'{path}/{subject}_task-{task}_device-biopac_downsampledcut.mat')
    hr_rr = hr_rr['downsampled_cut'].T
    confounds[['heart_rate', 'respiration_rate']] = hr_rr
        
    hmp = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z','trans_x_derivative1','trans_y_derivative1',
               'trans_z_derivative1','trans_x_power2','trans_y_power2','trans_z_power2','trans_x_derivative1_power2',
               'trans_y_derivative1_power2','trans_z_derivative1_power2','rot_x_derivative1','rot_y_derivative1',
               'rot_z_derivative1','rot_x_power2','rot_y_power2','rot_z_power2','rot_x_derivative1_power2',
               'rot_y_derivative1_power2','rot_z_derivative1_power2']
    phys = ['csf','csf_derivative1','csf_power2','csf_derivative1_power2','white_matter','white_matter_derivative1',
                'white_matter_power2','white_matter_derivative1_power2','heart_rate', 'respiration_rate']
    gs = ['global_signal','global_signal_derivative1','global_signal_derivative1_power2','global_signal_power2']
    motion = [s for s in list(confounds.columns) if "motion_outlier" in s]
        
    if strategy=='24HMP-8Phys-Spike_HPF':
        confound_names = hmp+phys+motion
    elif strategy=='24HMP-8Phys-4GSR-Spike_HPF':
        confound_names = hmp+phys+gs+motion
    else:
        raise ValueError('Strategy not found!')
        
    confounds = confounds[confound_names]
    confounds.fillna(0, inplace=True)
    return confounds

def compute_averagedbetas(conn_path, contrast, task, strategy, group_atlas):
    ''' computes the averaged-ROI timeseries based on a selected atlas. The 
    computations are done for all subjects in a folder.
    
    Parameters
    ----------
    conn_path: folder path to where the beta series are and where the ROIs will be stored
    contrast: 
    strategy: denoised strategy
    group_atlas: file path to the group mask multiplied by the selected atlas.
                 It should be a nii file
    
    Returns
    -------
    roi_ts_file: string with the path to the file containing the averaged-ROI 
                 time series for all subjects
    '''
    
    files = sorted(glob.glob(conn_path + f'/**/*{task}_*{strategy}*-{contrast}.nii', recursive=True))
    atlas_name = os.path.basename(group_atlas).split('_')[-1].split('.nii')[0]
    if task=='nback':
        roi_ts_file = f'{conn_path}/{strategy}/averaged_roits_{contrast}_{strategy}_{atlas_name}.mat'
    elif task=='pvt':
        roi_ts_file = f'{conn_path}/{strategy}/averaged_roits_{strategy}_{atlas_name}.mat'
    
    masker = NiftiLabelsMasker(labels_img=group_atlas, standardize='zscore_sample')
    
    if not os.path.exists(roi_ts_file):
        all_ts = []
        for file in files:
            head, tail = os.path.split(file)
            print(f'Creating node time series for {file}')
            time_series = masker.fit_transform(file)
            all_ts.append(time_series)
        rs_ts = list2mat(all_ts)
        savemat(roi_ts_file, {'rs_ts':rs_ts})
    return roi_ts_file

def get_pval(tvals, data):
    ''' computes the p-value for non-parametric permutations
    
    Parameters
    ----------
    tvals: numpy.array of correlation values. The size should be (i,j), where i
    is the variable and j the lag
    data: numpy.array of permutation correlation values. This data is generated 
    based on surrogate data. The size should be (i,j,n_perm), where i is the variable 
    and j the lag.
    
    Returns
    -------
    pvals: p-val for each (i,j) where i is the variable and j the lag.
    '''
    NCDF = 200
    pvals = np.zeros(tvals.shape)
    
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            outiter = data[i, j, :] #variable i, lag j
            tval = tvals[i, j]
            
            # Kernel Density Estimation and CDF computation
            kde = gaussian_kde(outiter, bw_method='silverman')
            xi = np.linspace(-1, 1, NCDF)
            fi = np.array([kde.integrate_box_1d(-np.inf, x) for x in xi])
            
            # Interpolation
            interp_fi = interp1d(xi, fi, bounds_error=False, fill_value=(0, 1))
            pval_left = interp_fi(tval)
            
            # Two-tailed p-value computation
            pval_right = 1 - pval_left
            pval = min(pval_right, pval_left)
            
            # Storing the p-value
            pvals[i, j] = pval
    return pvals

def compute_real_corr(behav_path, variables, pc, lag_no):
    ''' computes the real correlations (not fake) between global efficiency or 
    participation coefficient and the behavioral values.
    
    Parameters
    ----------
    behav_path: str, path where the behavioral data is stored
    variables: list, with the name of the variables/external factors that were computed
    pc: array, global efficiency or participation coefficients (size sessions X networks)
    lag_no: int, number of lags to inspect
    
    Returns
    -------
    real_corr_values: list of dataframes, each dataframe contains the correlation
                      values for a network. The dataframe is of size variables X
                      lags. 
    '''
    
    #Load behavioral data
    behav = get_behav_data_15days(f'{behav_path}/behavioral/',days=16)
    selected_cols = [col for col in behav.columns if any(var in col for var in variables)]
    behav = behav[selected_cols]
    num_var = len(variables)
    columns = list(behav.columns)
    node_num = pc.shape[1]
    
    real_corr_values = np.zeros((num_var,lag_no,node_num))  # move outside of loop
    for lag in range(lag_no):
        sub_behav = behav[[col for col in columns if col.endswith(f"{lag}") and not col.endswith(f"1{lag}")]]
        for node in range(node_num):
            corrs = sub_behav.corrwith(pd.Series(pc[:,node],name=str(node)), method='spearman')
            real_corr_values[:,lag,node] = corrs.values

    real_corr_values = [real_corr_values[:, :, i] for i in range(real_corr_values.shape[2])]
    for i in range(len(real_corr_values)):
        real_corr_values[i] = pd.DataFrame(real_corr_values[i], index=variables, columns=[f'lag {j}' for j in range(real_corr_values[i].shape[1])])
        real_corr_values[i].drop(columns=['lag 0'], inplace=True)
    
    return real_corr_values