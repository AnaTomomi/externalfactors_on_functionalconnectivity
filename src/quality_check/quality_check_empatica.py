"""Computes the number of missing datapoints 

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
import numpy as np

from glob import glob

path = sys.argv[1]

files = []
pattern   = f'*device-wristband_*preproc.csv'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'checking data quality for {str(len(files))} files..................')

variables = []
for file in files:
    left = 'device-wristband_'
    right = '_preproc.csv'
    variables.append(file[file.index(left)+len(left):file.index(right)])
variables = list(set(variables))
print(f'checking data quality for {str(len(variables))} variables..................')

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
        data = data.resample('5min').std()
        freq = '300S' #5mins
        num = len(data)
    elif variable=="hr":
        freq='S'
        num=86400
    else:
        freq='0.25S' #4Hz sampling
        num=86400*4 #4times in a second, for all the seconds in a day
        
    start_date = data.index[0]
    end_date = data.index[-1]
    all_points = pd.date_range(start=start_date, end=end_date, freq=freq)
    all_points = all_points.to_frame()
    all_points["data"] = np.nan
    all_points.rename(columns={0:"date"}, inplace=True)

    df = all_points.set_index('date').join(data, lsuffix="_a")
    df.drop(columns=["data_a"],inplace=True)
    df[df["data"]>0] = 0
    df.fillna(1, inplace=True)

    percentage = df.resample('1D').sum()
    percentage["data"] = (percentage["data"]/num)*100

    print(f'data loss in percentage for {variable}...............')
    print(percentage)
    
    