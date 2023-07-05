'''Preprocess nback scores. Reads all available logs from the nback task and  
    computes the scores (median RT, number of correct, wrong, and missing answers) 
    
    The input should be done in the following order: 
        - folder path where the files are
        - savefile where the proprocessed data will be stored in csv format

    Parameters
    ----------
    path : str
        path where the raw data is stored 
    savefile : str
        path and name of the save file where the preprocessed data will be stored
        

    
Salmela, V., Salo, E., Salmi, J., and Alho, K. (2018). Spatiotemporal Dynamics 
of Attention Networks Revealed by Representational Similarity Analysis of EEG 
and fMRI. Cereb. Cortex 28, 549–560. 10.1093/cercor/bhw389.

There are three types of resposnes: 
- Missing: the subject has not pressed any buttons. It is readable from the column 
        response as 0
- Right: the subject has identified both, the task and the change, correctly. It 
        is readable from the column change correct as 1
- Wrong: the subject has not identified the task or the change correcly. It is 
        readable from the column change correct as 5 or 0
'''

import os
import sys
import re
import pandas as pd
from datetime import datetime,timedelta

path = sys.argv[1]
savefile = sys.argv[2]
os.chdir(path)

#Find all relevant files
twoback = []
for file in os.listdir(path):
    if file.endswith("nback_run-2_pres.txt"):
        twoback.append(file)
twoback.sort()

oneback = []
for file in os.listdir(path):
    if file.endswith("nback_run-1_pres.txt"):
        oneback.append(file)
oneback.sort()

max_day = int(re.search('day-(\d+)', oneback[-1]).group(1))
start = datetime(2023,1,1) #set the first day of the experiment

#Compute the values for 1-back
median_RT = [None]*max_day
mean_RT = [None]*max_day
right = [None]*max_day
wrong = [None]*max_day
miss = [None]*max_day

day_idx = [None]*max_day

for file in oneback:
    print(f'Preprocessing {file}')
    df = pd.read_csv(file, delimiter="\t", header=4) #Read the data
    df.dropna(inplace=True) #Drop all info that is not numbers
    df.reset_index(inplace=True)
    df = df.astype(float)
    df.rename(columns={"level_0":"Block", "level_1":"trial", "Block ":"pitch", 
                       " trial ":"pit_change", " pitch ":"orientation", 
                       " pit_change ":"or_change", " orientation ":"vis_novel", 
                       " or_change ":"aud_novel", " vis_novel ":"whichtask", 
                       " aud_novel ":"response", " whichtask ":"reaction_time", 
                       " response ":"task_correct", " reaction_time ":"change_correct", 
                       " task_correct ":"no"," change_correct ":"number", 
                       " whichtask .1":"which_task"},inplace=True)
    df = df[df['trial'] > 1]
    
    #set the index in dates
    match = re.search(r"day-(\d+)", file)
    day_of_year = int(match.group(1))
    date = start + timedelta(days=day_of_year - 1)
    
    #set the index in the array
    idx = int(file[file.find('sub-01_day-')+len('sub-01_day-'):file.rfind('_task')])-1 
    
    #Start computing the values
    df.reaction_time[df.reaction_time < 0] = 0
    median_RT[idx] = df['reaction_time'].quantile(0.5)
    mean_RT[idx] = df['reaction_time'].mean()
    right[idx] = df.loc[df['change_correct'] == 1, 'change_correct'].sum()
    miss[idx] = df.loc[df['response'] == 0, 'response'].count()
    wrong[idx] = len(df) - right[idx] -miss[idx]
    day_idx[idx] = date.strftime('%d-%m-%Y')

one_results = {"median_RT_1": median_RT, "mean_RT_1":mean_RT, "right_1": right, 
               "wrong_1":wrong, "miss_1": miss, "date":day_idx}

#Compute the values for 2-back
median_RT = [None]*max_day
mean_RT = [None]*max_day
right = [None]*max_day
wrong = [None]*max_day
miss = [None]*max_day

day_idx = [None]*max_day

for file in twoback:
    print(f'Preprocessing {file}')
    
    df = pd.read_csv(file, delimiter="\t", header=4) #Read the data
    df.dropna(inplace=True) #Drop all info that is not numbers
    df.reset_index(inplace=True)
    df = df.astype(float)
    df.rename(columns={"level_0":"Block", "level_1":"trial", "Block ":"pitch", 
                       " trial ":"pit_change", " pitch ":"orientation", 
                       " pit_change ":"or_change", " orientation ":"vis_novel", 
                       " or_change ":"aud_novel", " vis_novel ":"whichtask", 
                       " aud_novel ":"response", " whichtask ":"reaction_time", 
                       " response ":"task_correct", " reaction_time ":"change_correct", 
                       " task_correct ":"no"," change_correct ":"number", 
                       " whichtask .1":"which_task"},inplace=True)
    df = df[df['trial'] > 2]
    
    #set the index in dates
    match = re.search(r"day-(\d+)", file)
    day_of_year = int(match.group(1))
    date = start + timedelta(days=day_of_year - 1)
    
    #set the index in the array
    idx = int(file[file.find('sub-01_day-')+len('sub-01_day-'):file.rfind('_task')])-1 
    
    #Start computing the values
    df.reaction_time[df.reaction_time < 0] = 0
    median_RT[idx] = df['reaction_time'].quantile(0.5)
    mean_RT[idx] = df['reaction_time'].mean()
    right[idx] = df.loc[df['change_correct'] == 1, 'change_correct'].sum()
    miss[idx] = df.loc[df['response'] == 0, 'response'].count()
    wrong[idx] = len(df) - right[idx] -miss[idx]
    day_idx[idx] = date.strftime('%d-%m-%Y')

two_results = {"median_RT_2": median_RT, "mean_RT_2":mean_RT, "right_2": right, 
               "wrong_2":wrong, "miss_2": miss, "date":day_idx}


nback_results = {**one_results,**two_results}
nback_results = pd.DataFrame.from_dict(nback_results)

#fill in the dates
nback_results['date'] = pd.to_datetime(nback_results['date'], format='%d-%m-%Y')
nback_results['date_filled'] = nback_results['date'].ffill()
s = nback_results['date_filled'].diff().dt.days.shift(-1).fillna(1).astype(int)
date_ranges = [pd.date_range(start, periods=period) for start, period in zip(nback_results['date_filled'], s)]
nback_results['date'] = [date for sublist in date_ranges for date in sublist]
nback_results['date'] = nback_results['date'].dt.strftime('%d-%m-%Y')
nback_results.drop(columns=['date_filled'], inplace=True)
nback_results.set_index("date", inplace=True)

nback_results.to_csv(savefile)