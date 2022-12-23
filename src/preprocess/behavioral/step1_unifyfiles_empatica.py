"""Preprocess empatica data. Reads all empatica data splitted in sessions, 
    organizes, and saves them in the given savepath.
    
    The input should be done in the following order:

    Parameters
    ----------
    variable : str
        name of the variable to preprocess. It could be heart rate (hr), 
        temperature (temperature), electrodermal activity (electrodermal), and interbeatinterval
    day : str
        day number to be preprocessed. It should be given in three digit numbers (e.g. 003)
    path : str
        path where the raw data is stored
    """
    
import os
import sys
import datetime as dt
import pandas as pd

variable = sys.argv[1]
path = sys.argv[2]

day = path[path.find('day-')+len('day-'):path.rfind('/')]

files = []
for file in os.listdir(path):
    if file.endswith(variable+'.csv'):
        files.append(file)

df = []
for file in files:
    data = pd.read_csv(f'{path}/{file}', header=None)
    start_time = data.iloc[0,0]
    
    if variable=='interbeatinterval':
        data.rename(columns={0:'time', 1:'data'}, inplace=True)
        data["time"] = data["time"] + start_time
        data = data.iloc[1:]
        data["time"] = pd.to_datetime(data['time'], unit='s')
        data.set_index("time", inplace=True)   
        
    else:
        sample_rate = 1/data.iloc[1,0]
        data = data.iloc[2:]
    
        start_time = dt.datetime.fromtimestamp(start_time)
        freq=f'{str(sample_rate)}S'    
        data["time"] = pd.date_range(start=start_time, periods=len(data),freq=freq)
        data.set_index("time", inplace=True)
        data.rename(columns={0:'data'}, inplace=True)
        
    df.append(data)
    
data = pd.concat(df)
data = data.sort_index()
data.to_csv(f'{path}/sub-01_day-{day}_device-wristband_{variable}_preproc.csv')