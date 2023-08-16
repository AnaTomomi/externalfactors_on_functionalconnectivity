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

path = sys.argv[1]
savepath = sys.argv[2]

tr = 0.594
nii_length = 1116

os.chdir(path)
days = pd.read_csv(f'{savepath}/participants.tsv',sep='\t')

# Organize the files to read
files = []
pattern   = f'*pvt_log.log'
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
    
    #check when does the PVT start and end
    for i in range(len(pulse_info) - 1):
        if pulse_info['Trial'].iloc[i] == '4' and pulse_info['Trial'].iloc[i + 1] != '4':
            pvt_start = pulse_info.iloc[i]
    pvt_end = pulse_info[pulse_info['Code'] == 'End screen present'].squeeze(axis=0)
    
    #add the first event which is the washout out cross
    first_row = pd.DataFrame([{'onset': 0, 'duration': pvt_start["Time"]/1000, 'trial_type': 'washout', 'response_time': "n/a"}])
    df = pd.concat([df, first_row], ignore_index=True)

    #add the other rows
    response = pd.read_csv(f'{file[:-3]}txt', sep='\t')
    pulse_info = pulse_info[pulse_info['Event Type']=='Response']
    
    #there are three special cases 
    if len(pulse_info)!=len(response):
        if day=='048' or day=='093':
            #there was a button press after the PVT has ended
            pulse_info = pulse_info.drop(pulse_info.index[-1])
        if day=='072':
            #there were two button presses before the PVT started, and
            #one button was not captured in the .log file maybe becuase it was too quick
            pulse_info = pulse_info.drop(pulse_info.index[0]) 
            pulse_info.loc[2,"Time"] = pvt_start["Time"] + response.loc[0,"Time"]
    
    assert len(pulse_info)==len(response), "number of the responses in the log files do not match"
    
    pulse_info.reset_index(inplace=True)
    full_info = pulse_info.join(response, rsuffix="_pres")
    full_info = full_info[['Time','RT','Category']]
    full_info.rename(columns={"Time":"onset","RT":"duration","Category":"trial_type"}, inplace=True)
    
    full_info['response_time'] = full_info['duration']
    
    # duration must be always positive
    full_info['duration'] = abs(full_info['duration'])
    #the onset is still the time when the button was pressed. Therefore, the onset was before
    #But, only update 'onset' for rows where 'trial_type' is not 'false'
    full_info.loc[full_info['trial_type'] != 'false', 'onset'] = full_info['onset'] - full_info['duration']

    #now everything to seconds
    full_info[['onset','duration','response_time']] = full_info[['onset','duration','response_time']]/1000
    full_info.loc[full_info['trial_type'] == 'false', 'duration'] = 0.1
    
    #concatenate the rows
    df = pd.concat([df, full_info], ignore_index=True)
    
    #last row
    dur = ((nii_length*tr)*1000)-pvt_end["Time"]
    last_row = pd.DataFrame([{'onset': pvt_end["Time"]/1000, 'duration': dur/1000, 'trial_type': 'washout', 'response_time': "n/a"}])
    df = pd.concat([df, last_row], ignore_index=True)
    
    df.to_csv(f'{savepath}/{subject}/func/{subject}_task-pvt_events.tsv', sep='\t', index=False)