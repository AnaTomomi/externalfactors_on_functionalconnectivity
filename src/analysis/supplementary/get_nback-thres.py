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
import numpy as np

from glob import glob

path = '/m/cs/project/networks-pm/cognitive'#sys.argv[1]
mri_path = '/m/cs/project/networks-pm/mri/fast_prepro_bids'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/cognitive'#sys.argv[2]

days = pd.read_csv(f'{mri_path}/participants.tsv',sep='\t')

def get_thresholds (pattern):
    files = []
    for dir,_,_ in os.walk(path):
        files.extend(glob(os.path.join(dir,pattern))) 
    print(f'preprocessing {str(len(files))} files..................')
    files.sort()

    filtered_files = []
    for file in files:
        day = int(file.split('_day-')[1].split('_')[0])
        if day in days['day'].values:
            filtered_files.append(file)

    aud_thresholds = []
    vis_thresholds = []
    for file in filtered_files:
        grab_aud_threshold = False
        grab_vis_threshold = False
        with open(file, 'r') as file:
            for line in file:
                # If the line contains 'aud reverals', activate the flag to grab the next 'threshold'
                if 'aud reverals' in line:
                    grab_aud_threshold = True
                # If the line contains 'vis reverals', activate the flag to grab the next 'threshold'
                elif 'vis reverals' in line:
                    grab_vis_threshold = True
                # If the line contains 'threshold', grab the value and reset the flag
                elif 'threshold:' in line:
                    value = float(line.split(':')[1].strip())  # Get value after ':'
                    # Assign threshold to respective variable based on the flag
                    if grab_aud_threshold:
                        aud_thresholds.append(value)
                        grab_aud_threshold = False
                    elif grab_vis_threshold:
                        vis_thresholds.append(value)
                        grab_vis_threshold = False
                    

    data = {'aud_thres': aud_thresholds, 'vis_thres': vis_thresholds}
    return pd.DataFrame(data)


# Organize the files to read
pattern   = f'*nback_run-1_pres-summary.txt'
one = get_thresholds (pattern)

pattern   = f'*nback_run-2_pres-summary.txt'
two = get_thresholds (pattern)

session_numbers = np.repeat(range(1, 31), 4)  # Repeats each number in 1-30, 4 times
one['session'] = session_numbers[:len(one)]
two['session'] = session_numbers[:len(two)]

one['rank'] = one.groupby('session').cumcount()
two['rank'] = two.groupby('session').cumcount()

# Merge on both 'session' and 'rank'
merged = pd.merge(
    one.rename(columns={'aud_thres': 'one_aud', 'vis_thres': 'one_vis'}),
    two.rename(columns={'aud_thres': 'two_aud', 'vis_thres': 'two_vis'}),
    on=['session', 'rank'],
    how='outer'  # adjust as needed
).drop(columns='rank')

merged.to_excel(f'{savepath}/sub-01_day-scandays_device-presentation_thresholds.xlsx', header=True, index=False)