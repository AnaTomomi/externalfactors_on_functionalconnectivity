'''Preprocess events from the presentation logs to the BIDS events file for the 
nback task. 

    Parameters
    ----------
    path : str
        path where the raw data is stored 
    savepath : str
        BIDS folder
        

'''

import os, sys
import re
import pandas as pd

from glob import glob

path = '/m/cs/project/networks-pm/cognitive'#sys.argv[1]
savepath = '/m/cs/project/networks-pm/mri/fast_prepro_bids'#sys.argv[2]

tr = 0.594
nii_length = 614

os.chdir(path)
days = pd.read_csv(f'{savepath}/participants.tsv',sep='\t')

# Organize the files to read
files = []
pattern   = f'*nback_run-0_pres.log'
for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'preprocessing {str(len(files))} files..................')
files.sort()

filtered_files = []
for file in files:
    day = int(file.split('_day-')[1].split('_')[0])
    if day in days['day'].values:
        filtered_files.append(file)

for file in filtered_files:
    print(f'processing {file}')
    day = re.search('day-(\d+)', file).group(1)
    subject = days[days['day'] == int(day)]['participant_id'].iloc[0]
    df = pd.DataFrame(columns=['onset','duration','trial_type','response_time'])
    
    pulse_info = pd.read_csv(file, sep='\t', skiprows=[0,1,2])
    pulse_info['Time'] = pd.to_numeric(pulse_info['Time'], errors='coerce')
    pulse_info['Time'] = pulse_info['Time']/10
    mri_pulse_time = pulse_info[pulse_info['Code'] == 'MRI pulse received']['Time'].iloc[0]
    pulse_info['Time'] = (pulse_info['Time']-mri_pulse_time)-(5*(tr*1000))

    #add the first line
    #check when does the nback start
    for i in range(len(pulse_info) - 1):
        if pulse_info['Trial'].iloc[i] == '4' and pulse_info['Trial'].iloc[i + 1] != '4':
            nback_start = pulse_info.iloc[i]
    
    #add the first event which is the washout out cross
    first_row = pd.DataFrame([{'onset': 0, 'duration': nback_start["Time"]/1000, 'trial_type': 'intro'}])
    
    info = pulse_info[pulse_info['Code'].isin(['dual_block', 'feedback'])]

    df = pd.DataFrame(columns=['onset','duration','trial_type'])
    df['onset'] = info['Time']
    df['duration'] = info['Time'].shift(-1) - info['Time']
    df['duration'].iloc[-1] = ((nii_length*tr)*1000)-info['Time'].iloc[-1]
    df['trial_type'] = info['Code']
    
    #sanity check: has the start of nback been cut?
    assert df.loc[df['trial_type'] == 'dual_block', 'onset'].iloc[0]>0, "the start has been cut"
    
    df['trial_type'] = df['trial_type'].replace(['3', 'feedback'], 'rest')
    
    #identify the one and two-back tasks
    tasks = ['oneback', 'twoback']
    task_idx = 0

    for idx, row in df[df['trial_type'] == 'dual_block'].iterrows():
        df.at[idx, 'trial_type'] = tasks[task_idx]
        task_idx = 1 - task_idx  # switch between 0 and 1
    
    df[['onset','duration']] = df[['onset','duration']]/1000
    
    #merge with the first row
    df = pd.concat([first_row, df])
    
    df.to_csv(f'/m/cs/scratch/networks-pm/pm_denoise/{subject}/{subject}_task-nback_blocks.tsv', sep='\t', index=False)
