'''Preprocess PVT scores. Reads all available logs from the PVT and computes 
    the scores according to (Basner & Dinges, 2011). 
    
    The input should be done in the following order: 
        - folder path where the files are
        - savefile where the proprocessed data will be stored in csv format

    Parameters
    ----------
    path : str
        path where the raw data is stored 
    savefile : str
        path and name of the save file where the preprocessed data will be stored
        

    
Mathias Basner, MD, PhD, MSc, David F. Dinges, PhD, 
Maximizing Sensitivity of the Psychomotor Vigilance Test (PVT) to Sleep Loss, 
Sleep, Volume 34, Issue 5, 1 May 2011, Pages 581–591, 
https://doi.org/10.1093/sleep/34.5.581 

'''

import os
import sys
import re
import numpy as np
import pandas as pd
from datetime import datetime,timedelta

from glob import glob

path = sys.argv[1]
savefile = sys.argv[2]
os.chdir(path)

files = []
pattern   = f'*-pvt_log.txt'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'preprocessing {str(len(files))} files..................')
files.sort()

max_day = max(int(re.search('day-(\d+)', file).group(1)) for file in files)
start = datetime(2023,1,1) #set the first day of the experiment

median = [None]*max_day
mean = [None]*max_day
mean_1_RT = [None]*max_day
no_lapse_false = [None]*max_day
fast_rt = [None]*max_day
slow_rt = [None]*max_day
fast_1_RT = [None]*max_day
slow_1_RT = [None]*max_day
lapse_prob = [None]*max_day
performance = [None]*max_day

day_idx = [None]*max_day


for file in files:    
    pvt = pd.read_csv(file, sep="\t", header=[0])
    
    #index in the array for saving
    idx = int(file[file.find('sub-01_day-')+len('sub-01_day-'):file.rfind('_task')])-1 
    
    #set the index in dates
    match = re.search(r"day-(\d+)", file)
    day_of_year = int(match.group(1))
    date = start + timedelta(days=day_of_year - 1)
    
    pvt['1_RT'] = 1000/pvt.RT
    
    no_false = len(pvt[pvt['Category']=='false']) + len(pvt[abs(pvt['RT'])<=100])
    no_lapse = len(pvt[pvt['RT']>500])
    no_lapse_false[idx] = no_false + no_lapse
    performance[idx] = 1-(no_lapse_false[idx]/len(pvt))
    lapse_prob[idx] = no_lapse/(len(pvt))
    
    #delete the false starts because their reaction time is negative
    pvt.drop(pvt[pvt.Category=="false"].index, inplace=True) 
    
    median[idx] = pvt.RT.quantile(0.5)
    mean[idx] = pvt.RT.mean()
    fast_rt[idx] = pvt.RT.quantile(0.1)
    slow_rt[idx] = pvt.RT.quantile(0.9)
    mean_1_RT[idx] = pvt["1_RT"].mean()
    slow_1_RT[idx] = pvt["1_RT"].quantile(0.9)
    fast_1_RT[idx] = pvt["1_RT"].quantile(0.1)
    day_idx[idx] = date.strftime('%d-%m-%Y')
    print(file)

pvt_results = {"mean_1_RT": mean_1_RT, "median": median, "mean":mean,
               "fast10_RT": fast_rt, "slow10_RT":slow_rt, "fast10_1_RT": fast_1_RT,
               "slow10_1_RT": slow_1_RT, "no_lapse_false": no_lapse_false, 
               "lapse_prob": lapse_prob, "performance": performance, "date": day_idx}

pvt_results = pd.DataFrame.from_dict(pvt_results)

#fill in the dates
pvt_results['date'] = pd.to_datetime(pvt_results['date'], format='%d-%m-%Y')
pvt_results['date_filled'] = pvt_results['date'].ffill()
s = pvt_results['date_filled'].diff().dt.days.shift(-1).fillna(1).astype(int)
date_ranges = [pd.date_range(start, periods=period) for start, period in zip(pvt_results['date_filled'], s)]
pvt_results['date'] = [date for sublist in date_ranges for date in sublist]
pvt_results['date'] = pvt_results['date'].dt.strftime('%d-%m-%Y')
pvt_results.drop(columns=['date_filled'], inplace=True)
pvt_results.set_index("date", inplace=True)

#save the results
pvt_results.to_csv(savefile)