'''Preprocess events from the presentation logs to the BIDS events file for the 
PVT task. 

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
    pulse_info.dropna(subset=['Code', 'Time', 'TTime'], inplace=True) #drop repeated information
    pulse_info = pulse_info.drop(pulse_info.iloc[-1].name)
    
    pulse_info['Time'] = pd.to_numeric(pulse_info['Time'], errors='coerce')
    pulse_info['Time'] = pulse_info['Time']/10
    mri_pulse_time = pulse_info[pulse_info['Code'] == 'MRI pulse received']['Time'].iloc[0]
    pulse_info['Time'] = (pulse_info['Time']-mri_pulse_time)-(5*(tr*1000))
    
    #check when does the nback start and end
    for i in range(len(pulse_info) - 1):
        if pulse_info['Trial'].iloc[i] == '4' and pulse_info['Trial'].iloc[i + 1] != '4':
            nback_start = pulse_info.iloc[i]
    nback_end = pulse_info.iloc[-1]
    last_row = pd.DataFrame([{'onset': nback_end['Time']/1000, 'duration': nback_start["Duration"], 'trial_type': 'end'}])
    
    #add the first event which is the washout out cross
    first_row = pd.DataFrame([{'onset': 0, 'duration': nback_start["Time"]/1000, 'trial_type': 'intro'}])
        
    #add the other rows
    pulse_info = pulse_info.loc[(pulse_info['Code'] == 'response') | 
                                (pulse_info['Code'].str.contains('dual_vis_')) | 
                                (pulse_info['Code'].str.contains('dual_aud')) | 
                                (pulse_info['Code'] == 'dual_block') | 
                                (pulse_info['Code'] == 'feedback')]
    pulse_info['Duration'] = pulse_info['Duration'].astype(float)
    
    other_rows = pd.DataFrame({'onset': pulse_info['Time'] / 1000, 'duration': pulse_info['Duration'] / 1000,
                               'trial_type': pulse_info['Code']})
    # 1. Change 'trial_type'
    blocks = other_rows[other_rows['trial_type'] == 'dual_block'].index.tolist()
    feedbacks = other_rows[other_rows['trial_type'] == 'feedback'].index.tolist()

    # Ensure there's the same number of blocks and feedbacks
    assert len(blocks) == len(feedbacks), "Number of blocks does not match number of feedbacks"

    stimulus_types = ['stimulus1', 'stimulus2'] * (len(blocks) // 2)

    for block, feedback, stimulus in zip(blocks, feedbacks, stimulus_types):
        mask = (other_rows.index > block) & (other_rows.index < feedback) & (other_rows['trial_type'].str.startswith('dual_'))
        other_rows.loc[mask, 'trial_type'] = stimulus
    
    # 2. Merge the duration
    one_summ = pd.read_csv(f'{path}/{subject}_day-{day}_task-nback_run-1_pres.txt', sep='\t', 
                           skiprows=[0,1,2,3,4,5,6], index_col=False)
    two_summ = pd.read_csv(f'{path}/{subject}_day-{day}_task-nback_run-2_pres.txt', sep='\t', 
                           skiprows=[0,1,2,3,4,5,6], index_col=False)
    one_summ.dropna(inplace=True)
    two_summ.dropna(inplace=True)
    one_summ = one_summ[one_summ['Block '].apply(lambda x: pd.to_numeric(x, errors='coerce')).notnull()]
    two_summ = two_summ[two_summ['Block '].apply(lambda x: pd.to_numeric(x, errors='coerce')).notnull()]
    
    response_indices = other_rows[other_rows['trial_type'] == 'response'].index.tolist()
    reaction_times_one = one_summ[' reaction_time '].tolist()
    reaction_times_two = two_summ[' reaction_time '].tolist()

    # Ensure both lists are divisible by 20
    assert len(reaction_times_one) % 20 == 0
    assert len(reaction_times_two) % 20 == 0

    # Merge reaction times in the desired order
    merged_reaction_times = []
    for i in range(0, len(reaction_times_one), 20):
        merged_reaction_times.extend(reaction_times_one[i:i+20])
        merged_reaction_times.extend(reaction_times_two[i:i+20])
    merged_reaction_times = [(int(i)/1000) for i in merged_reaction_times]

    # Replace duration values for response rows in other_rows dataframe
    for idx, rt in zip(response_indices, merged_reaction_times):
        other_rows.at[idx, 'duration'] = rt

    df = pd.concat([first_row, other_rows, last_row], ignore_index=True)
    df['duration'] = df['duration'].apply(lambda x: 0 if x < 0 else x)
    
    for idx, row in df.iterrows():
        if pd.isna(row['duration']):
            try:
                df.at[idx, 'duration'] = df.at[idx+1, 'onset'] - row['onset']
            except KeyError:  # In case idx+1 doesn't exist
                pass
    df.to_csv(f'{savepath}/{subject}/func/{subject}_task-nback_events.tsv', sep='\t', index=False)
