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

variable = sys.argv[1]
path = sys.argv[2]
savefile = sys.argv[3]

files = []
pattern   = f'*_{variable}_preproc.csv'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 

df=[]
for file in files:
    data = pd.read_csv(file, index_col="time")
    data["date"] = pd.to_datetime(data.index)
    data.set_index("date", inplace=True)
    
    df.append(data)

data = pd.concat(df)
data.resample('1D').mean()

data.to_csv(savefile)