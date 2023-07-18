"""
Created on Mon Jul 17 13:14:11 2023

@author: trianaa1
"""
import os, glob
import pandas as pd

path = "/m/cs/project/networks-pm/behavioral"
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral"

files = []
pattern   = f'*device-smartphone*'

for dir,_,_ in os.walk(path):
    files.extend(glob.glob(os.path.join(dir,pattern))) 
print(f'checking data quality for {str(len(files))} files..................')

for file in files:
    df = pd.read_csv(file)
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert('Europe/Helsinki')
    if "ESM" in file:
        df['date'] = df['date'].dt.date
        df = df[df['id'].isin(['am_01', 'dq_01', 'pm_01'])]
        df = df.dropna(subset=['answer'])
        df = df.groupby(['date', 'id']).size().reset_index(name='count')
        df = pd.pivot_table(df, values="count", index=["date"], columns="id")
        df.rename(columns={"am_01":"morning", "dq_01":"daily", "pm_01":"evening"}, inplace=True)
        df.fillna(0, inplace=True)
        df["daily"] = df["daily"]/3
        df.index = pd.to_datetime(df.index)
        df.index = df.index.strftime('%d-%m-%Y')
        df.to_csv(f'{savepath}/sub-01_day-all_device-smartphone_sensor-ema_quality.csv')
    if "Battery" in file:
        df.set_index('date', inplace=True)
        df = df["battery_level"].resample('10T').mean()
        df = df.resample('1D').count()
        df = df/144
        df.index = df.index.strftime('%d-%m-%Y')
        df.to_csv(f'{savepath}/sub-01_day-all_device-smartphone_sensor-battery_quality.csv')
