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
files = sorted(files)

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

#the eye tracker failed during several sessions and we have recorded these failures,
#so let's set to nan that session as the data cannot be trusted
microsleep.loc[(microsleep['subject'] == 'sub-09') & (microsleep['task'] == 'nback'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-09') & (microsleep['task'] == 'movie'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-26') & (microsleep['task'] == 'nback'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-11') & (microsleep['task'] == 'nback'), 'sleep_percentage'] = np.nan

#on top, there are other datapoints that are dubious and should not be trusted. 
#this is based on the data quality analyses. So, let's set those to nan as well.
microsleep.loc[(microsleep['subject'] == 'sub-21') & (microsleep['task'] == 'nback'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-21') & (microsleep['task'] == 'movie'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-09') & (microsleep['task'] == 'resting'), 'sleep_percentage'] = np.nan
microsleep.loc[(microsleep['subject'] == 'sub-03') & (microsleep['task'] == 'resting'), 'sleep_percentage'] = np.nan
    
#now separate based on the tasks and save the info
microsleep = microsleep.pivot(index='subject', columns='task', values='sleep_percentage')
microsleep = microsleep[['pvt', 'resting', 'movie', 'nback']]

#input the missing data 
#microsleep = microsleep.fillna((microsleep.mean()))

#and save the data
microsleep.to_csv(f'{save_dir}/sub-01_day-all_device-eyetracker.csv')
