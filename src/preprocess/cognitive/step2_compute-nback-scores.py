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
'''

import os
import sys
import numpy as np
import pandas as pd

from glob import glob

path = sys.argv[1]
savefile = sys.argv[2]
os.chdir(path)


def get_dual_data(stim2back):
    count=1
    for key in stim2back["DD1"]:
        print(key)
        stat = stim2back["DD1"][key].groupby([" change_correct "]).size().to_frame().T
        if count==1:
            stats = stat
        else:
            stats = pd.concat([stats,stat])
        count = count+1
    stats = stats.rename(columns={"0": "wrong", "1": "correct", "5":"missing"})
    stats = stats.reset_index()
    stats = stats.drop(columns=["index"])
    stats["days"] = range(1,len(stats)+1)
    return stats

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

#Organize the data in dictionaries
table_names = ["DD1"]
days2back = dict()
for file in twoback:
    day = int(file[file.find('sub-01_day-')+len('sub-01_day-'):file.rfind('_task')])
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        if k<4:
            df = df.iloc[1:-3]
        else:
            df = df.iloc[1:]
        tables[f'{g.iloc[0,1]}_{k}'] = df
        tables.pop("nan_0",None)
    days2back[day] = tables
    print(file)

days1back = dict()
for file in oneback:
    day = int(file[file.find('sub-01_day-')+len('sub-01_day-'):file.rfind('_task')])
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        if k<4:
            df = df.iloc[1:-3]
        else:
            df = df.iloc[1:]
        tables[f'{g.iloc[0,1]}_{k}'] = df
        tables.pop("nan_0",None)
    days1back[day] = tables
    print(file)

