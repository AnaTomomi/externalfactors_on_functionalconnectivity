"""Preprocess empatica data. Reads all empatica data splitted in sessions, 
    organizes, and saves them in the given savepath.
    
    The input should be done in the following order:

    Parameters
    ----------
    variable : str
        name of the variable to preprocess. It could be heart rate (hr), 
        temperature (temperature), electrodermal activity (electrodermal)
    path : str
        path where the raw data is stored
    savefile : str
        
    """
    
import os
import sys
import datetime as dt
import pandas as pd

from glob import glob
from fnmatch import fnmatch

path = sys.argv[1]
savefile = sys.argv[2]

files = []
pattern   = f'*device-wristband_*_preproc.csv'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'aggregating data for {str(len(files))} files..................')

variables = []
for file in files:
    left = 'device-wristband_'
    right = '_preproc.csv'
    variables.append(file[file.index(left)+len(left):file.index(right)])
variables = list(set(variables))

final = []
for variable in variables:
    print(f'processing {variable}')
    df=[]
    for file in files:
        if variable in file:
            data = pd.read_csv(file, index_col="time")
            data["date"] = pd.to_datetime(data.index)
            data.set_index("date", inplace=True)
    
            df.append(data)

    data = pd.concat(df)
    data = data.sort_index()

    if variable=="interbeatinterval":
        temp = data.resample('5min').std()
        temp.dropna(inplace=True)
        temp = temp.resample('1D').mean()
        temp.rename(columns={"data":f'hrv_mean_sdrr'}, inplace=True)
        final.append(temp)
        temp = data.resample('1D').std()
        temp.rename(columns={"data":f'hrv_sdrr'}, inplace=True)
        final.append(temp)
        temp = data.resample('1D').mean()
        temp.rename(columns={"data":f'hrv_mean'}, inplace=True)
        final.append(temp)
        temp = data.copy()
        temp["in"] = temp.diff()
        temp["in"] = temp["in"]**2
        temp = (temp["in"].resample('1D').mean())**(1/2)
        temp = temp.to_frame(name="hrv_RMSRR")
        final.append(temp)
    else:
        temp = data.resample('1D').mean()
        temp.rename(columns={"data":f'{variable}_mean'}, inplace=True)
        final.append(temp)
        temp = data.resample('1D').median()
        temp.rename(columns={"data":f'{variable}_median'}, inplace=True)
        final.append(temp)
        temp = data.resample('1D').std()
        temp.rename(columns={"data":f'{variable}_std'}, inplace=True)
        final.append(temp)    
        temp = data.resample('1D').min()
        temp.rename(columns={"data":f'{variable}_min'}, inplace=True)
        final.append(temp)    
        temp = data.resample('1D').max()
        temp.rename(columns={"data":f'{variable}_max'}, inplace=True)
        final.append(temp)

data = pd.concat(final, axis=1)
data.to_csv(savefile)