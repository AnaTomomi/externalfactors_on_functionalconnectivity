"""Computes the number of missing datapoints 

    Parameters
    ----------
    file : str
        path where the raw data is stored
        
    """
    
import os
import sys
import datetime as dt
import pandas as pd

file = sys.argv[2]

data = pd.read_csv(file, index_col="date")
data["date"] = pd.to_datetime(data.index)
data.set_index("date", inplace=True)

start_date = data.index[0]
end_date = data.index[-1]
all_points = pd.date_range(start=start_date, end=end_date, freq='1D')
all_points = all_points.to_frame()
all_points["data"] = np.nan
all_points.rename(columns={0:"date"}, inplace=True)

df = all_points.set_index('date').join(data)
df.drop(columns=["data"],inplace=True)
df[df["Activity Score"]>0] = 0
df = df["Activity Score"].to_frame()
df.fillna(1, inplace=True)

percentage = df.sum()
percentage = (percentage/133)*100

print(f'data loss in percentage for oura...............')
print(percentage.values)