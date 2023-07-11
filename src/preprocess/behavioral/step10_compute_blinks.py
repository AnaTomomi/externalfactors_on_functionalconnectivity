"""
This script reads computes the percentage of time the eyes were closed during 
the MRI sessions. Closure of the eyes is determined by the blink state and only
microsleeps (i.e. eye closure longer than 10s) are counted. 

The script returns a dataframe per task with the sleep percentage.

Inputs: path 

Outputs: csv file saved in the output path

@author: trianaa1
"""

import os, glob, sys
import pandas as pd
import numpy as np
import re

import warnings
warnings.filterwarnings("ignore")

root_dir = sys.argv[1]
save_dir = sys.argv[2]

search_str = os.path.join(root_dir, '**', 'func', '*eyetrack.csv')
files = glob.glob(search_str, recursive=True)

microsleep = pd.DataFrame(columns=['subject', 'task', 'sleep_percentage'])

for file in files:
    print(file)
    sub = re.search('sub-\d+', file)
    task = re.search('task-(.*)_device', file)
    sub = sub.group()
    task = task.group(1)
    
    df = pd.read_csv(file, index_col=0)
    if not df.empty:
        total_time = df.loc[df.index[-1],'END_TIME'] - df.loc[0,'START_TIME']
       
        #let's take only the blink events that are over 10seconds, defined as microsleep
        df = df[df['EVENT']=='blink'] 
        sleep = df[df["BLINK_DURATION"]>10000]
        sleep_percentage = sleep['BLINK_DURATION'].sum()/total_time
    else:
        sleep_percentage = np.nan
    
    microsleep = microsleep.append({'subject': sub, 'task': task, 'sleep_percentage': sleep_percentage}, ignore_index=True)

#the eye tracker failed during sub-09 session, so let's set to nan that session as the data cannot be trusted
microsleep.loc[(microsleep['subject'] == 'sub-09') & (microsleep['task'] == 'nback'), 'sleep_percentage'] = np.nan
    
#now separate based on the tasks and save the info
pvt = microsleep[microsleep['task']=='pvt']
resting = microsleep[microsleep['task']=='resting']
movie = microsleep[microsleep['task']=='movie']
nback = microsleep[microsleep['task']=='nback']

#and save the data
pvt.to_csv(f'{save_dir}/sub-01_day-all_task-pvt_device-eyetracker.csv')
resting.to_csv(f'{save_dir}/sub-01_day-all_task-resting_device-eyetracker.csv')
movie.to_csv(f'{save_dir}/sub-01_day-all_task-movie_device-eyetracker.csv')
nback.to_csv(f'{save_dir}/sub-01_day-all_task-nback_device-eyetracker.csv')
