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

from glob import glob

variable = sys.argv[1]
path = sys.argv[2]

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
data = data.sort_index()

start_date = data.index[0]
end_date = data.index[-1]
all_points = pd.date_range(start=start_date, end=end_date, freq='S')
all_points = all_points.to_frame()
all_points["data"] = np.nan
all_points.rename(columns={0:"date"}, inplace=True)

df = all_points.set_index('date').join(data, lsuffix="_a")
df.drop(columns=["data_a"],inplace=True)
df[df["data"]>0] = 0
df.fillna(1, inplace=True)

percentage = df.resample('1D').sum()
percentage["data"] = (percentage["data"]/86400)*100

print(f'data loss in percentage for {variable}...............')
print(percentage)