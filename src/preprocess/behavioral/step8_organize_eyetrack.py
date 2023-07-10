"""
This script will copy the files from the archive folder to the BIDS folder

@author: trianaa1
"""

import os, glob, sys
import shutil
import pandas as pd

path = '/m/cs/archive/networks-pm/mri'
savepath = '/m/cs/project/networks-pm/mri/fast_prepro_bids'

#search all eye-tracker files
search_str = os.path.join(path, '**', '*.asc')
files = glob.glob(search_str, recursive=True)

guide = pd.read_csv(f'{savepath}/participants.tsv', sep='\t')
guide['session'] = guide['session'].str.replace('-', '')
for file in files:
    parts = file.split('/')
    date = parts[-2] 
    day_number = parts[-1].split('_')[1].split('-')[1]
    
    subject = guide.loc[guide['session'] == date, 'participant_id']
    subject = subject.iloc[0]
    
    file_parts = file.rsplit('_', 2)
    
    destination = f'{savepath}/{subject}/func/{subject}_{file_parts[1]}_{file_parts[2]}'
    shutil.copy2(file, destination)
    
    print(file)