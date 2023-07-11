"""
This script reads the .asc eyetracker files in a folder and extracts information
about the fixation, saccade, and blinks for each file, following the guidelines in:
https://risoms.github.io/mdl/docs/build/manual/EyeLink%201000%20Plus%20User%20Manual%201.0.12.pdf

The script returns a dataframe with the information.

Inputs: path 

Outputs: csv file saved in the same input path

@author: trianaa1 based on the parse_eyetrack by @merzonl1
"""

import os, glob, sys
import pandas as pd
import re

import warnings
warnings.filterwarnings("ignore")

fix_str = re.compile(r'EFIX(.*)')
blink_str = re.compile(r'EBLINK(.*)')
sac_str = re.compile(r'ESACC(.*)')
message_str = re.compile(r'MSG(.*)')

root_dir = sys.argv[1]
search_str = os.path.join(root_dir, '**', 'func', '*.asc')
files = glob.glob(search_str, recursive=True)

for file in files:
    file_parts = file.rsplit('_', 2)
    sb = re.search('sub-\d+', file)
    task = re.search('task-(.*)_device', file)
    sb = sb.group()
    task = task.group(1)
    
    #Determine the tags of the tasks
    if task == 'pvt':
        tag = 'SYNCTIME'
    elif task == 'resting':
        tag = 'rest'
    elif task == 'movie':
        tag = 'movie'
    elif task == 'nback':
        tag = 'back'
     
    flag = False
    event = None
    df = pd.DataFrame(columns=['SUBJECT', 'TASK', 'EVENT', 'START_TIME', 'END_TIME', 'BLINK_DURATION', 'FIX_DURATION', 'SAC_DURATION', 'FIX_X', 'FIX_Y', 'SAC_START_X', 'SAC_START_Y', 'SAC_END_X', 'SAC_END_Y', 'SAC_AMPLITUDE', 'SAC_PEAK_VELOCITY', 'PUPIL_SIZE'])

    with open(file) as log:
        for index, line in enumerate(log):
            line = line.strip()
            
            if message_str.match(line):
                event = 'message'
                mes = line.replace('\t', ' ').split()
                if tag in mes[2]:
                    flag =True #If the message is detected, it means the stimulus begun, 
                    #so we need to start preprocessing from this point onwards.
                else:
                    flag =False #if message, but not matching, then set to false
            
            #fixation
            if fix_str.match(line) and flag:
                event = 'fix'
                fix_dt = line.replace('\t', ' ').split()
                st_time = fix_dt[2]
                end_time = fix_dt[3]
                dur = fix_dt[4]
                x = fix_dt[5]
                y = fix_dt[6]
                pupil = fix_dt[7]  
                df = df.append({'SUBJECT': sb, 'TASK': task, 'EVENT': event,'START_TIME': st_time, 'END_TIME': end_time,
                                'FIX_DURATION': dur, 'FIX_X': x, 'FIX_Y': y, 'PUPIL_SIZE':pupil}, ignore_index=True)
            # saccade
            elif sac_str.match(line) and flag and event!='blink': #do not include saccade if following a blink
                event = 'saccade'
                sc_dt = line.replace('\t', ' ').split()
                st_time = sc_dt[2]
                end_time = sc_dt[3]
                dur = sc_dt[4]
                st_x = sc_dt[5]
                st_y = sc_dt[6]
                end_x = sc_dt[7]
                end_y = sc_dt[8]
                amp = sc_dt[9]
                pv = sc_dt[10]

                df = df.append({'SUBJECT': sb, 'TASK': task, 'EVENT': event, 'START_TIME': st_time, 'END_TIME': end_time,
                                'SAC_DURATION': dur, 'SAC_START_X': st_x, 'SAC_START_Y': st_y, 'SAC_END_X': end_x, 
                                'SAC_END_Y': end_y, 'SAC_AMPLITUDE': amp, 'SAC_PEAK_VELOCITY': pv}, ignore_index=True)

            # blink
            elif blink_str.match(line) and flag:
                event = 'blink'
                time = line.replace('\t', ' ').split()
                st_time = time[2]
                end_time = time[3]
                dur = time[4]
                df = df.append({'SUBJECT': sb, 'TASK': task, 'EVENT': event, 'START_TIME': st_time, 'END_TIME': end_time,
                                'BLINK_DURATION': dur}, ignore_index=True)
        
        log.close()
        
        df.to_csv(f'{root_dir}/{sb}/func/{sb}_task-{task}_device-eyetrack.csv')
        print (f'{root_dir}/{sb}/func/{sb}_task-{task}_device-eyetrack.csv')
        del df