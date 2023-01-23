"""
This script creates the needed files in a folder to make it BIDS-complaint.

Requirements: 
            - Folder with NIFTI and JSON files in pseudo-BIDS format.  
            - known sequence of images taken in the scanner. There are 2 fields that are needed, 
              sequences: this refers to the type of sequences. For now, only 'T1', 'EPI', 'localizer' 
              are accepted.
              tasks: this refers to the names that will be used in the BIDS format. For example, 'localizer',
              'MPRAGE_T1w', 'resting', etc. These names can be anything, but make sure it includes all the
              names that have been used in the DICOM2NIFTI step. 

Outputs: - several JSON and tsv files. 

@author: ana.trianahoyos@aalto.fi
Created: 16.02.2021
"""

################################## User input needed ##########################
# Please modify this part 
savepath = '/m/cs/project/networks-pm/mri/fast_prepro_bids'
dcm2niix_path = '/m/cs/scratch/networks-pm/software/dcm2niix/build/bin/dcm2niix'
subject = 'sub-01'
session = '2023-01-16'

#This mapping is needed to change the names of the EPI files in case there are different tasks in a session
tasks = {'1': 'pvt', '2':'resting', '3':'movie', '4':'nback'}

###############################################################################

import os
import json
import pandas as pd
import warnings

#Create other needed files for BIDS
print("Converting to BIDS format...")
file = os.path.join(savepath,f'dataset_description.json')
if not os.path.isfile(file):
    content = {"BIDSVersion": "1.0.0",
               "License": "Apache 2.0",
               "Name": "precision_mapping",
               "ReferencesAndLinks": ["osf.io/5hu9c"]}
    with open(file,'w') as f:
        json.dump(content,f, indent=4)

file = os.path.join(savepath,f'participants.json')
if not os.path.isfile(file):
    content = {"participant_id": {"Description": "Participant identifier"},
               "session": {"Description": "date"}}
    with open(file,'w') as f:
        json.dump(content,f, indent=4)

file = os.path.join(savepath,f'participants.tsv')
if not os.path.isfile(file):
    content = {'participant_id': [subject], 'session': [session]}
    data = pd.DataFrame.from_dict(content)
    data.to_csv(file, sep = '\t', index=False)
else:
    data = pd.read_csv(file, sep = '\t')
    if data['participant_id'].str.contains(subject).any():
        warnings.warn("Warning the subject already exists! No subjects are added.")
    elif set(data.columns)==set(['participant_id', 'session']):
        data = data.append({'participant_id': subject, 'session': session}, ignore_index=True)
        data.to_csv(file, sep = '\t', index=False)
    else:
        warnings.warn("Warning the tsv files has other fields. No modification will be made, please remember to add the info later.")

file = os.path.join(savepath,f'README')
if not os.path.isfile(file):
    with open(file, "w") as f:
        f.write("this dataset contains the data collected for the paper Effects of daily environmental, physiological, and lifestyle factors on functional brain connectivity by Triana et al. (2023)")

file = os.path.join(savepath,f'.bidsignore')
if not os.path.isfile(file):
    with open(file, "w") as f:
        f.write(" ")

for i in tasks:
    if tasks[i]=='localizer' or tasks[i]=='_T1w':
        continue
    elif not os.path.isfile(os.path.join(savepath,f'task-{tasks[i]}_bold.json')):
        content = {"TaskName": f'{tasks[i]}'}
        with open(os.path.join(savepath,f'task-{tasks[i]}_bold.json'),'w') as f:
            json.dump(content,f)

print("BIDS format done! Please validate your folder.")
